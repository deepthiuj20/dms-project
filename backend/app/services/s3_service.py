"""
S3 service for file operations
"""
import boto3
import uuid
from typing import Optional
from datetime import timedelta
from botocore.exceptions import ClientError

from app.utils.config import settings
from app.utils.logger import setup_logger
from app.utils.exceptions import S3Exception, ValidationException
from app.utils.validators import validate_file_size, validate_file_type


logger = setup_logger(__name__)


class S3Service:
    """Service for S3 operations"""
    
    def __init__(self):
        """Initialize S3 client"""
        self.s3_client = boto3.client(
            's3',
            region_name=settings.aws_region,
            endpoint_url=settings.aws_endpoint_url,  # For LocalStack development
        )
        self.bucket = settings.s3_bucket_name
    
    def generate_presigned_upload_url(
        self,
        document_id: str,
        filename: str,
        file_size: int,
        mime_type: str,
    ) -> tuple[str, str]:
        """
        Generate presigned URL for file upload
        
        Returns: (presigned_url, s3_key)
        """
        validate_file_size(file_size)
        validate_file_type(mime_type)
        
        # Generate S3 key
        version_id = str(uuid.uuid4())
        s3_key = f"documents/{document_id}/{version_id}/{filename}"
        
        try:
            presigned_url = self.s3_client.generate_presigned_url(
                'put_object',
                Params={
                    'Bucket': self.bucket,
                    'Key': s3_key,
                    'ContentType': mime_type,
                    'ServerSideEncryption': settings.s3_encryption_type,
                },
                ExpiresIn=settings.s3_presigned_url_expiration,
            )
            logger.info(f"Generated presigned upload URL for {document_id}")
            return presigned_url, s3_key
        except ClientError as e:
            logger.error(f"Failed to generate presigned URL: {str(e)}")
            raise S3Exception(f"Failed to generate presigned URL: {str(e)}")
    
    def generate_presigned_download_url(
        self,
        s3_key: str,
        expiration: int = 3600,
    ) -> str:
        """Generate presigned URL for file download"""
        try:
            presigned_url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket,
                    'Key': s3_key,
                },
                ExpiresIn=expiration,
            )
            logger.info(f"Generated presigned download URL for {s3_key}")
            return presigned_url
        except ClientError as e:
            logger.error(f"Failed to generate presigned download URL: {str(e)}")
            raise S3Exception(f"Failed to generate presigned URL: {str(e)}")
    
    def delete_file(self, s3_key: str) -> None:
        """Delete file from S3"""
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket,
                Key=s3_key,
            )
            logger.info(f"Deleted file from S3: {s3_key}")
        except ClientError as e:
            logger.error(f"Failed to delete file from S3: {str(e)}")
            raise S3Exception(f"Failed to delete file: {str(e)}")
    
    def get_object_metadata(self, s3_key: str) -> dict:
        """Get object metadata from S3"""
        try:
            response = self.s3_client.head_object(
                Bucket=self.bucket,
                Key=s3_key,
            )
            return {
                'size': response['ContentLength'],
                'content_type': response['ContentType'],
                'last_modified': response['LastModified'],
                'etag': response['ETag'],
            }
        except ClientError as e:
            logger.error(f"Failed to get object metadata: {str(e)}")
            raise S3Exception(f"Failed to get object metadata: {str(e)}")
    
    def copy_object(self, source_key: str, dest_key: str) -> None:
        """Copy object in S3"""
        try:
            copy_source = {
                'Bucket': self.bucket,
                'Key': source_key,
            }
            self.s3_client.copy_object(
                CopySource=copy_source,
                Bucket=self.bucket,
                Key=dest_key,
                ServerSideEncryption=settings.s3_encryption_type,
            )
            logger.info(f"Copied S3 object from {source_key} to {dest_key}")
        except ClientError as e:
            logger.error(f"Failed to copy object: {str(e)}")
            raise S3Exception(f"Failed to copy object: {str(e)}")
    
    def list_objects(self, prefix: str, max_keys: int = 100) -> list:
        """List objects in S3 with given prefix"""
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket,
                Prefix=prefix,
                MaxKeys=max_keys,
            )
            
            objects = []
            if 'Contents' in response:
                objects = [
                    {
                        'key': obj['Key'],
                        'size': obj['Size'],
                        'modified': obj['LastModified'],
                    }
                    for obj in response['Contents']
                ]
            
            logger.info(f"Listed {len(objects)} objects with prefix {prefix}")
            return objects
        except ClientError as e:
            logger.error(f"Failed to list objects: {str(e)}")
            raise S3Exception(f"Failed to list objects: {str(e)}")


# Singleton instance
s3_service = S3Service()
