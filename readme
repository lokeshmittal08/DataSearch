
# Search CLI Tool

A powerful command-line interface for generating semantic embeddings from files and performing intelligent document search using natural language queries.

## Features

- 🚀 **Batch Processing**: Process entire directories of files with parallel ingestion
- 🔍 **Semantic Search**: Find documents using natural language queries, not just keywords
- 📊 **Multiple Output Formats**: View results as formatted tables or JSON
- 🔄 **Real-time Monitoring**: Watch directories for new files and auto-ingest them
- 📁 **Smart Tracking**: Avoid duplicate processing with built-in document tracking
- ⚡ **Parallel Processing**: Multi-threaded ingestion for faster processing
- 🎯 **Rich Metadata**: Store and search with comprehensive file information


Installation
Prerequisites

Docker and Docker Compose (for dev container).
Python 3.11 (if running outside Docker).

Setup

Clone the Repository:
git clone <repository-url>
cd <repository-name>


Set Up Dev Container:

Open the project in VS Code with the Dev Containers extension.
Reopen in the dev container (uses devcontainer.json and Dockerfile).
The container sets up Python 3.11, SQLite, and dependencies.


Install Dependencies (if not using dev container):
pip install -r requirements.txt


Directory Structure:

Place files (PDFs, images) in /app/data/documents or a custom directory.
Embeddings are stored in /app/storage (ChromaDB).
Temporary files are stored in /tmp.

## Quick Start

### 1. Generate Embeddings

Process all files in a directory:

```bash
python cli.py generate --path /path/to/documents
```

With custom metadata:

```bash
python cli.py generate --path /documents --metadata '{"project": "research", "team": "ai"}'
```

### 2. Search Documents

Find documents using natural language:

```bash
python cli.py query --text "machine learning algorithms"
```

Get more results in JSON format:

```bash
python cli.py query --text "python programming" --top-k 10 --output json
```

## Detailed Usage

### Generate Command

Process files and create embeddings for semantic search.

```bash
python cli.py generate [OPTIONS]
```

**Options:**

| Option | Required | Description | Example |
|--------|----------|-------------|---------|
| `--path` | ✅ | Root directory to process | `--path /documents` |
| `--background` | ❌ | Monitor directory for new files | `--background` |
| `--metadata` | ❌ | JSON metadata for all files | `--metadata '{"project": "docs"}'` |
| `--workers` | ❌ | Parallel processing threads (default: 4) | `--workers 8` |
| `--tracker-file` | ❌ | Custom tracker file location | `--tracker-file my_tracker.json` |

**Examples:**

```bash
# Basic usage
python cli.py generate --path /documents

# With background monitoring
python cli.py generate --path /documents --background

# High-performance processing
python cli.py generate --path /large-dataset --workers 16

# With custom metadata
python cli.py generate --path /research --metadata '{"department": "AI", "year": "2024"}'
```

### Query Command

Search through your embedded documents using natural language.

```bash
python cli.py query [OPTIONS]
```

**Options:**

| Option | Required | Description | Example |
|--------|----------|-------------|---------|
| `--text` | ✅ | Search query | `--text "neural networks"` |
| `--top-k` | ❌ | Number of results (default: 5) | `--top-k 10` |
| `--output` | ❌ | Format: table/json (default: table) | `--output json` |

**Examples:**

```bash
# Basic search
python cli.py query --text "artificial intelligence"

# Get more results
python cli.py query --text "python code examples" --top-k 15

# JSON output for programmatic use
python cli.py query --text "data analysis" --output json
```

### Tracker Management

The tool automatically tracks processed files to avoid duplicates.

#### Check Tracker Status

```bash
python cli.py tracker-status
```

View detailed information:

```bash
python cli.py tracker-status --verbose
```

#### Reset Tracker

Force reprocessing of all files:

```bash
python cli.py reset-tracker
```

Use custom tracker file:

```bash
python cli.py reset-tracker --tracker-file custom_tracker.json
```

## Advanced Features

### Background Monitoring

Monitor a directory for new files and automatically process them:

```bash
python cli.py generate --path /watch-folder --background
```

The tool will:
- Process existing files immediately
- Watch for new files being added
- Automatically ingest new files with the same metadata
- Skip files that are already processed
- Run until stopped with Ctrl+C

### Parallel Processing

Optimize processing speed with multiple workers:

```bash
# Light processing (2 workers)
python cli.py generate --path /documents --workers 2

# Heavy processing (16 workers)
python cli.py generate --path /large-dataset --workers 16
```

**Note**: More workers = faster processing but higher system load.

### Custom Metadata

Add structured metadata to all files:

```bash
python cli.py generate --path /documents --metadata '{
    "project": "research-2024",
    "department": "AI",
    "classification": "public",
    "version": "1.0"
}'
```

This metadata becomes searchable and appears in query results.

## Output Examples

### Table Output

```
python cli.py query --text "machine learning"
```

```
┌─────────────────────┬──────────────────────────────┬────────────┬─────────────────────────────────────┐
│ Filename            │ File Path                    │ Similarity │ Document Snippet                    │
├─────────────────────┼──────────────────────────────┼────────────┼─────────────────────────────────────┤
│ ml_guide.pdf        │ /docs/ml_guide.pdf           │ 0.8945     │ Machine learning is a subset of...  │
│ ai_research.txt     │ /docs/ai_research.txt        │ 0.8721     │ Artificial intelligence research... │
│ neural_nets.md      │ /docs/neural_nets.md         │ 0.8456     │ Neural networks are computing...    │
└─────────────────────┴──────────────────────────────┴────────────┴─────────────────────────────────────┘
```

### JSON Output

```bash
python cli.py query --text "machine learning" --output json
```

```json
[
  {
    "id": "doc_123",
    "filename": "ml_guide.pdf",
    "filepath": "/docs/ml_guide.pdf",
    "absolute_path": "/home/user/docs/ml_guide.pdf",
    "directory": "/docs",
    "mimetype": "application/pdf",
    "similarity": 0.8945,
    "distance": 0.1055,
    "document_snippet": "Machine learning is a subset of artificial intelligence that focuses on...",
    "metadata": {
      "filename": "ml_guide.pdf",
      "filepath": "/docs/ml_guide.pdf",
      "project": "research",
      "department": "AI"
    }
  }
]
```

## File Support

The tool processes various file types including:
- **Documents**: PDF, DOC, DOCX, TXT, MD
- **Code**: PY, JS, HTML, CSS, JSON, XML
- **Data**: CSV, TSV, JSON
- **And many more** (depends on your `AnyFileParser` implementation)

## Configuration

### Similarity Threshold

The search sensitivity is controlled by `SIMILARITY_THRESHOLD` in `app.config`. Lower values return more results but with potentially lower relevance.

### Tracker File

By default, the tool creates `.ingestion_tracker.json` to track processed files. You can:
- Customize location: `--tracker-file custom_tracker.json`
- Reset to reprocess files: `python cli.py reset-tracker`
- Check status: `python cli.py tracker-status`

## Workflow Examples

### Research Document Management

```bash
# Initial processing
python cli.py generate --path /research-papers --metadata '{"type": "research", "year": "2024"}'

# Daily queries
python cli.py query --text "transformer architecture"
python cli.py query --text "attention mechanisms" --top-k 8

# Add new papers (background monitoring)
python cli.py generate --path /research-papers --background
```

### Code Repository Analysis

```bash
# Process codebase
python cli.py generate --path /project-src --workers 8 --metadata '{"type": "source-code", "project": "myapp"}'

# Find code examples
python cli.py query --text "authentication implementation"
python cli.py query --text "database connection" --output json
```

### Document Compliance

```bash
# Process with compliance metadata
python cli.py generate --path /legal-docs --metadata '{"classification": "confidential", "retention": "7-years"}'

# Find specific documents
python cli.py query --text "privacy policy" --top-k 3
```

## Troubleshooting

### Common Issues

**"No results found"**
- Check if files were properly ingested
- Verify similarity threshold in config
- Try broader search terms

**"Directory does not exist"**
- Ensure the path exists and is accessible
- Use absolute paths for clarity

**Tracker issues**
- Reset tracker: `python cli.py reset-tracker`
- Check status: `python cli.py tracker-status --verbose`

**Performance issues**
- Reduce workers if system is overloaded
- Process smaller batches
- Check available system memory

### Getting Help

```bash
# General help
python cli.py --help

# Command-specific help
python cli.py generate --help
python cli.py query --help
```

## Best Practices

1. **Start Small**: Test with a small directory first
2. **Use Metadata**: Add meaningful metadata for better organization
3. **Monitor Resources**: Adjust workers based on system capabilities
4. **Regular Queries**: Test search quality with known documents
5. **Backup Tracker**: Keep your `.ingestion_tracker.json` file safe
6. **Meaningful Names**: Use descriptive filenames for better search results

Project Structure

/app/lib/: Core logic for file parsing, text cleaning, and embedding.
AnyFileParser.py: Parses PDFs and images.
Api.py: Handles ingestion and querying.
VectorStore.py: Manages ChromaDB and DPR embeddings.
TextCleaner.py, ImageParser.py, ImageExif.py, ImageObjects.py: File processing utilities.
util.py: Helper functions (e.g., list files, chunk text).


/app/data/documents/: Default directory for input files.
/app/storage/: ChromaDB storage for embeddings.
/app/cli.py: CLI interface for generating and querying embeddings.
/app/config.py: Configuration (paths, embedding parameters).
/app/pdf_utils.py: PDF text extraction utilities.
/app/models.py: Data models (e.g., FileInfo).

Dependencies
Key dependencies (see requirements.txt for full list):

Python 3.11
chromadb: Vector store for embeddings.
transformers: DPR models for embedding generation.
ultralytics: YOLO for image object detection.
docling, pdfplumber, pytesseract: PDF text extraction.


Contributing
Contributions are welcome! Please:

Fork the repository.
Create a feature branch (git checkout -b feature/xyz).
Submit a pull request with clear descriptions.

License
MIT License.
---

**Happy Searching!** 🔍✨
