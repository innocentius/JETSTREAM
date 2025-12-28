import json
import os
from datetime import datetime
from collections import defaultdict

def calculate_similarity(keywords1, keywords2):
    """Calculate Jaccard similarity between two keyword sets"""
    set1 = set(keywords1)
    set2 = set(keywords2)
    
    if not set1 or not set2:
        return 0.0
    
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    
    return intersection / union if union > 0 else 0.0

def find_related_documents(timeline, current_idx, threshold=0.5):
    """
    Find related documents before and after the current document.
    
    Args:
        timeline: List of document objects
        current_idx: Index of current document
        threshold: Minimum similarity threshold (default 0.5 = 50%)
    
    Returns:
        Dictionary with 'previous' and 'next' lists of related documents
    """
    current_doc = timeline[current_idx]
    current_keywords = set(current_doc.get('keywords', []))
    
    # Find previous related documents
    previous_related = []
    for i in range(current_idx - 1, -1, -1):
        if len(previous_related) >= 3:
            break
        
        doc = timeline[i]
        similarity = calculate_similarity(current_keywords, doc.get('keywords', []))
        
        if similarity >= threshold:
            previous_related.append({
                'file_id': doc['file_id'],
                'similarity': round(similarity, 3),
                'index': i
            })
    
    # Find next related documents
    next_related = []
    for i in range(current_idx + 1, len(timeline)):
        if len(next_related) >= 3:
            break
        
        doc = timeline[i]
        similarity = calculate_similarity(current_keywords, doc.get('keywords', []))
        
        if similarity >= threshold:
            next_related.append({
                'file_id': doc['file_id'],
                'similarity': round(similarity, 3),
                'index': i
            })
    
    return {
        'previous': previous_related,
        'next': next_related
    }

def categorize_similarity(similarity):
    """Categorize similarity score into levels"""
    if similarity >= 0.7:
        return 'highly_relevant'  # Red
    elif similarity >= 0.5:
        return 'relevant'  # Orange
    elif similarity >= 0.3:
        return 'somewhat_relevant'  # Yellow
    else:
        return 'low_relevance'  # Default

def process_keyword_file(filepath, threshold=0.5):
    """Process a single keyword JSON file to add relationship data"""
    print(f"Processing {os.path.basename(filepath)}...")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    timeline = data.get('timeline', [])
    
    if not timeline:
        print(f"  No timeline data found in {filepath}")
        return
    
    # Add relationship data to each document
    for idx, doc in enumerate(timeline):
        relationships = find_related_documents(timeline, idx, threshold)
        
        # Add categorized relationships
        doc['relationships'] = {
            'previous': [
                {
                    **rel,
                    'category': categorize_similarity(rel['similarity'])
                }
                for rel in relationships['previous']
            ],
            'next': [
                {
                    **rel,
                    'category': categorize_similarity(rel['similarity'])
                }
                for rel in relationships['next']
            ]
        }
    
    # Save updated data
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"  ✓ Processed {len(timeline)} documents")

def generate_statistics(data_dir='data', threshold=0.5):
    """Generate statistics about document relationships"""
    stats = {
        'total_documents': 0,
        'documents_with_previous': 0,
        'documents_with_next': 0,
        'similarity_distribution': defaultdict(int),
        'avg_relationships_per_doc': 0
    }
    
    total_relationships = 0
    
    for filename in os.listdir(data_dir):
        if filename.startswith('keyword_') and filename.endswith('.json') and filename != 'keyword_connections.json':
            filepath = os.path.join(data_dir, filename)
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                timeline = data.get('timeline', [])
                stats['total_documents'] += len(timeline)
                
                for doc in timeline:
                    relationships = doc.get('relationships', {})
                    prev_count = len(relationships.get('previous', []))
                    next_count = len(relationships.get('next', []))
                    
                    if prev_count > 0:
                        stats['documents_with_previous'] += 1
                    if next_count > 0:
                        stats['documents_with_next'] += 1
                    
                    total_relationships += prev_count + next_count
                    
                    # Count by category
                    for rel in relationships.get('previous', []) + relationships.get('next', []):
                        category = rel.get('category', 'unknown')
                        stats['similarity_distribution'][category] += 1
            
            except Exception as e:
                print(f"  Error processing {filename}: {e}")
    
    if stats['total_documents'] > 0:
        stats['avg_relationships_per_doc'] = round(total_relationships / stats['total_documents'], 2)
    
    return dict(stats)

def main():
    data_dir = 'data'
    threshold = 0.5  # 50% similarity threshold
    
    print("=" * 60)
    print("Document Relationship Analysis")
    print("=" * 60)
    print(f"Threshold: {threshold * 100}% keyword overlap")
    print()
    
    # Get all keyword files
    keyword_files = [
        os.path.join(data_dir, f) 
        for f in os.listdir(data_dir) 
        if f.startswith('keyword_') and f.endswith('.json') and f != 'keyword_connections.json'
    ]
    
    print(f"Found {len(keyword_files)} keyword files to process")
    print()
    
    # Process each file
    for filepath in sorted(keyword_files):
        try:
            process_keyword_file(filepath, threshold)
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    print()
    print("=" * 60)
    print("Generating Statistics...")
    print("=" * 60)
    
    stats = generate_statistics(data_dir, threshold)
    
    print(f"Total documents analyzed: {stats['total_documents']}")
    print(f"Documents with previous relationships: {stats['documents_with_previous']}")
    print(f"Documents with next relationships: {stats['documents_with_next']}")
    print(f"Average relationships per document: {stats['avg_relationships_per_doc']}")
    print()
    print("Similarity Distribution:")
    for category, count in sorted(stats['similarity_distribution'].items()):
        print(f"  {category}: {count}")
    
    # Save statistics
    stats_file = os.path.join(data_dir, 'relationship_stats.json')
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2)
    
    print()
    print(f"Statistics saved to {stats_file}")
    print()
    print("=" * 60)
    print("Analysis Complete!")
    print("=" * 60)

if __name__ == '__main__':
    main()
