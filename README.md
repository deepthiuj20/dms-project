# Production-Ready Document Management System

A comprehensive document management system built with Angular 18, FastAPI, AWS Lambda, and enterprise-grade security features.

## 📋 Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Angular 18)                     │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  NgRx State Management | Angular Material UI         │   │
│  │  JWT Authentication | Role-Based Access Control      │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────┘
                             │ HTTPS
                ┌────────────▼────────────┐
                │   API Gateway           │
                │ (REST Endpoints)        │
                └────────────┬────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
   ┌─────────┐          ┌─────────┐         ┌──────────┐
   │ Lambda  │          │ Lambda  │         │ Cognito  │
   │ Auth    │          │ Document│         │ User Pool│
   │ Service │          │ Service │         │          │
   └─────────┘          └────┬────┘         └──────────┘
                             │
                ┌────────────┬┴────────────┐
                │            │            │
                ▼            ▼            ▼
            ┌───────┐   ┌─────────┐  ┌──────────┐
            │   S3  │   │DynamoDB │  │CloudWatch│
            │(Files)│   │(Metadata)  │(Logging) │
            └───────┘   └─────────┘  └──────────┘
```

## 🚀 Features

- ✅ User Management: Registration, login, JWT tokens via Cognito
- ✅ Role-Based Access Control: Admin and User roles
- ✅ File Upload: S3 presigned URLs for secure uploads
- ✅ Metadata Management: DynamoDB for scalable storage
- ✅ Search: Full-text search capabilities
- ✅ Versioning: Track file versions and modifications
- ✅ Audit Logging: Complete audit trail
- ✅ Pagination: Efficient data loading
- ✅ Security: End-to-end encryption, CORS, input validation
- ✅ Monitoring: CloudWatch integration

## 📁 Project Structure

```
dms-project/
├── frontend/                    # Angular 18 application
├── backend/                     # Python FastAPI application
├── infrastructure/              # AWS SAM templates
├── pipeline/                    # CI/CD configuration
├── docs/                        # Documentation
└── README.md
```

## 🛠️ Technology Stack

- **Frontend**: Angular 18, Angular Material, NgRx, RxJS, TypeScript
- **Backend**: Python 3.11+, FastAPI, Pydantic, Boto3
- **Infrastructure**: AWS Lambda, API Gateway, S3, DynamoDB, Cognito, SAM

## 🚀 Quick Start

```bash
# Frontend
cd frontend && npm install && ng serve

# Backend
cd backend && python -m venv venv && pip install -r requirements.txt

# Deploy
cd infrastructure && sam build && sam deploy --guided
```

## 📚 Documentation

- [Architecture & Design](ARCHITECTURE.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Security Best Practices](docs/SECURITY.md)
- [API Reference](docs/API.md)
- [Testing Strategy](docs/TESTING.md)

## 🔐 Security Features

- JWT token validation
- Cognito user pool authentication
- Role-based access control (RBAC)
- S3 presigned URLs with expiration
- DynamoDB encryption at rest
- CloudWatch audit logging
- Input validation and sanitization
- CORS configuration

---

**Built with ❤️ for enterprise document management**
