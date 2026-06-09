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

## Data Models

### DynamoDB Tables

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
```

**File Versions Table**
```
PK: document_id#version_id
SK: created_at
Attributes:
  - version_id (UUID)
  - document_id (UUID)
  - s3_key (versioned object)
  - created_by (user email)
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
  - resource_type (DOCUMENT, VERSION)
  - resource_id
  - timestamp
  - ip_address
  - status (SUCCESS, FAILURE)
  - details (JSON)
```

## Authentication & Authorization

### Cognito Flow
1. User registers/logs in via Cognito
2. Cognito returns JWT token
3. Client stores token
4. All requests include token in Authorization header
5. API Gateway validates token
6. Lambda extracts user_id and roles
7. RBAC decisions based on roles

### Roles
- **Admin**: Full access, user management, audit logs
- **User**: Document management (own documents only)

---

See implementation guides for detailed setup instructions.
