"""
DynamoDB service for database operations
"""
import boto3
import uuid
from typing import List, Dict, Optional
from datetime import datetime
from decimal import Decimal
from botocore.exceptions import ClientError

from app.utils.config import settings
from app.utils.logger import setup_logger
from app.utils.exceptions import DynamoDBException


logger = setup_logger(__name__)


class DynamoDBService:
    """Service for DynamoDB operations"""
    
    def __init__(self):
        """Initialize DynamoDB client"""
        self.dynamodb = boto3.resource(
            'dynamodb',
            region_name=settings.aws_region,
            endpoint_url=settings.aws_endpoint_url,  # For LocalStack
        )
        self.documents_table = self.dynamodb.Table(settings.dynamodb_documents_table)
        self.versions_table = self.dynamodb.Table(settings.dynamodb_versions_table)
        self.audit_log_table = self.dynamodb.Table(settings.dynamodb_audit_log_table)
    
    # ==================== Documents Operations ====================
    
    def create_document(
        self,
        user_id: str,
        document_id: str,
        filename: str,
        file_size: int,
        mime_type: str,
        s3_key: str,
        email: str,
        tags: List[str] = None,
    ) -> Dict:
        """Create document metadata in DynamoDB"""
        try:
            timestamp = datetime.utcnow()
            
            item = {
                'user_id': user_id,
                'document_id': document_id,
                'filename': filename,
                'file_size': file_size,
                'mime_type': mime_type,
                's3_key': s3_key,
                'created_at': timestamp.isoformat(),
                'updated_at': timestamp.isoformat(),
                'created_by': email,
                'status': 'active',
                'tags': tags or [],
                'version_count': 1,
            }
            
            self.documents_table.put_item(Item=item)
            logger.info(f"Created document {document_id} for user {user_id}")
            return item
        except ClientError as e:
            logger.error(f"Failed to create document: {str(e)}")
            raise DynamoDBException(f"Failed to create document: {str(e)}")
    
    def get_document(self, user_id: str, document_id: str) -> Optional[Dict]:
        """Get document by ID"""
        try:
            response = self.documents_table.get_item(
                Key={
                    'user_id': user_id,
                    'document_id': document_id,
                }
            )
            return response.get('Item')
        except ClientError as e:
            logger.error(f"Failed to get document: {str(e)}")
            raise DynamoDBException(f"Failed to get document: {str(e)}")
    
    def list_documents(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None,
    ) -> tuple[List[Dict], int]:
        """List documents for user with pagination"""
        try:
            filter_expression = None
            expression_values = {':user_id': user_id}
            
            if status:
                filter_expression = 'attribute_exists(#status) AND #status = :status'
                expression_values[':status'] = status
            
            query_kwargs = {
                'KeyConditionExpression': 'user_id = :user_id',
                'ExpressionAttributeValues': expression_values,
                'ScanIndexForward': False,  # Most recent first
                'Limit': limit + skip,  # Fetch extra to account for skip
            }
            
            if filter_expression:
                query_kwargs['FilterExpression'] = filter_expression
                query_kwargs['ExpressionAttributeNames'] = {'#status': 'status'}
            
            response = self.documents_table.query(**query_kwargs)
            
            items = response.get('Items', [])[skip:skip + limit]
            total = response.get('Count', 0)
            
            logger.info(f"Listed {len(items)} documents for user {user_id}")
            return items, total
        except ClientError as e:
            logger.error(f"Failed to list documents: {str(e)}")
            raise DynamoDBException(f"Failed to list documents: {str(e)}")
    
    def update_document(
        self,
        user_id: str,
        document_id: str,
        updates: Dict,
    ) -> Dict:
        """Update document metadata"""
        try:
            updates['updated_at'] = datetime.utcnow().isoformat()
            
            update_expression = "SET " + ", ".join(
                [f"{key} = :{key}" for key in updates.keys()]
            )
            expression_values = {f":{key}": value for key, value in updates.items()}
            
            response = self.documents_table.update_item(
                Key={
                    'user_id': user_id,
                    'document_id': document_id,
                },
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_values,
                ReturnValues='ALL_NEW',
            )
            
            logger.info(f"Updated document {document_id}")
            return response.get('Attributes', {})
        except ClientError as e:
            logger.error(f"Failed to update document: {str(e)}")
            raise DynamoDBException(f"Failed to update document: {str(e)}")
    
    def delete_document(self, user_id: str, document_id: str) -> None:
        """Delete document (soft delete - mark as deleted)"""
        try:
            self.update_document(
                user_id,
                document_id,
                {'status': 'deleted'},
            )
            logger.info(f"Deleted document {document_id}")
        except ClientError as e:
            logger.error(f"Failed to delete document: {str(e)}")
            raise DynamoDBException(f"Failed to delete document: {str(e)}")
    
    # ==================== Versions Operations ====================
    
    def create_version(
        self,
        document_id: str,
        version_id: str,
        s3_key: str,
        file_size: int,
        email: str,
        change_description: Optional[str] = None,
    ) -> Dict:
        """Create document version"""
        try:
            timestamp = datetime.utcnow()
            
            item = {
                'document_id': document_id,
                'version_id': version_id,
                's3_key': s3_key,
                'file_size': file_size,
                'created_by': email,
                'created_at': timestamp.isoformat(),
                'change_description': change_description or 'Version created',
            }
            
            self.versions_table.put_item(Item=item)
            logger.info(f"Created version {version_id} for document {document_id}")
            return item
        except ClientError as e:
            logger.error(f"Failed to create version: {str(e)}")
            raise DynamoDBException(f"Failed to create version: {str(e)}")
    
    def get_versions(
        self,
        document_id: str,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[List[Dict], int]:
        """Get document versions"""
        try:
            response = self.versions_table.query(
                KeyConditionExpression='document_id = :doc_id',
                ExpressionAttributeValues={':doc_id': document_id},
                ScanIndexForward=False,  # Most recent first
                Limit=limit + skip,
            )
            
            items = response.get('Items', [])[skip:skip + limit]
            total = response.get('Count', 0)
            
            logger.info(f"Retrieved {len(items)} versions for document {document_id}")
            return items, total
        except ClientError as e:
            logger.error(f"Failed to get versions: {str(e)}")
            raise DynamoDBException(f"Failed to get versions: {str(e)}")
    
    # ==================== Audit Log Operations ====================
    
    def log_audit_event(
        self,
        user_id: str,
        action: str,
        resource_type: str,
        resource_id: str,
        ip_address: str,
        status: str = "SUCCESS",
        details: Optional[Dict] = None,
    ) -> None:
        """Log audit event"""
        try:
            timestamp = datetime.utcnow()
            event_id = str(uuid.uuid4())
            
            item = {
                'user_id': user_id,
                'event_id': event_id,
                'action': action,
                'resource_type': resource_type,
                'resource_id': resource_id,
                'timestamp': timestamp.isoformat(),
                'ip_address': ip_address,
                'status': status,
                'details': details or {},
            }
            
            self.audit_log_table.put_item(Item=item)
            logger.info(f"Logged audit event: {action} on {resource_type}")
        except ClientError as e:
            logger.error(f"Failed to log audit event: {str(e)}")
            # Don't raise exception for audit logging failures
    
    def get_audit_logs(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[List[Dict], int]:
        """Get audit logs for user"""
        try:
            response = self.audit_log_table.query(
                KeyConditionExpression='user_id = :user_id',
                ExpressionAttributeValues={':user_id': user_id},
                ScanIndexForward=False,  # Most recent first
                Limit=limit + skip,
            )
            
            items = response.get('Items', [])[skip:skip + limit]
            total = response.get('Count', 0)
            
            logger.info(f"Retrieved {len(items)} audit logs for user {user_id}")
            return items, total
        except ClientError as e:
            logger.error(f"Failed to get audit logs: {str(e)}")
            raise DynamoDBException(f"Failed to get audit logs: {str(e)}")


# Singleton instance
dynamodb_service = DynamoDBService()
