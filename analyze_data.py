"""
EPF Data Analysis Program
Extracts keywords, associates files, and builds timelines from document content timestamps
"""

import os
import re
import json
from collections import defaultdict, Counter
from datetime import datetime
from pathlib import Path
import sys

# Configuration - Use relative paths for portability
BASE_DIR = Path(__file__).parent.resolve()
ORIGINAL_FILES_DIR = BASE_DIR / "Original Files"
SUMMARY_KEYWORDS_DIR = BASE_DIR / "Summary and Keywords"
OUTPUT_DIR = BASE_DIR / "data"
OUTPUT_INDEX_FILE = OUTPUT_DIR / "index.json"
MIN_KEYWORD_OCCURRENCES = 25  # Include keywords with 25+ occurrences


def clean_summary(summary):
    """
    Clean summary by removing introductory phrases like 'Here's a summary' or 'Here's a factual summary'
    Only removes the first sentence if it starts with these phrases.
    """
    if not summary:
        return summary
    
    # Split into sentences (simple split by period followed by space or newline)
    sentences = re.split(r'\.\s+', summary, maxsplit=1)
    
    if len(sentences) < 2:
        # Only one sentence or no sentence boundary found
        return summary
    
    first_sentence = sentences[0].strip().lower()
    
    # Check if first sentence starts with the phrases we want to remove
    remove_phrases = [
        "here's a summary",
        "here's a factual summary",
        "here is a summary",
        "here is a factual summary",
        "here’s a factual summary",
        "here’s a summary"
    ]
    
    for phrase in remove_phrases:
        if first_sentence.startswith(phrase):
            # Remove first sentence and return the rest
            return sentences[1].strip()
    
    # If no match, return original
    return summary


def extract_keywords_from_file(filepath):
    """Extract keywords from a keyword file ONLY (not summary files)"""
    keywords = []
    
    # Only process keyword files, not summary files
    if not filepath.name.endswith('_keywords.txt'):
        return keywords
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            # Keywords are typically comma-separated after the header
            lines = content.split('\n')
            for line in lines:
                if line.strip() and not line.startswith('=') and not line.startswith('Keywords') and not line.startswith('Summary'):
                    # Split by comma and clean up
                    parts = [k.strip() for k in line.split(',')]
                    keywords.extend([k for k in parts if k])
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
    return keywords


def extract_timestamps_from_content_text(text):
    """
    Extract timestamps from text content (summary or original file)
    """
    timestamps = []
    
    # Common date patterns to look for in the actual document content
    date_patterns = [
                # Full month name patterns
                r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),?\s+(\d{4})\b',
                r'\b(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December),?\s+(\d{4})\b',
                
                # Abbreviated month patterns
                r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)\.?\s+(\d{1,2}),?\s+(\d{4})\b',
                r'\b(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)\.?,?\s+(\d{4})\b',
                
                # Numeric date patterns (MM/DD/YYYY, MM-DD-YYYY, YYYY-MM-DD)
                r'\b(\d{1,2})[/-](\d{1,2})[/-](\d{4})\b',
                r'\b(\d{4})[/-](\d{1,2})[/-](\d{1,2})\b',
                
                # Date: prefix patterns
                r'Date:\s*(\d{4}-\d{2}-\d{2})',
                r'Date:\s*(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),?\s+(\d{4})',
                r'Date:\s*(\d{1,2})[/-](\d{1,2})[/-](\d{4})',
                
                # Dated patterns
                r'[Dd]ated\s+(?:at\s+)?(?:\w+,?\s+)?(?:\w+\s+)?(?:this\s+)?(\d{1,2})(?:st|nd|rd|th)?\s+day\s+of\s+(January|February|March|April|May|June|July|August|September|October|November|December),?\s+(\d{4})',
    ]
    
    # Try each pattern
    for pattern in date_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            try:
                date_str = match.group(0)
                parsed_date = parse_flexible_date(match.groups())
                if parsed_date:
                    timestamps.append({
                        'raw': date_str,
                        'parsed': parsed_date.isoformat(),
                        'line': date_str  # Just the date itself
                    })
            except Exception as e:
                continue
    
    return timestamps


def extract_timestamps_from_content(filepath):
    """
    Extract actual document timestamps from the original file content
    (NOT the 'Generated:' timestamp)
    """
    timestamps = []
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
            # Skip the "Generated:" line at the top
            lines = content.split('\n')
            
            for i, line in enumerate(lines):
                # Skip first 5 lines to avoid the "Generated:" timestamp
                if i < 5:
                    continue
                
                # Extract from remaining lines
                line_timestamps = extract_timestamps_from_content_text(line)
                timestamps.extend(line_timestamps)
            
    except Exception as e:
        print(f"Error extracting timestamps from {filepath}: {e}")
    
    return timestamps


def parse_flexible_date(groups):
    """Parse various date formats into a datetime object with smart format detection"""
    try:
        # Handle different tuple structures from regex groups
        groups = [g for g in groups if g]  # Remove None values
        
        if not groups:
            return None
        
        # Month name formats
        month_names = ['january', 'february', 'march', 'april', 'may', 'june',
                      'july', 'august', 'september', 'october', 'november', 'december']
        month_abbrev = ['jan', 'feb', 'mar', 'apr', 'may', 'jun',
                       'jul', 'aug', 'sep', 'sept', 'oct', 'nov', 'dec']
        
        # Check if we have text month names (these are unambiguous)
        has_text_month = False
        for g in groups:
            g_lower = str(g).lower().replace('.', '')
            if g_lower in month_names or g_lower in month_abbrev:
                has_text_month = True
                break
        
        # If we have text months, use the old logic
        if has_text_month:
            month = None
            day = None
            year = None
            
            for g in groups:
                g_lower = str(g).lower().replace('.', '')
                
                # Check if it's a month name
                if g_lower in month_names:
                    month = month_names.index(g_lower) + 1
                elif g_lower in month_abbrev:
                    if g_lower == 'sept':
                        month = 9
                    else:
                        month = month_abbrev.index(g_lower) + 1
                # Check if it's a year (4 digits)
                elif len(str(g)) == 4 and str(g).isdigit():
                    year = int(g)
                # Check if it's a day or month (1-2 digits)
                elif str(g).isdigit():
                    num = int(g)
                    if 1 <= num <= 31:
                        if day is None:
                            day = num
                        elif month is None and num <= 12:
                            month = num
            
            # Try to construct date
            if year and month and day:
                if 1900 <= year <= 2030:
                    return datetime(year, month, day)
            elif year and month:
                if 1900 <= year <= 2030:
                    return datetime(year, month, 1)
        
        # For numeric-only dates, use format priority
        # Priority 1: YYYY-MM-DD or YYYY/MM/DD (ISO format)
        # Priority 2: MM/DD/YYYY or MM-DD-YYYY (US format)
        # Priority 3: DD/MM/YYYY or DD-MM-YYYY (EU format)
        
        if len(groups) == 3 and all(str(g).isdigit() for g in groups):
            nums = [int(g) for g in groups]
            
            # Check if first is a 4-digit year (YYYY-MM-DD or YYYY-DD-MM)
            if nums[0] >= 1900 and nums[0] <= 2030:
                year = nums[0]
                # Determine if second is month or day
                # Priority: assume YYYY-MM-DD first
                if 1 <= nums[1] <= 12 and 1 <= nums[2] <= 31:
                    # Could be YYYY-MM-DD
                    try:
                        return datetime(year, nums[1], nums[2])
                    except:
                        pass
                # If that fails, try YYYY-DD-MM
                if 1 <= nums[2] <= 12 and 1 <= nums[1] <= 31:
                    try:
                        return datetime(year, nums[2], nums[1])
                    except:
                        pass
            
            # Check if last is a 4-digit year (MM/DD/YYYY or DD/MM/YYYY)
            elif nums[2] >= 1900 and nums[2] <= 2030:
                year = nums[2]
                # Priority: assume MM/DD/YYYY (US format)
                if 1 <= nums[0] <= 12 and 1 <= nums[1] <= 31:
                    try:
                        return datetime(year, nums[0], nums[1])
                    except:
                        pass
                # If that fails, try DD/MM/YYYY (EU format)
                if 1 <= nums[1] <= 12 and 1 <= nums[0] <= 31:
                    try:
                        return datetime(year, nums[1], nums[0])
                    except:
                        pass
            
    except Exception as e:
        pass
    
    return None


def get_file_id(filename):
    """Extract the EFTA ID from filename"""
    match = re.search(r'EFTA\d+', filename)
    return match.group(0) if match else filename


def process_all_files():
    """Main processing function"""
    print("=" * 80)
    print("EPF DATA ANALYSIS - Starting...")
    print("=" * 80)
    
    # Step 1: Collect all keywords and build file associations
    print("\n[1/4] Extracting keywords from summary and keyword files...")
    keyword_counter = Counter()
    keyword_to_files = defaultdict(set)
    file_to_keywords = defaultdict(list)
    
    summary_keywords_path = Path(SUMMARY_KEYWORDS_DIR)
    all_files = list(summary_keywords_path.glob("*_keywords.txt"))
    
    print(f"Found {len(all_files)} keyword files to process")
    
    for i, filepath in enumerate(all_files, 1):
        if i % 100 == 0:
            print(f"  Processed {i}/{len(all_files)} files...")
        
        file_id = get_file_id(filepath.name)
        keywords = extract_keywords_from_file(filepath)
        
        for keyword in keywords:
            if keyword:  # Skip empty keywords
                keyword_lower = keyword.lower().strip()
                keyword_counter[keyword_lower] += 1
                keyword_to_files[keyword_lower].add(file_id)
                file_to_keywords[file_id].append(keyword_lower)
    
    print(f"  Total unique keywords found: {len(keyword_counter)}")
    print(f"  Total files processed: {len(file_to_keywords)}")
    
    # Step 2: Get keywords with minimum occurrences (filter out redaction-related keywords and years)
    print(f"\n[2/4] Identifying keywords with {MIN_KEYWORD_OCCURRENCES}+ occurrences...")
    
    # Filter out keywords containing "redaction", years (4-digit numbers), or too short keywords
    MIN_KEYWORD_LENGTH = 3  # Minimum 3 characters
    filtered_keywords = []
    for kw, count in keyword_counter.items():
        # Skip if too short (less than 3 characters)
        if len(kw.strip()) < MIN_KEYWORD_LENGTH:
            continue
        # Skip if contains "redaction"
        if 'redaction' in kw.lower():
            continue
        # Skip if it's a 4-digit year (1900-2099)
        if kw.strip().isdigit() and len(kw.strip()) == 4:
            year = int(kw.strip())
            if 1900 <= year <= 2099:
                continue
        # Only include if count >= minimum
        if count >= MIN_KEYWORD_OCCURRENCES:
            filtered_keywords.append((kw, count))
    
    top_keywords = sorted(filtered_keywords, key=lambda x: x[1], reverse=True)
    
    print(f"  Filtered out keywords containing 'redaction', year keywords, and keywords < {MIN_KEYWORD_LENGTH} chars")
    print(f"  Keywords with {MIN_KEYWORD_OCCURRENCES}+ occurrences: {len(top_keywords)}")
    print(f"\nTop 10 Keywords Preview:")
    for keyword, count in top_keywords[:10]:
        print(f"  {keyword}: {count} occurrences")
    
    # Step 3: Extract timestamps from summary files first, then original files
    print(f"\n[3/4] Extracting timestamps from summary and original files...")
    file_timestamps = {}
    file_summaries = {}
    
    summary_keywords_path = Path(SUMMARY_KEYWORDS_DIR)
    original_path = Path(ORIGINAL_FILES_DIR)
    original_files = list(original_path.glob("*.txt"))
    print(f"Found {len(original_files)} original files to process")
    
    for i, filepath in enumerate(original_files, 1):
        if i % 100 == 0:
            print(f"  Processed {i}/{len(original_files)} files...")
        
        file_id = get_file_id(filepath.name)
        
        # First, try to get timestamp from summary file (PRIORITY)
        summary_file = summary_keywords_path / f"{filepath.stem}_summary.txt"
        summary_timestamps = []
        
        if summary_file.exists():
            try:
                with open(summary_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    lines = [l.strip() for l in content.split('\n') if l.strip() and not l.startswith('=') and not l.startswith('Summary')]
                    summary_text = ' '.join(lines)
                    file_summaries[file_id] = summary_text  # Keep full summary
                    
                    # Extract timestamps from summary
                    summary_timestamps = extract_timestamps_from_content_text(summary_text)
            except Exception as e:
                pass
        
        # If summary has timestamps, use those (prioritize first one)
        if summary_timestamps:
            file_timestamps[file_id] = summary_timestamps
        else:
            # Otherwise, extract from original file
            timestamps = extract_timestamps_from_content(filepath)
            if timestamps:
                file_timestamps[file_id] = timestamps
    
    print(f"  Extracted timestamps from {len(file_timestamps)} files")
    
    # Step 4: Build timelines for each keyword (including content matches)
    print(f"\n[4/4] Building timelines for {len(top_keywords)} keywords...")
    print(f"  This includes both keyword matches and content matches...")
    keyword_timelines = {}
    
    def select_best_timestamp(timestamps):
        """
        Select the best timestamp from a list.
        PRIORITY: Use the FIRST timestamp that appears in the text
        (assumes summary file timestamps come first if they exist)
        """
        if not timestamps:
            return None, None
        
        # Simply use the first timestamp found
        # If it came from summary, it will be first (we prioritized summary)
        # Otherwise it's the first from the original file
        return timestamps[0]['parsed'], timestamps[0]
    
    for i, (keyword, count) in enumerate(top_keywords, 1):
        if i % 10 == 0:
            print(f"  Processing keyword {i}/{len(top_keywords)}...")
        
        # Get files where this keyword is explicitly listed
        keyword_match_files = keyword_to_files[keyword]
        
        # Find files where keyword appears in summary but not in keyword list
        content_match_files = set()
        keyword_lower = keyword.lower()
        
        for file_id, summary in file_summaries.items():
            # Skip if already in keyword matches
            if file_id in keyword_match_files:
                continue
            
            # Check if keyword appears in summary (case-insensitive)
            if keyword_lower in summary.lower():
                content_match_files.add(file_id)
        
        # Combine both sets
        timeline_entries = []
        
        # Add keyword matches
        for file_id in keyword_match_files:
            best_timestamp_iso = None
            best_timestamp_data = None
            
            if file_id in file_timestamps and file_timestamps[file_id]:
                best_timestamp_iso, best_timestamp_data = select_best_timestamp(file_timestamps[file_id])
            
            # Only include entries with timestamps from year 2000 to Dec 1, 2025
            if best_timestamp_iso:
                try:
                    date_obj = datetime.fromisoformat(best_timestamp_iso)
                    cutoff_date = datetime(2025, 12, 1)
                    if date_obj.year < 2000 or date_obj >= cutoff_date:
                        best_timestamp_iso = None
                        best_timestamp_data = None
                except:
                    pass
            
            # Clean the summary before adding to timeline
            raw_summary = file_summaries.get(file_id, 'No summary available')
            cleaned_summary = clean_summary(raw_summary)
            
            entry = {
                'file_id': file_id,
                'summary': cleaned_summary,
                'timestamp': best_timestamp_iso,
                'timestamp_raw': best_timestamp_data['raw'] if best_timestamp_data else None,
                'keywords': file_to_keywords.get(file_id, []),
                'match_type': 'keyword'
            }
            timeline_entries.append(entry)
        
        # Add content matches
        for file_id in content_match_files:
            best_timestamp_iso = None
            best_timestamp_data = None
            
            if file_id in file_timestamps and file_timestamps[file_id]:
                best_timestamp_iso, best_timestamp_data = select_best_timestamp(file_timestamps[file_id])
            
            # Only include entries with timestamps from year 2000 to Dec 1, 2025
            if best_timestamp_iso:
                try:
                    date_obj = datetime.fromisoformat(best_timestamp_iso)
                    cutoff_date = datetime(2025, 12, 1)
                    if date_obj.year < 2000 or date_obj >= cutoff_date:
                        best_timestamp_iso = None
                        best_timestamp_data = None
                except:
                    pass
            
            # Clean the summary before adding to timeline
            raw_summary = file_summaries.get(file_id, 'No summary available')
            cleaned_summary = clean_summary(raw_summary)
            
            entry = {
                'file_id': file_id,
                'summary': cleaned_summary,
                'timestamp': best_timestamp_iso,
                'timestamp_raw': best_timestamp_data['raw'] if best_timestamp_data else None,
                'keywords': file_to_keywords.get(file_id, []),
                'match_type': 'content'
            }
            timeline_entries.append(entry)
        
        # Sort by timestamp
        def get_date(entry):
            if entry['timestamp']:
                try:
                    return datetime.fromisoformat(entry['timestamp'])
                except:
                    pass
            return datetime.max  # Put entries without dates at the end
        
        timeline_entries.sort(key=get_date)
        
        keyword_timelines[keyword] = {
            'count': count,
            'keyword_match_count': len(keyword_match_files),
            'content_match_count': len(content_match_files),
            'total_files': len(keyword_match_files) + len(content_match_files),
            'timeline': timeline_entries
        }
    
    # Re-sort keywords by total_files (keyword + content matches)
    print("\nRe-sorting keywords by total file count (keyword + content matches)...")
    top_keywords = sorted(
        [(kw, keyword_timelines[kw]['total_files']) for kw, _ in top_keywords],
        key=lambda x: x[1],
        reverse=True
    )
    print(f"Top 10 Keywords by Total Files:")
    for keyword, total in top_keywords[:10]:
        print(f"  {keyword}: {total} total files (keyword + content matches)")
    
    # Step 5: Save results - separate files for each keyword + timeline by year
    print("\n[5/6] Saving results to separate files...")
    
    # Create output directory if it doesn't exist
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Build timeline by year (all files organized by year)
    print("\nBuilding timeline by year...")
    timeline_by_year = {}
    
    for file_id in file_to_keywords.keys():
        # Get timestamp for this file
        best_timestamp_iso = None
        best_timestamp_data = None
        
        if file_id in file_timestamps and file_timestamps[file_id]:
            best_timestamp_iso, best_timestamp_data = select_best_timestamp(file_timestamps[file_id])
        
        # Filter to year 2000 through Nov 30, 2025
        if best_timestamp_iso:
            try:
                date_obj = datetime.fromisoformat(best_timestamp_iso)
                cutoff_date = datetime(2025, 12, 1)
                if date_obj.year < 2000 or date_obj >= cutoff_date:
                    best_timestamp_iso = None
                    best_timestamp_data = None
            except:
                pass
        
        # Add to timeline by year
        if best_timestamp_iso:
            try:
                date_obj = datetime.fromisoformat(best_timestamp_iso)
                year = date_obj.year
                
                if year not in timeline_by_year:
                    timeline_by_year[year] = []
                
                # Clean the summary before adding to timeline
                raw_summary = file_summaries.get(file_id, 'No summary available')
                cleaned_summary = clean_summary(raw_summary)
                
                entry = {
                    'file_id': file_id,
                    'summary': cleaned_summary,
                    'timestamp': best_timestamp_iso,
                    'timestamp_raw': best_timestamp_data['raw'] if best_timestamp_data else None,
                    'keywords': file_to_keywords.get(file_id, [])
                }
                timeline_by_year[year].append(entry)
            except:
                pass
    
    # Sort entries within each year
    for year in timeline_by_year:
        timeline_by_year[year].sort(key=lambda x: x['timestamp'])
    
    print(f"  Organized {sum(len(entries) for entries in timeline_by_year.values())} files across {len(timeline_by_year)} years")
    
    # Step 6: Calculate keyword co-occurrences (shared documents)
    print("\n[6/6] Calculating keyword co-occurrences for network graph...")
    keyword_connections = {}
    
    # For each pair of keywords, count how many documents they share
    for i, (kw1, _) in enumerate(top_keywords):
        if i % 10 == 0:
            print(f"  Processing keyword {i}/{len(top_keywords)}...")
        
        keyword_connections[kw1] = {}
        files1 = keyword_to_files[kw1]
        
        for j, (kw2, _) in enumerate(top_keywords):
            if i >= j:  # Skip same keyword and avoid duplicates
                continue
            
            files2 = keyword_to_files[kw2]
            shared_docs = len(files1 & files2)  # Set intersection
            
            if shared_docs > 0:
                keyword_connections[kw1][kw2] = shared_docs
    
    print(f"  Calculated co-occurrences for {len(keyword_connections)} keywords")
    
    # Create index file with metadata and keyword list
    index_data = {
        'metadata': {
            'generated_at': datetime.now().isoformat(),
            'total_files': len(file_to_keywords),
            'total_keywords': len(keyword_counter),
            'min_occurrences': MIN_KEYWORD_OCCURRENCES,
            'keywords_included': len(top_keywords),
            'files_with_timestamps': len(file_timestamps)
        },
        'top_keywords': [
            {
                'keyword': kw,
                'count': keyword_timelines[kw]['count'],
                'file_count': keyword_timelines[kw]['keyword_match_count'],
                'total_files': keyword_timelines[kw]['total_files'],
                'data_file': f"keyword_{i+1:03d}.json"  # e.g., keyword_001.json
            }
            for i, (kw, total) in enumerate(top_keywords)
        ],
        'keyword_connections': keyword_connections
    }
    
    # Add timeline by year data to index
    index_data['timeline_by_year'] = {
        'years': sorted(timeline_by_year.keys()),
        'total_files': sum(len(entries) for entries in timeline_by_year.values()),
        'data_file': 'timeline_by_year.json'
    }
    
    # Save index file
    with open(OUTPUT_INDEX_FILE, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Index file saved: {OUTPUT_INDEX_FILE}")
    print(f"  Size: {os.path.getsize(OUTPUT_INDEX_FILE) / 1024:.2f} KB")
    
    # Save timeline by year file
    timeline_by_year_file = OUTPUT_DIR / 'timeline_by_year.json'
    with open(timeline_by_year_file, 'w', encoding='utf-8') as f:
        json.dump(timeline_by_year, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Timeline by year saved: {timeline_by_year_file}")
    print(f"  Size: {os.path.getsize(timeline_by_year_file) / 1024 / 1024:.2f} MB")
    
    # Save individual keyword timeline files
    print(f"\nSaving individual keyword files...")
    total_size = 0
    
    def sanitize_filename(keyword):
        """Convert keyword to safe filename"""
        # Replace spaces and special characters
        safe = keyword.replace(' ', '_').replace('/', '_').replace('\\', '_')
        safe = safe.replace(':', '_').replace('*', '_').replace('?', '_')
        safe = safe.replace('"', '_').replace('<', '_').replace('>', '_')
        safe = safe.replace('|', '_').replace('.', '_')
        # Limit length
        if len(safe) > 50:
            safe = safe[:50]
        return safe.lower()
    
    for i, (keyword, total) in enumerate(top_keywords, 1):
        if i % 10 == 0 or i == 1:
            print(f"  Saving keyword {i}/{len(top_keywords)}...")
        
        keyword_data = {
            'keyword': keyword,
            'count': keyword_timelines[keyword]['count'],
            'keyword_match_count': keyword_timelines[keyword]['keyword_match_count'],
            'content_match_count': keyword_timelines[keyword]['content_match_count'],
            'total_files': keyword_timelines[keyword]['total_files'],
            'timeline': keyword_timelines[keyword]['timeline']
        }
        
        # New filename format: keyword_XXX_actual_keyword.json
        safe_keyword = sanitize_filename(keyword)
        filename = f"keyword_{i:03d}_{safe_keyword}.json"
        filepath = OUTPUT_DIR / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(keyword_data, f, indent=2, ensure_ascii=False)
        
        file_size = os.path.getsize(filepath)
        total_size += file_size
    
    total_size += os.path.getsize(OUTPUT_INDEX_FILE)
    
    print(f"\n✓ All files saved to: {OUTPUT_DIR}")
    print(f"✓ Total files created: {len(top_keywords) + 1} (index + {len(top_keywords)} keyword files)")
    print(f"✓ Total size: {total_size / 1024 / 1024:.2f} MB")
    print(f"✓ Average keyword file size: {(total_size - os.path.getsize(OUTPUT_INDEX_FILE)) / len(top_keywords) / 1024:.2f} KB")
    
    # Print summary statistics
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE - Summary Statistics")
    print("=" * 80)
    print(f"Total files analyzed: {len(file_to_keywords)}")
    print(f"Total unique keywords: {len(keyword_counter)}")
    print(f"Files with timestamps: {len(file_timestamps)}")
    print(f"Keywords with {MIN_KEYWORD_OCCURRENCES}+ occurrences: {len(top_keywords)}")
    print(f"Keyword files saved with timelines: {len(top_keywords)}")
    print("=" * 80)


if __name__ == "__main__":
    try:
        process_all_files()
    except KeyboardInterrupt:
        print("\n\nProcess interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
