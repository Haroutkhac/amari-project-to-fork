# Scripts Directory

Utility and debug scripts for development and testing.

## Scripts

### Docker Helper Scripts

- **setup-docker.sh** - Automated Docker deployment setup script with environment configuration
- **docker-healthcheck.sh** - Health check script for Docker containers and services

### Debug Scripts

- **debug_pdf_extraction.py** - Debug script to test PDF extraction and OpenAI response
- **debug_multi_doc.py** - Debug script to test combined PDF and XLSX extraction
- **verify_user_docs.py** - Script to verify extraction of specific test documents

### Analysis Scripts

- **analyze_pdf.py** - Test if PDF is image-based and requires OCR, analyze PDF structure

### Setup Scripts

- **create_test_docs.py** - Generate sample test documents (Bill of Lading PDF and Invoice XLSX)

## Usage

### Docker Scripts

Run from project root:

```bash
./scripts/setup-docker.sh
./scripts/docker-healthcheck.sh
```

### Python Scripts

Most scripts can be run directly from the project root:

```bash
python scripts/debug_pdf_extraction.py
python scripts/debug_multi_doc.py
python scripts/verify_user_docs.py
python scripts/analyze_pdf.py
python scripts/create_test_docs.py
```

Note: Some scripts may contain hardcoded paths that need to be adjusted for your environment.
