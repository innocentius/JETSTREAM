# 📊 EPF Visualizer

> **Interactive timeline visualization of FBI document collections with intelligent keyword extraction and document relationship analysis**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Web App](https://img.shields.io/badge/demo-live-brightgreen.svg)](#quick-start)

---

## 🎯 Overview

EPF Visualizer is a comprehensive document analysis and visualization tool that processes the epstein file collections, extracting keywords, building chronological timelines, and identifying relationships between documents. The web interface provides an intuitive way to explore 10,777 documents across 498 keywords spanning from 2000 to 2025.

### ✨ Key Features

- **📑 498 Keywords** - Automatically extracted and analyzed (25+ occurrences threshold)
- **📅 Timeline View** - Documents organized by year from 2000-2025
- **🕸️ Network Graph** - Visual keyword relationships based on shared documents
- **🔗 Document Relationships** - AI-powered similarity detection (50%+ keyword overlap)
- **🎨 Dark/Light Theme** - Automatic theme switching
- **🔍 Search & Filter** - Real-time keyword search

---

## 📸 Screenshots

### Timeline View
Browse documents chronologically with keyword highlights and related document suggestions.

### Network Graph
Explore keyword relationships with interactive force-directed graph visualization.

### Document Details
View full summaries, timestamps, and related keywords with color-coded relevance badges.

---

## 🚀 Quick Start

### Option 1: Run Analysis (Advanced)

If you have the source documents:

```bash
# Ensure folder structure:
# - Original Files/          (raw EFTA documents)
# - Summary and Keywords/    (AI-extracted data)

# Run the analysis
python analyze_data.py

# Generate document relationships
python analyze_relationships.py

# Verify results
python test_results.py
```

### Option 2: Online deployment


This repository is deployed with cloudflare pages (https://jetstream.naturemag.org).


---

## 📦 Project Structure

```
EPF_Visualizer_web/
├── index.html                      # Main web interface
├── run_server.py                   # Local development server
├── analyze_data.py                 # Main analysis script
├── analyze_relationships.py        # Document relationship analyzer
├── test_results.py                 # Verification script
├── test_relationships.py           # Relationship testing
│
├── data/                           # Generated JSON files (122 MB)
│   ├── index.json                  # Main index (427 KB)
│   ├── keyword_001_epstein.json    # Keyword timelines
│   ├── keyword_002_email.json
│   └── ... (498 keyword files)
│   ├── timeline_by_year.json       # Year-organized timeline
│   └── relationship_stats.json     # Relationship statistics
│
├── Original Files/                 # Source documents (excluded via .gitignore)
└── Summary and Keywords/           # Extracted data (excluded via .gitignore)
```

---

## 📊 Dataset Statistics

### Current Dataset (December 28, 2025)

| Metric | Value |
|--------|-------|
| **Total Documents** | 10,777 |
| **Documents with Timestamps** | 9,555 (88.7%) |
| **Unique Keywords Found** | 22,545 |
| **Keywords Tracked** | 498 (≥25 occurrences) |
| **Date Range** | 2000 - 2025 |
| **Total Data Size** | 122 MB |
| **Document Relationships** | 80,327 |

### Top 10 Keywords

1. **epstein** - 5,677 total documents (3,384 keyword matches + 2,293 content matches)
2. **email** - 4,462 total documents (540 keyword + 3,922 content)
3. **document** - 4,294 total documents (54 keyword + 4,240 content)
4. **request** - 4,270 total documents
5. **new york** - 3,772 total documents
6. **efta** - 3,719 total documents
7. **case** - 3,655 total documents
8. **jeffrey** - 3,618 total documents
9. **jeffrey epstein** - 3,532 total documents
10. **attorney** - 3,458 total documents

---

## 🛠️ Technology Stack

### Backend (Python 3.8+)
- **No external dependencies** - Uses only Python standard library
- `pathlib` - Cross-platform file handling
- `json` - Data serialization
- `collections` - Data structures (Counter, defaultdict)
- `datetime` - Timestamp parsing

### Frontend
- **Pure HTML/CSS/JavaScript** - No frameworks required
- Canvas API - Network graph visualization
- Fetch API - Lazy data loading
- CSS Grid/Flexbox - Responsive layout

---

## 📖 Features in Detail

### 1. Keyword Timeline Explorer

Browse 498 keywords extracted from FBI documents:
- **Keyword Matches** - Documents explicitly tagged with the keyword
- **Content Matches** - Documents containing the keyword in summary text
- **Smart Filtering** - Excludes redaction-related keywords
- **Chronological Sorting** - Documents ordered by timestamp

### 2. Year-Based Timeline

View all documents organized by year:
- **2000-2025 Coverage** - Only validated dates included
- **Year Clusters** - See document density over time
- **Quick Navigation** - Jump to any year
- **Statistics** - Document count per year

### 3. Network Graph Visualization

Interactive keyword relationship map:
- **Force-Directed Layout** - Keywords cluster by similarity
- **Connection Strength** - Line thickness = shared document count
- **Adjustable Parameters**:
  - Min Keyword Count (10-100)
  - Connection Strength (1-10)
  - Max Keywords (20-100)
- **Click to Explore** - Click any node to view that keyword's timeline

### 4. Document Relationships

AI-powered document similarity detection:
- **Jaccard Similarity** - Measures keyword overlap between documents
- **Color-Coded Relevance**:
  - 🔴 **Red** = Highly Relevant (≥70% shared keywords)
  - 🟠 **Orange** = Relevant (50-70% shared keywords)
  - 🟡 **Yellow** = Somewhat Relevant (30-50% shared keywords)
- **Directional Links** - Up to 3 previous + 3 next related documents
- **One-Click Navigation** - Jump between related documents

### 5. Search & Filter

Powerful search capabilities:
- **Real-time Keyword Search** - Filter as you type
- **Date Range Filtering** - Focus on specific time periods
- **Keyword Highlighting** - Matches highlighted in summaries
- **Result Counts** - See filtered totals instantly

---

## 🔧 How It Works

### Data Processing Pipeline

```
┌─────────────────────┐
│  Source Documents   │  10,777 EFTA labeled text files
│   (Original Files)  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  AI Extraction      │  Gemma 3 4B model
│  (Summary/Keywords) │  → Summaries + Keywords
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  analyze_data.py    │  → Keyword extraction
│                     │  → Timestamp parsing (multi-format)
│                     │  → Timeline building
│                     │  → Keyword co-occurrence calculation
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│analyze_relationships│  → Jaccard similarity calculation
│       .py           │  → Relationship graph building
│                     │  → Relevance categorization
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   JSON Data Files   │  498 keyword files + index
│    (data/ folder)   │  122 MB total
└─────────────────────┘
```

### Timestamp Extraction

The analysis script supports multiple date formats:
- **Full Dates**: "May 8, 2007", "August 23, 1972"
- **Numeric**: "1/20/1953", "2007-05-08", "2019-07-01"
- **Document Dates**: "Dated this 28th day of May, 2007"
- **Abbreviated**: "Jan. 4, 2000", "Aug 10, 2019"

**Validation**: Only dates from 2000-2025 are included in the final output.

### Keyword Filtering

Intelligent keyword extraction with filtering:
- ✅ Minimum 25 occurrences
- ✅ Minimum 3 characters
- ❌ Keywords containing "redaction"
- ❌ 4-digit years (1900-2099)
- ❌ Generic noise terms

### Relationship Algorithm

**Jaccard Similarity**:
```
Similarity = |Shared Keywords| / |Total Unique Keywords|

Example:
Doc A: [epstein, email, florida, victim, fbi]
Doc B: [epstein, email, attorney, victim, court]

Shared: {epstein, email, victim} = 3
Total: {epstein, email, florida, victim, fbi, attorney, court} = 7

Similarity = 3/7 = 42.9% → 🟡 Somewhat Relevant
```

---

## 📝 Configuration

### Analysis Script Options

Edit `analyze_data.py` to customize:

```python
MIN_KEYWORD_OCCURRENCES = 25  # Minimum keyword frequency
MIN_KEYWORD_LENGTH = 3        # Minimum keyword length
```

### Relationship Threshold

Edit `analyze_relationships.py`:

```python
threshold = 0.5  # 50% minimum keyword similarity
```

### Web Server Port

Edit `run_server.py`:

```python
PORT = 8000  # Change to your preferred port
```

---

## 🎨 Usage Tips

### For Researchers
- Use **Network Graph** to discover topic clusters
- Follow **document relationships** to trace event sequences
- Export keyword timelines for external analysis
- Cross-reference with original documents using file IDs

### For Investigators
- Search for specific **people**, **places**, or **events**
- Identify document clusters around key dates
- Trace communication patterns via email keywords
- Verify timeline consistency across documents

### For Developers
- All data in standard JSON format
- Easy to integrate with other tools
- RESTful data structure (index → keyword files)
- Lazy loading prevents memory issues

---

## 🔒 Privacy & Security

- ✅ No external API calls - runs entirely locally
- ✅ No tracking or analytics
- ✅ All data processed offline

**Note**: This tool processes public document releases. No confidential or classified information is included.

---

## ⚠️ Important Notices

### AI-Generated Content
Summaries and keywords are AI-generated using Gemma 3 4B. **Errors WILL occur**. We are not responsible for inaccuracies in AI-extracted content.

### Data Accuracy
- Timestamps extracted from document content (not metadata)
- Some documents may lack dates or have parsing errors
- Keyword extraction quality depends on source document formatting

### Legal Disclaimer
This tool is for research and educational purposes. All source documents are publicly available releases. No confidential or classified information is processed or distributed.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Gemma 3** - AI model used for summary/keyword extraction
- **Open Source Community** - For inspiration and tools
- **ChadIDE** - For providing the tools for vibe coding
---

## 🚀 Roadmap

### Planned Features
- [ ] Export functionality (PDF, CSV)
- [ ] Advanced search (Boolean operators)
- [ ] Saved searches/bookmarks
- [ ] Keyword weighting system
- [ ] Cross-keyword relationship visualization
- [ ] Document clustering (ML-based)
- [ ] Full-text search in original documents
- [ ] Mobile app (React Native)

### Potential Improvements
- [ ] Semantic similarity (beyond keyword matching)
- [ ] Entity recognition (people, places, organizations)
- [ ] Timeline event annotations
- [ ] Collaborative features (shared annotations)
- [ ] Integration with document management systems

---

## 📚 Additional Documentation

- **Quick Start**: See `QUICK_RELATIONSHIP_GUIDE.md`
- **Security Review**: See `OPEN_SOURCE_CHECKLIST.md` and `SECURITY_REVIEW.md`
- **For Developers**: See source code comments in `analyze_data.py`

---

**Built with ❤️ for transparency and research**

*Last Updated: December 28, 2025*
