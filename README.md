# Document Processing Application

A production-ready application that processes shipment documents (PDF, XLSX) and extracts structured data using AI.

## 🚀 Quick Start

### Docker Deployment (Recommended)

**Prerequisites:**

- Docker Engine 20.10+
- Docker Compose 2.0+
- OpenAI API key

**Setup and Run:**

```bash
cp .env.example .env
```

**Start all services:**

```bash
docker-compose up --build
```

**Access:**

- Frontend: http://localhost
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

**Useful commands:**

```bash
make build
make up
make down
make logs
make prod
```

See `DEPLOYMENT.md` for detailed deployment guide.

### Local Development

**Prerequisites:**

- Python 3.13+
- Node.js 18+
- OpenAI API key

**Backend:**

```bash
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Frontend:**

```bash
cd frontend
npm run dev
```

**Access:** Open `http://localhost:5174` in your browser

### Testing

**Run all tests:**

```bash
source venv/bin/activate
python -m pytest tests/test_app.py -v
```

**Generate sample test documents:**

```bash
source venv/bin/activate
python scripts/create_test_docs.py
```

## 📋 Features

- ✅ Upload multiple documents (PDF, XLSX)
- ✅ AI-powered data extraction using GPT-5-mini
- ✅ Editable form with extracted data
- ✅ Side-by-side document preview
- ✅ Comprehensive test suite (8 tests passing)
- ✅ Sample test documents included

## 🧪 Test Files

Sample documents are available in `tests/`:

- `sample_bill_of_lading.pdf` - Bill of lading with shipping details
- `sample_invoice.xlsx` - Commercial invoice with line items

## 📦 Tech Stack

**Backend:**

- FastAPI
- openai
- PyPDF2 (PDF extraction)
- Pandas (XLSX processing)

**Frontend:**

- React + Vite
- Tailwind CSS
- Axios

## 🔧 Configuration

LLM settings are in `app/services/llm_service.py`:

- Model: `gpt-5-mini`
- Provider: Anthropic

## 📝 Extracted Fields

- Bill of lading number
- Container Number
- Consignee Name
- Consignee Address
- Date of export
- Date
- Line Items Count
- Average Gross Weight
- Average Price

## 📁 Project Structure

```
/app                    - Backend application code
/frontend               - React frontend application
/tests                  - Unit tests and test fixtures
/testDocs               - Real test documents for validation
/eval                   - Evaluation scripts and ground truth data
/scripts                - Utility and debug scripts
/docs                   - Project documentation and requirements
```

## 🐳 Docker Architecture

The application is fully containerized with:

- **Backend Container**: Python FastAPI service with OCR capabilities
- **Frontend Container**: React app served by Nginx
- **Bridge Network**: Secure communication between containers
- **Health Checks**: Automatic service monitoring
- **Volume Mounts**: Hot-reload support in development

See `DEPLOYMENT.md` for production deployment strategies.
