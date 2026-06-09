# System Architecture

## High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                                 │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │                    Angular 18 SPA                            │ │
│  │  ┌─────────────┐  ┌──────────────┐  ┌─────────────────────┐ │ │
│  │  │ Auth Module │  │ Document     │  │ Shared Services    │ │ │
│  │  │             │  │ Management   │  │ - HTTP Client      │ │ │
│  │  │ - Login     │  │ Module       │  │ - Auth Guard       │ │ │
│  │  │ - Register  │  │ - Upload     │  │ - Error Handler    │ │ │
│  │  │ - Token Mgmt│  │ - Search     │  │ - Logger           │ │ │
│  │  └─────────────┘  │ - Download   │  └─────────────────────┘ │ │
│  │                    │ - Delete     │                           │ │
│  │                    │ - Version    │                           │ │
│  │                    └──────────────┘                           │ │
│  │  ┌────────────────────────────────────────────────────────┐  │ │
│  │  │           NgRx Store (Global State)                   │  │ │
│  │  │  - Auth State     - Document State    - UI State      │  │ │
│  │  │  - Selectors      - Actions           - Effects       │  │ │
│  │  └────────────────────────────────────────────────────────┘  │ │
│  └───────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  │ HTTPS (TLS 1.2+)
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    AWS API GATEWAY (REST API)                       │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │  - CORS Configuration                                         │ │
│  │  - Request/Response Transformation                            │ │
│  │  - Rate Limiting                                              │ │
│  │  - Authorization (JWT Validation)                             │ │
│  │  - Logging & Monitoring                                       │ │
│  └───────────────────────────────────────────────────────────────┘ │
└────────────────┬────────────────────────────────────────────────────┘
                 │
    ┌────────────┼────────────┬──────────────┐
    │            │            │              │
    ▼            ▼            ▼              ▼
┌────────┐  ┌────────┐  ┌────────┐  ┌───────────┐
│ Lambda │  │ Lambda │  │ Lambda │  │ Cognito   │
│ Auth   │  │ Docs   │  │ Search │  │ User Pool │
│ Service│  │Service │  │Service │  │           │
└────────┘  └────────┘  └────────┘  └───────────┘
    │            │            │
    └────────────┼────────────┘
                 │
    ┌────────────┼─────────────┬──────────────┐
    │            │             │              │
    ▼            ▼             ▼              ▼
┌──────────┐ ┌──────────┐ ┌─────────┐ ┌────────────┐
│ DynamoDB │ │    S3    │ │Cognito  │ │CloudWatch  │
│ Metadata │ │  Files   │ │ Auth    │ │  Logs &    │
│ Versions │ │ Versions │ │         │ │  Metrics   │
│ Audit Log│ │          │ │         │ │            │
└──────────┘ └──────────┘ └─────────┘ └────────────┘
```

## Component Details

### Frontend Layer (Angular 18)

#### Authentication Module
- User registration and login forms
- Token management (storage, refresh)
- Auth guard for route protection
- Cognito integration

#### Document Management Module
- File upload with progress tracking
- File search and filtering
- Version management UI
- Download functionality
- Audit log viewer
- Pagination controls

#### Shared Services
- HTTP interceptor for JWT token injection
- Error handling and retry logic
- Logging service
- Notification service
- State management effects

#### NgRx State Management
```
Actions → Reducers → Store → Selectors → Components
        ↓
      Effects
        ↓
    Side Effects (HTTP calls, routing)
```

### API Gateway Layer

- Authorizer: JWT token validation
- CORS: Cross-origin request handling
- Rate limiting: DDoS protection
- Request logging: CloudWatch integration
- Response transformation

### Backend Layer (FastAPI on Lambda)

#### Auth Service Lambda
```
Endpoints:
POST   /auth/register       - User registration
POST   /auth/login          - User login
POST   /auth/refresh        - Token refresh
POST   /auth/logout         - Token revocation
GET    /auth/me             - Current user info
```

**Process Flow:**
1. Receive credentials
2. Validate with Cognito
3. Generate JWT token
4. Return token to client
5. Client stores token (localStorage/sessionStorage)

#### Document Service Lambda
```
Endpoints:
POST   /documents/upload      - Initiate upload
GET    /documents             - List documents (paginated)
GET    /documents/{id}        - Get document metadata
GET    /documents/{id}/versions - List versions
PUT    /documents/{id}        - Update metadata
DELETE /documents/{id}        - Delete document
GET    /documents/{id}/download - Get download URL
```

**Process Flow:**
1. Receive request with JWT token
2. Verify token and extract user_id
3. Check role-based permissions
4. Perform operation
5. Log audit event
6. Return response

### Data Layer

#### DynamoDB Tables

**Documents Table**
```
PK: user_id#document_id
SK: created_at
Attributes:
  - document_id (UUID)
  - user_id (Cognito sub)
  - filename
  - file_size
  - mime_type
  - s3_bucket
  - s3_key
  - created_at (ISO 8601)
  - updated_at (ISO 8601)
  - created_by (user email)
  - status (active, archived, deleted)
  - tags (list)
  - TTL (for soft deletes)
GSI: status-created_at (for filtering by status and date)
```

**File Versions Table**
```
PK: document_id#version_id
SK: created_at
Attributes:
  - version_id (UUID)
  - document_id (UUID)
  - s3_key (points to versioned S3 object)
  - created_by (user email)
  - created_at
  - change_description
  - file_size
```

**Audit Log Table**
```
PK: user_id#timestamp
SK: event_id
Attributes:
  - event_id (UUID)
  - user_id
  - action (UPLOAD, DOWNLOAD, DELETE, UPDATE)
  - resource_type (DOCUMENT, VERSION, USER)
  - resource_id
  - timestamp (ISO 8601)
  - ip_address
  - user_agent
  - status (SUCCESS, FAILURE)
  - details (JSON)
```

#### S3 Buckets

**Document Files Bucket**
```
Structure:
/{user_id}/{document_id}/{version_id}/filename

Configuration:
- Versioning: Enabled
- Encryption: AES-256
- Block Public Access: All
- Lifecycle Policy: Transition to Glacier after 90 days
- MFA Delete: Enabled (production)
```

#### Cognito User Pool

```
Attributes:
- email (required)
- given_name
- family_name
- phone_number
- custom:role (Admin/User)
- custom:department
- email_verified
- enabled

Policies:
- Password Policy: Min 12 chars, uppercase, lowercase, numbers, symbols
- MFA: Optional (recommended for Admin)
- Session Duration: 1 hour
```

### Security Architecture

#### Authentication Flow
```
User Input → Cognito Pool → JWT Token → Client Storage
                                         ↓
                          Token in Authorization Header
                                         ↓
                          API Gateway Authorizer
                                         ↓
                          Decode & Verify JWT
                                         ↓
                          Extract user_id, roles
                                         ↓
                          Pass to Lambda Function
```

#### Authorization Flow
```
Request with JWT → Extract roles from token
                         ↓
              Check role requirements
                         ↓
         RBAC Decision (Allow/Deny)
                         ↓
           Execute/Reject Operation
```

#### Encryption Strategy
- **In Transit**: TLS 1.2+ for all API calls
- **At Rest**: 
  - S3: AES-256 encryption
  - DynamoDB: AWS managed encryption
  - Cognito: Built-in encryption
- **Application Level**: Sensitive data encrypted before storage

### Monitoring & Logging

#### CloudWatch Integration

**Log Groups:**
- `/aws/lambda/auth-service`
- `/aws/lambda/document-service`
- `/aws/apigateway/api`

**Metrics:**
- Lambda invocations and duration
- Error rates by endpoint
- DynamoDB throughput and throttling
- S3 upload/download rates

**Alarms:**
- Lambda error rate > 1%
- DynamoDB throttling events
- API Gateway 5xx errors
- Unauthorized access attempts

#### Audit Logging

Every operation logged with:
- Timestamp
- User ID
- Action type
- Resource ID
- Result (success/failure)
- IP address
- User agent
- Request/response size

### Deployment Architecture

```
Local Dev → Git Push → GitHub Actions
                           ↓
                   ├─ Code Quality Checks
                   ├─ Unit Tests
                   ├─ Integration Tests
                   ├─ Security Scan
                           ↓
                    Build Artifacts
                           ↓
                    ├─ Frontend: S3 + CloudFront
                    ├─ Backend: Lambda Layers
                           ↓
                    Deploy to Dev/Staging
                           ↓
                    Smoke Tests
                           ↓
                    Manual Approval (Prod)
                           ↓
                    Deploy to Production
                           ↓
                    Health Checks
```

### Scalability Considerations

1. **Lambda**: Auto-scales with request volume
2. **DynamoDB**: On-demand billing for variable workloads
3. **S3**: Unlimited scalability with lifecycle policies
4. **Cognito**: Managed scaling for concurrent users
5. **Frontend**: Static hosting via CloudFront (CDN)

### Cost Optimization

1. **Compute**: Lambda pay-per-use model
2. **Storage**: S3 lifecycle policies to Glacier
3. **Data Transfer**: CloudFront caching
4. **Database**: DynamoDB on-demand vs provisioned capacity
5. **Monitoring**: Selective logging at DEBUG level only in dev

---

For implementation details, see the specific service documentation.
