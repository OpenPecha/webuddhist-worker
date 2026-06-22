import logging
from io import BytesIO

import boto3
from botocore.exceptions import ClientError
from fastapi import HTTPException, UploadFile
from starlette import status

from worker_api.config import get, get_int

logger = logging.getLogger(__name__)

# Initialize S3 client
s3_client = boto3.client(
    "s3",
    aws_access_key_id=get("AWS_ACCESS_KEY"),
    aws_secret_access_key=get("AWS_SECRET_KEY"),
    region_name=get("AWS_REGION"),
)


def upload_file(file: UploadFile, key: str):
    """
    Upload a file to S3 bucket.
    
    Args:
        file: FastAPI UploadFile object
        key: S3 object key (path in bucket)
    
    Returns:
        S3 key of uploaded file
    
    Raises:
        HTTPException: If upload fails
    """
    try:
        bucket_name = get("AWS_BUCKET_NAME")
        s3_client.upload_fileobj(file.file, bucket_name, key)
        logger.info(f"File uploaded successfully to S3: {key}")
        return key
    except ClientError as e:
        logger.error(f"Failed to upload file to S3: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Unexpected error uploading file to S3: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}",
        )


def upload_bytes(file_bytes: BytesIO, key: str, content_type: str = "image/jpeg"):
    """
    Upload bytes to S3 bucket.
    
    Args:
        file_bytes: BytesIO object containing file data
        key: S3 object key (path in bucket)
        content_type: MIME type of the file
    
    Returns:
        S3 key of uploaded file
    
    Raises:
        HTTPException: If upload fails
    """
    try:
        bucket_name = get("AWS_BUCKET_NAME")
        s3_client.upload_fileobj(
            file_bytes, bucket_name, key, ExtraArgs={"ContentType": content_type}
        )
        logger.info(f"Bytes uploaded successfully to S3: {key}")
        return key
    except ClientError as e:
        logger.error(f"Failed to upload bytes to S3: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload bytes: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Unexpected error uploading bytes to S3: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}",
        )


def generate_presigned_access_url(key: str, expiration: int = None) -> str:
    """
    Generate a presigned URL for accessing an S3 object.
    
    Args:
        key: S3 object key (path in bucket)
        expiration: URL expiration time in seconds (default from config)
    
    Returns:
        Presigned URL string
    
    Raises:
        HTTPException: If URL generation fails
    """
    try:
        bucket_name = get("AWS_BUCKET_NAME")
        if expiration is None:
            expiration = get_int("IMAGE_EXPIRATION_IN_SEC")
        
        url = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket_name, "Key": key},
            ExpiresIn=expiration,
        )
        return url
    except ClientError as e:
        logger.error(f"Failed to generate presigned URL: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate presigned URL: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Unexpected error generating presigned URL: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}",
        )


def delete_file(key: str):
    """
    Delete a file from S3 bucket.
    
    Args:
        key: S3 object key (path in bucket)
    
    Raises:
        HTTPException: If deletion fails
    """
    try:
        bucket_name = get("AWS_BUCKET_NAME")
        s3_client.delete_object(Bucket=bucket_name, Key=key)
        logger.info(f"File deleted successfully from S3: {key}")
    except ClientError as e:
        logger.error(f"Failed to delete file from S3: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete file: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Unexpected error deleting file from S3: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}",
        )
