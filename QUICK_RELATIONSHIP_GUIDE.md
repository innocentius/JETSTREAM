# Quick Relationship Guide

## What You'll See

When viewing documents in the timeline, some will have a **"🔗 Related Documents"** section showing:

### Color-Coded Badges

- 🔴 **RED** = Highly Relevant (70%+ shared keywords) - Very similar documents
- 🟠 **ORANGE** = Relevant (50-70% shared keywords) - Related documents  
- 🟡 **YELLOW** = Somewhat Relevant (30-50% shared keywords) - Loosely related
- ⚫ **GRAY** = Low Relevance (<30% shared keywords) - Weak connection

### Two Sections

- **⬆️ Previous Related** - Up to 3 earlier documents that are related
- **⬇️ Next Related** - Up to 3 later documents that are related

## How to Use It

1. **Find documents with relationships** - Look for the "🔗 Related Documents" section
2. **Click any badge** - Instantly scroll to that related document
3. **Watch for the pulse** - The target document will flash to show you where it is
4. **Keep exploring** - Click relationships on the new document to continue

## What It Means

- **Many RED badges** = This document is part of a closely-related document cluster
- **Mix of colors** = Varied levels of connection to surrounding documents
- **No relationships** = This document is unique or doesn't share many keywords
- **Chain of relationships** = Following badges creates a document trail

## Example

```
Document: EFTA00012345
🔗 Related Documents
  ⬆️ Previous Related
    [📄 EFTA00012340] [75%] ← RED: Very similar to this document
    [📄 EFTA00012338] [52%] ← ORANGE: Related but less similar
  
  ⬇️ Next Related  
    [📄 EFTA00012350] [68%] ← ORANGE: Fairly related
    [📄 EFTA00012355] [55%] ← ORANGE: Related
```

Click on EFTA00012340 → Jump to that document → See its relationships → Keep exploring!

## Tips

- **RED badges first** - Start with highly relevant documents for strongest connections
- **Follow chains** - Click through related documents to trace a story
- **Compare keywords** - Look at the keyword tags to see what they have in common
- **Use browser back button** - Navigate back if you get lost
- **Try different keywords** - Some keywords have more relationships than others

## Statistics

- **80,327** relationships found across all documents
- **19.5%** of documents have at least one relationship
- **0.69** relationships per document on average
- **15.5%** of relationships are "Highly Relevant" (red)
- **84.5%** of relationships are "Relevant" (orange)

## Need More Info?

- **Full Documentation**: See `RELATIONSHIPS_FEATURE.md`
- **Implementation Details**: See `RELATIONSHIP_SUMMARY.md`
- **Regenerate Relationships**: Run `python analyze_relationships.py`

---

**Happy exploring! 🔍**
