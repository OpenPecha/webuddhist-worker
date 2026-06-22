import pytest
from unittest.mock import Mock, patch, MagicMock
from io import BytesIO
from botocore.exceptions import ClientError
from fastapi import HTTPException

from worker_api.uploads.S3_utils import (
    upload_file,
    upload_bytes,
    generate_presigned_access_url,
    download_bytes,
    delete_file,
)


@pytest.fixture
def mock_upload_file():
    mock_file = MagicMock()
    mock_file.file = BytesIO(b"test file content")
    mock_file.filename = "test.txt"
    return mock_file


class TestUploadFile:
    @patch("worker_api.uploads.S3_utils.s3_client")
    @patch("worker_api.uploads.S3_utils.get")
    def test_successful_upload(self, mock_get, mock_s3_client, mock_upload_file):
        mock_get.return_value = "test-bucket"
        
        result = upload_file(mock_upload_file, "test/path/file.txt")
        
        assert result == "test/path/file.txt"
        mock_s3_client.upload_fileobj.assert_called_once_with(
            mock_upload_file.file,
            "test-bucket",
            "test/path/file.txt"
        )
    
    @patch("worker_api.uploads.S3_utils.s3_client")
    @patch("worker_api.uploads.S3_utils.get")
    def test_client_error_raises_http_exception(self, mock_get, mock_s3_client, mock_upload_file):
        mock_get.return_value = "test-bucket"
        mock_s3_client.upload_fileobj.side_effect = ClientError(
            {"Error": {"Code": "NoSuchBucket", "Message": "Bucket not found"}},
            "upload_fileobj"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            upload_file(mock_upload_file, "test/path/file.txt")
        
        assert exc_info.value.status_code == 500
        assert "Failed to upload file" in exc_info.value.detail
    
    @patch("worker_api.uploads.S3_utils.s3_client")
    @patch("worker_api.uploads.S3_utils.get")
    def test_unexpected_error_raises_http_exception(self, mock_get, mock_s3_client, mock_upload_file):
        mock_get.return_value = "test-bucket"
        mock_s3_client.upload_fileobj.side_effect = Exception("Unexpected error")
        
        with pytest.raises(HTTPException) as exc_info:
            upload_file(mock_upload_file, "test/path/file.txt")
        
        assert exc_info.value.status_code == 500
        assert "Unexpected error" in exc_info.value.detail


class TestUploadBytes:
    @patch("worker_api.uploads.S3_utils.s3_client")
    @patch("worker_api.uploads.S3_utils.get")
    def test_successful_upload(self, mock_get, mock_s3_client):
        mock_get.return_value = "test-bucket"
        file_bytes = BytesIO(b"test bytes content")
        
        result = upload_bytes(file_bytes, "test/path/image.jpg", "image/jpeg")
        
        assert result == "test/path/image.jpg"
        mock_s3_client.upload_fileobj.assert_called_once_with(
            file_bytes,
            "test-bucket",
            "test/path/image.jpg",
            ExtraArgs={"ContentType": "image/jpeg"}
        )
    
    @patch("worker_api.uploads.S3_utils.s3_client")
    @patch("worker_api.uploads.S3_utils.get")
    def test_default_content_type(self, mock_get, mock_s3_client):
        mock_get.return_value = "test-bucket"
        file_bytes = BytesIO(b"test bytes")
        
        result = upload_bytes(file_bytes, "test/path/file.jpg")
        
        assert result == "test/path/file.jpg"
        call_args = mock_s3_client.upload_fileobj.call_args
        assert call_args[1]["ExtraArgs"]["ContentType"] == "image/jpeg"
    
    @patch("worker_api.uploads.S3_utils.s3_client")
    @patch("worker_api.uploads.S3_utils.get")
    def test_client_error_raises_http_exception(self, mock_get, mock_s3_client):
        mock_get.return_value = "test-bucket"
        file_bytes = BytesIO(b"test bytes")
        mock_s3_client.upload_fileobj.side_effect = ClientError(
            {"Error": {"Code": "AccessDenied", "Message": "Access denied"}},
            "upload_fileobj"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            upload_bytes(file_bytes, "test/path/file.jpg")
        
        assert exc_info.value.status_code == 500
        assert "Failed to upload bytes" in exc_info.value.detail
    
    @patch("worker_api.uploads.S3_utils.s3_client")
    @patch("worker_api.uploads.S3_utils.get")
    def test_unexpected_error_raises_http_exception(self, mock_get, mock_s3_client):
        mock_get.return_value = "test-bucket"
        file_bytes = BytesIO(b"test bytes")
        mock_s3_client.upload_fileobj.side_effect = Exception("Unexpected error")
        
        with pytest.raises(HTTPException) as exc_info:
            upload_bytes(file_bytes, "test/path/file.jpg")
        
        assert exc_info.value.status_code == 500
        assert "Unexpected error" in exc_info.value.detail


class TestGeneratePresignedAccessUrl:
    @patch("worker_api.uploads.S3_utils.s3_client")
    @patch("worker_api.uploads.S3_utils.get")
    @patch("worker_api.uploads.S3_utils.get_int")
    def test_successful_generation_default_expiration(self, mock_get_int, mock_get, mock_s3_client):
        mock_get.return_value = "test-bucket"
        mock_get_int.return_value = 3600
        mock_s3_client.generate_presigned_url.return_value = "https://s3.amazonaws.com/presigned-url"
        
        result = generate_presigned_access_url("test/path/file.jpg")
        
        assert result == "https://s3.amazonaws.com/presigned-url"
        mock_s3_client.generate_presigned_url.assert_called_once_with(
            "get_object",
            Params={"Bucket": "test-bucket", "Key": "test/path/file.jpg"},
            ExpiresIn=3600
        )
    
    @patch("worker_api.uploads.S3_utils.s3_client")
    @patch("worker_api.uploads.S3_utils.get")
    def test_successful_generation_custom_expiration(self, mock_get, mock_s3_client):
        mock_get.return_value = "test-bucket"
        mock_s3_client.generate_presigned_url.return_value = "https://s3.amazonaws.com/presigned-url"
        
        result = generate_presigned_access_url("test/path/file.jpg", expiration=7200)
        
        assert result == "https://s3.amazonaws.com/presigned-url"
        call_args = mock_s3_client.generate_presigned_url.call_args
        assert call_args[1]["ExpiresIn"] == 7200
    
    @patch("worker_api.uploads.S3_utils.s3_client")
    @patch("worker_api.uploads.S3_utils.get")
    def test_client_error_raises_http_exception(self, mock_get, mock_s3_client):
        mock_get.return_value = "test-bucket"
        mock_s3_client.generate_presigned_url.side_effect = ClientError(
            {"Error": {"Code": "NoSuchKey", "Message": "Key not found"}},
            "generate_presigned_url"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            generate_presigned_access_url("test/path/file.jpg", expiration=3600)
        
        assert exc_info.value.status_code == 500
        assert "Failed to generate presigned URL" in exc_info.value.detail
    
    @patch("worker_api.uploads.S3_utils.s3_client")
    @patch("worker_api.uploads.S3_utils.get")
    def test_unexpected_error_raises_http_exception(self, mock_get, mock_s3_client):
        mock_get.return_value = "test-bucket"
        mock_s3_client.generate_presigned_url.side_effect = Exception("Unexpected error")
        
        with pytest.raises(HTTPException) as exc_info:
            generate_presigned_access_url("test/path/file.jpg", expiration=3600)
        
        assert exc_info.value.status_code == 500
        assert "Unexpected error" in exc_info.value.detail


class TestDownloadBytes:
    @patch("worker_api.uploads.S3_utils.s3_client")
    @patch("worker_api.uploads.S3_utils.get")
    def test_successful_download(self, mock_get, mock_s3_client):
        mock_get.return_value = "test-bucket"
        
        mock_body = MagicMock()
        mock_body.read.return_value = b"downloaded file content"
        
        mock_response = {"Body": mock_body}
        mock_s3_client.get_object.return_value = mock_response
        
        result = download_bytes("test/path/file.txt")
        
        assert result == b"downloaded file content"
        mock_s3_client.get_object.assert_called_once_with(
            Bucket="test-bucket",
            Key="test/path/file.txt"
        )
    
    @patch("worker_api.uploads.S3_utils.s3_client")
    @patch("worker_api.uploads.S3_utils.get")
    def test_client_error_raises_http_exception(self, mock_get, mock_s3_client):
        mock_get.return_value = "test-bucket"
        mock_s3_client.get_object.side_effect = ClientError(
            {"Error": {"Code": "NoSuchKey", "Message": "Key not found"}},
            "get_object"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            download_bytes("test/path/file.txt")
        
        assert exc_info.value.status_code == 400
        assert "Failed to download file" in exc_info.value.detail
    
    @patch("worker_api.uploads.S3_utils.s3_client")
    @patch("worker_api.uploads.S3_utils.get")
    def test_unexpected_error_raises_http_exception(self, mock_get, mock_s3_client):
        mock_get.return_value = "test-bucket"
        mock_s3_client.get_object.side_effect = Exception("Unexpected error")
        
        with pytest.raises(HTTPException) as exc_info:
            download_bytes("test/path/file.txt")
        
        assert exc_info.value.status_code == 500
        assert "Unexpected error" in exc_info.value.detail


class TestDeleteFile:
    @patch("worker_api.uploads.S3_utils.s3_client")
    @patch("worker_api.uploads.S3_utils.get")
    def test_successful_deletion(self, mock_get, mock_s3_client):
        mock_get.return_value = "test-bucket"
        
        delete_file("test/path/file.txt")
        
        mock_s3_client.delete_object.assert_called_once_with(
            Bucket="test-bucket",
            Key="test/path/file.txt"
        )
    
    @patch("worker_api.uploads.S3_utils.s3_client")
    @patch("worker_api.uploads.S3_utils.get")
    def test_client_error_raises_http_exception(self, mock_get, mock_s3_client):
        mock_get.return_value = "test-bucket"
        mock_s3_client.delete_object.side_effect = ClientError(
            {"Error": {"Code": "AccessDenied", "Message": "Access denied"}},
            "delete_object"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            delete_file("test/path/file.txt")
        
        assert exc_info.value.status_code == 500
        assert "Failed to delete file" in exc_info.value.detail
    
    @patch("worker_api.uploads.S3_utils.s3_client")
    @patch("worker_api.uploads.S3_utils.get")
    def test_unexpected_error_raises_http_exception(self, mock_get, mock_s3_client):
        mock_get.return_value = "test-bucket"
        mock_s3_client.delete_object.side_effect = Exception("Unexpected error")
        
        with pytest.raises(HTTPException) as exc_info:
            delete_file("test/path/file.txt")
        
        assert exc_info.value.status_code == 500
        assert "Unexpected error" in exc_info.value.detail
