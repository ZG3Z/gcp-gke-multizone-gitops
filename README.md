# Multi-Zone GKE Production Stack

[![Infrastructure](https://img.shields.io/badge/infrastructure-terraform-623CE4)](https://www.terraform.io/)
[![Platform](https://img.shields.io/badge/platform-GKE-4285F4)](https://cloud.google.com/kubernetes-engine)
[![CI/CD](https://img.shields.io/badge/CI%2FCD-Cloud%20Build-4285F4)](https://cloud.google.com/build)

Production-ready FastAPI application deployed on Google Kubernetes Engine with full GitOps workflow, managed database, and comprehensive monitoring.

## Project Overview

Enterprise-grade infrastructure on Google Cloud Platform demonstrating:

- **Multi-zone Kubernetes cluster** for high availability across 3 availability zones
- **Automated CI/CD pipeline** with Cloud Build triggering on git push
- **Managed PostgreSQL database** with private networking and regional HA
- **Security best practices** using Workload Identity and Secret Manager
- **Real-time monitoring** with Cloud Monitoring dashboards
- **Infrastructure as Code** using Terraform for reproducible deployments

## Tech Stack

### Infrastructure
- **Google Kubernetes Engine** - Regional cluster across 3 zones
- **Terraform** - Infrastructure as Code
- **Cloud SQL PostgreSQL** - Managed database with automatic backups
- **Cloud Build** - Automated CI/CD pipeline
- **Artifact Registry** - Private container registry

### Application
- **Python 3.11** - Application runtime
- **FastAPI** - Modern web framework
- **SQLAlchemy** - Database ORM
- **Uvicorn** - ASGI web server
- **PostgreSQL** - Relational database

### Security
- **Workload Identity** - Secure pod-to-GCP authentication
- **Secret Manager** - Encrypted secrets storage
- **Private IP** - Database isolated from internet
- **Custom Service Accounts** - Least privilege access control

### Observability
- **Cloud Monitoring** - Metrics collection and dashboards
- **Cloud Logging** - Centralized log aggregation
- **Structured Logging** - JSON-formatted application logs

## Repository Structure
```
.
├── app/
│   ├── src/
│   │   ├── main.py              # FastAPI application
│   │   ├── database.py          # SQLAlchemy models and connection
│   │   └── secrets.py           # Secret Manager integration
│   ├── requirements.txt         # Python dependencies
│   └── Dockerfile               # Container image build
│
├── terraform/
│   ├── main.tf                 # API enablement
│   ├── versions.tf             # Provider configuration
│   ├── variables.tf            # Input variables
│   ├── artifact-registry.tf    # Container registry
│   ├── cloud-build.tf          # CI/CD pipeline
│   ├── cloud-sql.tf            # PostgreSQL database
│   ├── gke.tf                  # Kubernetes cluster
│   ├── iam.tf                  # Service accounts and permissions
│   ├── monitoring.tf           # Monitoring dashboard
│   ├── networking.tf           # VPC and firewall
│   └── secrets.tf              # Secret Manager
│
├── kubernetes/
│   ├── rbac.yaml               # Cluster roles and bindings
│   ├── deployment.yaml         # Application deployment
│   ├── service.yaml            # LoadBalancer service
│   ├── serviceaccount.yaml     # Workload Identity binding
│   └── hpa.yaml                # Horizontal Pod Autoscaler
│
├── docs/
│   ├── ARCHITECTURE.md         # System design and decisions
│   └── COSTS.md                # Cost analysis 
│
├── .gitignore
├── cloudbuild.yaml            # Build pipeline configuration
└── README.md
```

## Prerequisites

**Required:**
- Google Cloud Platform account with billing enabled
- `gcloud` CLI >= 400.0.0
- `terraform` >= 1.6.0
- `kubectl` >= 1.28.0
- GitHub account for CI/CD integration

**GCP APIs** (automatically enabled by Terraform):
- Compute Engine API
- Kubernetes Engine API
- Cloud SQL Admin API
- Artifact Registry API
- Cloud Build API
- Secret Manager API
- Cloud Logging API
- Cloud Monitoring API

## Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/ZG3Z/gcp-gke-multizone-gitops.git
cd gcp-gke-multizone-gitops
```

### 2. Configure GCP Authentication
```bash
# Set project ID
export PROJECT_ID="your-project-id"

# Authenticate with Google Cloud
gcloud auth login
gcloud auth application-default login

# Set active project
gcloud config set project $PROJECT_ID
```

### 3. Configure Terraform Variables

Create `terraform/terraform.tfvars`:
```hcl
project_id    = "your-project-id"
region        = "us-east1"
zones         = ["us-east1-b", "us-east1-c", "us-east1-d"]

network_name         = "gke-network"
subnet_name          = "gke-subnet"
subnet_cidr          = "10.0.0.0/20"
pods_cidr_name       = "pods"
pods_cidr            = "10.4.0.0/14"
services_cidr_name   = "services"
services_cidr        = "10.8.0.0/20"

cluster_name         = "multizone-cluster"
node_machine_type    = "e2-standard-2"
node_disk_size_gb    = 50
node_count_per_zone  = 2
min_node_count       = 1
max_node_count       = 5

artifact_registry_repository = "app-images"

github_owner = "your-github-username"
github_repo  = "gcp-gke-multizone-gitops"

labels = {
  project     = "gcp-gke-multizone"
  managed_by  = "terraform"
  environment = "prod"
}
```

### 4. Deploy Infrastructure
```bash
cd terraform

# Initialize Terraform
terraform init

# Review planned changes
terraform plan

# Deploy infrastructure (15-20 minutes)
terraform apply
```



### 5. Configure kubectl
```bash
# Download cluster credentials
gcloud container clusters get-credentials multizone-cluster \
  --region us-east1 \
  --project $PROJECT_ID

# Verify cluster access
kubectl get nodes
```


### 6. Deploy Application

**Option A: Manual Deployment**
```bash
kubectl apply -f kubernetes/serviceaccount.yaml
kubectl apply -f kubernetes/setup/rbac.yaml
kubectl apply -f kubernetes/deployment.yaml
kubectl apply -f kubernetes/service.yaml
kubectl apply -f kubernetes/hpa.yaml

# Wait for pods to be ready
kubectl get pods -w
```

**Option B: Automated via CI/CD**

1. Connect GitHub repository (first time):
   - Navigate to: https://console.cloud.google.com/cloud-build/triggers
   - Click "Connect Repository"
   - Authorize GitHub and select: `ZG3Z/gcp-gke-multizone-gitops`

2. Deploy via git push:
```bash
git add .
git commit -m "Deploy application"
git push origin main

# Monitor build progress
gcloud builds log $(gcloud builds list --limit=1 --format="value(id)") --stream
```

### 7. Access Application
```bash
# Get LoadBalancer external IP
EXTERNAL_IP=$(kubectl get svc fastapi-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
echo "Application: http://$EXTERNAL_IP"

# Test endpoints
curl http://$EXTERNAL_IP/
curl http://$EXTERNAL_IP/health
curl http://$EXTERNAL_IP/api/data
```

## API Documentation

### Endpoints

**Health Check**
```bash
GET /health
Response: {"status":"ok"}
```

**Application Info**
```bash
GET /
Response: {
  "message": "FastAPI + Cloud SQL + Secret Manager + GKE",
  "hostname": "fastapi-app-xyz",
  "pod": "fastapi-app-xyz",
  "zone": "us-east1-b",
  "database": "postgresql"
}
```

**List Items**
```bash
GET /api/data
Response: {"count": 0, "items": []}
```

**Create Item**
```bash
POST /api/data
Content-Type: application/json

{
  "id": "item1",
  "name": "Test Item",
  "value": 123,
  "description": "Optional description"
}

Response: {"message": "created", "item": {"id": "item1", "name": "Test Item"}}
```

**Get Item**
```bash
GET /api/data/{item_id}
Response: {
  "id": "item1",
  "name": "Test Item",
  "value": 123,
  "created_at": "2025-01-15T10:30:00"
}
```

**Delete Item**
```bash
DELETE /api/data/{item_id}
Response: {"message": "deleted"}
```


## Monitoring

### Dashboard
```bash
https://console.cloud.google.com/monitoring/dashboards
```

Metrics displayed:
- Pod CPU Usage
- Pod Memory Usage
- Running Pods Count
- Network Traffic

### Logs
```bash
# Stream deployment logs
kubectl logs -f deployment/fastapi-app

# View all pod logs
kubectl logs -l app=fastapi-app --tail=100

# Follow specific pod
kubectl logs -f POD_NAME

# Or visit:
https://console.cloud.google.com/logs/query
```

## Scaling

### Test Autoscaling
```bash
EXTERNAL_IP=$(kubectl get svc fastapi-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# Generate load
for i in {1..1000}; do
  curl -s http://$EXTERNAL_IP/ > /dev/null &
done

# Watch scaling
kubectl get hpa -w
kubectl get pods -w
```

## Documentation

For detailed information, see:

- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - System design, component details, and architectural decisions
- **[COSTS.md](docs/COSTS.md)** - Detailed cost breakdown and optimization guide

## Troubleshooting

### Pods Not Starting
```bash
kubectl describe pod POD_NAME
kubectl get events --sort-by='.lastTimestamp'
kubectl logs POD_NAME
```

### Database Connection
```bash
# Verify instance
gcloud sql instances describe INSTANCE_NAME

# Check environment variables
kubectl exec -it POD_NAME -- env | grep DB_

# Test connectivity
kubectl exec -it POD_NAME -- nc -zv 10.20.0.2 5432
```

### CI/CD Pipeline
```bash
# List builds
gcloud builds list --limit=5

# View logs
gcloud builds log BUILD_ID

# Check permissions
gcloud projects get-iam-policy PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:cloud-build-sa@"
```

### Authentication
```bash
# Re-authenticate
gcloud auth login
gcloud auth application-default login

# Verify account
gcloud auth list

# Check project
gcloud config get-value project
```

## Cleanup

### Destroy Infrastructure
```bash
cd terraform
terraform destroy
```

### Delete Application Only
```bash
kubectl delete -f kubernetes/
```
