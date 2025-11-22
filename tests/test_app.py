import pytest
import os
import sys
import io
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app
from app.services.document_processor import process_documents
from app.utils.pdf_utils import extract_text_from_pdf

client = TestClient(app)


class TestRootEndpoint:
    
    def test_root_endpoint_success(self):
        response = client.get("/")
        assert response.status_code == 200
        assert "message" in response.json()
        assert response.json()["message"] == "Welcome to the Document Processing API"
    
    def test_root_endpoint_method_not_allowed(self):
        response = client.post("/")
        assert response.status_code == 405


class TestProcessDocumentsEndpoint:
    
    def test_process_documents_no_files(self):
        response = client.post("/process-documents")
        assert response.status_code == 422
    
    def test_process_documents_empty_files_list(self):
        response = client.post("/process-documents", files=[])
        assert response.status_code == 422
    
    @patch('app.api.routes.extract_field_from_document')
    @patch('app.api.routes.process_documents')
    def test_process_documents_with_pdf(self, mock_process, mock_extract):
        mock_process.return_value = {
            "pdf_text": "Sample PDF content"
        }
        mock_extract.return_value = {
            "text_extraction": {
                "bill_of_lading_number": "BL123",
                "container_number": "CONT456"
            }
        }
        
        pdf_content = b"%PDF-1.4 sample content"
        files = [
            ("files", ("test.pdf", io.BytesIO(pdf_content), "application/pdf"))
        ]
        response = client.post("/process-documents", files=files)
        
        assert response.status_code == 200
        assert "extracted_data" in response.json()
        mock_process.assert_called_once()
        mock_extract.assert_called_once()
    
    @patch('app.api.routes.extract_field_from_document')
    @patch('app.api.routes.process_documents')
    def test_process_documents_with_xlsx(self, mock_process, mock_extract):
        mock_process.return_value = {
            "xlsx_text": "Sample Excel content"
        }
        mock_extract.return_value = {
            "text_extraction": {
                "line_items_count": 5,
                "average_price": 100.50
            }
        }
        
        xlsx_content = b"PK\x03\x04sample xlsx"
        files = [
            ("files", ("test.xlsx", io.BytesIO(xlsx_content), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"))
        ]
        response = client.post("/process-documents", files=files)
        
        assert response.status_code == 200
        assert "extracted_data" in response.json()
        mock_process.assert_called_once()
        mock_extract.assert_called_once()
    
    @patch('app.api.routes.extract_field_from_document')
    @patch('app.api.routes.process_documents')
    def test_process_documents_with_multiple_files(self, mock_process, mock_extract):
        mock_process.return_value = {
            "pdf_text": "Sample PDF",
            "xlsx_text": "Sample Excel"
        }
        mock_extract.return_value = {
            "text_extraction": {
                "bill_of_lading_number": "BL123"
            }
        }
        
        pdf_content = b"%PDF-1.4"
        xlsx_content = b"PK\x03\x04"
        files = [
            ("files", ("test.pdf", io.BytesIO(pdf_content), "application/pdf")),
            ("files", ("test.xlsx", io.BytesIO(xlsx_content), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"))
        ]
        response = client.post("/process-documents", files=files)
        
        assert response.status_code == 200
        assert "extracted_data" in response.json()
    
    @patch('app.api.routes.process_documents')
    def test_process_documents_processing_error(self, mock_process):
        mock_process.side_effect = Exception("Processing failed")
        
        pdf_content = b"%PDF-1.4"
        files = [
            ("files", ("test.pdf", io.BytesIO(pdf_content), "application/pdf"))
        ]
        
        with pytest.raises(Exception):
            response = client.post("/process-documents", files=files)
    
    @patch('app.api.routes.extract_field_from_document')
    @patch('app.api.routes.process_documents')
    def test_process_documents_extraction_error(self, mock_process, mock_extract):
        mock_process.return_value = {"pdf_text": "Sample"}
        mock_extract.return_value = {"error": "Extraction failed"}
        
        pdf_content = b"%PDF-1.4"
        files = [
            ("files", ("test.pdf", io.BytesIO(pdf_content), "application/pdf"))
        ]
        response = client.post("/process-documents", files=files)
        
        assert response.status_code == 200
        assert "extracted_data" in response.json()
        assert "error" in response.json()["extracted_data"]
    
    @patch('app.api.routes.extract_field_from_document')
    @patch('app.api.routes.process_documents')
    def test_process_documents_file_cleanup(self, mock_process, mock_extract):
        mock_process.return_value = {"pdf_text": "Sample"}
        mock_extract.return_value = {"text_extraction": {}}
        
        pdf_content = b"%PDF-1.4"
        files = [
            ("files", ("test.pdf", io.BytesIO(pdf_content), "application/pdf"))
        ]
        
        with patch('os.unlink') as mock_unlink:
            response = client.post("/process-documents", files=files)
            assert response.status_code == 200
            mock_unlink.assert_called()
    
    @patch('app.api.routes.extract_field_from_document')
    @patch('app.api.routes.process_documents')
    def test_process_documents_with_unsupported_file(self, mock_process, mock_extract):
        mock_process.return_value = {}
        mock_extract.return_value = {"error": "No text could be extracted"}
        
        txt_content = b"Plain text"
        files = [
            ("files", ("test.txt", io.BytesIO(txt_content), "text/plain"))
        ]
        response = client.post("/process-documents", files=files)
        
        assert response.status_code == 200
        assert "extracted_data" in response.json()


class TestHealthCheckEndpoint:
    
    @patch('openai.OpenAI')
    def test_health_check_openai_success(self, mock_openai):
        mock_client = Mock()
        mock_response = Mock()
        mock_parsed = Mock()
        mock_parsed.status = "OK"
        mock_parsed.message = "API is working"
        mock_response.output_parsed = mock_parsed
        mock_client.responses.parse.return_value = mock_response
        mock_openai.return_value = mock_client
        
        response = client.get("/health-check/openai")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["message"] == "OpenAI API is accessible"
        assert data["model"] == "gpt-5-mini"
        assert "response" in data
        assert data["response"]["status"] == "OK"
    
    @patch('openai.OpenAI')
    def test_health_check_openai_api_error(self, mock_openai):
        mock_openai.side_effect = Exception("API connection failed")
        
        response = client.get("/health-check/openai")
        
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert data["detail"]["status"] == "error"
        assert "Failed to connect to OpenAI API" in data["detail"]["message"]
    
    @patch('openai.OpenAI')
    def test_health_check_openai_auth_error(self, mock_openai):
        mock_openai.side_effect = Exception("Invalid API key")
        
        response = client.get("/health-check/openai")
        
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert data["detail"]["status"] == "error"
    
    @patch('openai.OpenAI')
    def test_health_check_openai_timeout(self, mock_openai):
        mock_openai.side_effect = TimeoutError("Request timeout")
        
        response = client.get("/health-check/openai")
        
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
    
    def test_health_check_method_not_allowed(self):
        response = client.post("/health-check/openai")
        assert response.status_code == 405


class TestDocumentProcessor:
    
    def test_extract_text_from_pdf_with_real_file(self):
        pdf_path = "tests/sample_bill_of_lading.pdf"
        
        if not os.path.exists(pdf_path):
            pytest.skip("Test PDF not found")
        
        text = extract_text_from_pdf(pdf_path)
        assert isinstance(text, str)
        assert len(text) > 0
    
    def test_process_documents_pdf(self):
        pdf_path = "tests/sample_bill_of_lading.pdf"
        
        if not os.path.exists(pdf_path):
            pytest.skip("Test PDF not found")
        
        result = process_documents([pdf_path])
        assert isinstance(result, dict)
        assert "pdf_text" in result
        assert len(result["pdf_text"]) > 0
    
    def test_process_documents_xlsx(self):
        xlsx_path = "tests/sample_invoice.xlsx"
        
        if not os.path.exists(xlsx_path):
            pytest.skip("Test XLSX not found")
        
        result = process_documents([xlsx_path])
        assert isinstance(result, dict)
        assert "xlsx_text" in result
        assert len(result["xlsx_text"]) > 0
    
    def test_process_documents_mixed(self):
        pdf_path = "tests/sample_bill_of_lading.pdf"
        xlsx_path = "tests/sample_invoice.xlsx"
        
        if not os.path.exists(pdf_path) or not os.path.exists(xlsx_path):
            pytest.skip("Test files not found")
        
        result = process_documents([pdf_path, xlsx_path])
        assert isinstance(result, dict)
        assert "pdf_text" in result
        assert "xlsx_text" in result
        assert len(result["pdf_text"]) > 0
        assert len(result["xlsx_text"]) > 0
    
    def test_process_documents_empty_list(self):
        result = process_documents([])
        assert isinstance(result, dict)
        assert len(result) == 0
    
    @patch('app.services.document_processor.extract_text_from_pdf')
    def test_process_documents_pdf_extraction_error(self, mock_extract):
        mock_extract.side_effect = Exception("PDF extraction failed")
        
        with pytest.raises(Exception):
            process_documents(["fake.pdf"])


class TestDataExtraction:
    
    def test_extracted_data_structure(self):
        expected_fields = [
            "bill_of_lading_number",
            "container_number",
            "consignee_name",
            "consignee_address",
            "date_of_export",
            "date",
            "line_items_count",
            "average_gross_weight",
            "average_price"
        ]
        
        assert len(expected_fields) == 9
        for field in expected_fields:
            assert isinstance(field, str)
            assert len(field) > 0


class TestAPIValidation:
    
    def test_invalid_endpoint(self):
        response = client.get("/invalid-endpoint")
        assert response.status_code == 404
    
    def test_process_documents_wrong_method(self):
        response = client.get("/process-documents")
        assert response.status_code == 405
    
    def test_cors_headers_present(self):
        response = client.get("/")
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
