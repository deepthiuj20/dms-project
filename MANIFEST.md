version: 0.1

frontend:
  - name: package.json
    path: frontend/package.json
    
  - name: angular.json
    path: frontend/angular.json
    
  - name: tsconfig.json
    path: frontend/tsconfig.json

backend:
  - name: requirements.txt
    path: backend/requirements.txt
    
  - name: Dockerfile
    path: backend/Dockerfile
    
  - name: main.py
    path: backend/app/main.py

infrastructure:
  - name: template.yaml
    path: infrastructure/template.yaml
    
  - name: parameters.json
    path: infrastructure/parameters.json

pipeline:
  - name: build.yml
    path: .github/workflows/build.yml
    
  - name: deploy.yml
    path: .github/workflows/deploy.yml

docs:
  - name: ARCHITECTURE.md
    path: docs/ARCHITECTURE.md
    
  - name: DEPLOYMENT.md
    path: docs/DEPLOYMENT.md
    
  - name: SECURITY.md
    path: docs/SECURITY.md
