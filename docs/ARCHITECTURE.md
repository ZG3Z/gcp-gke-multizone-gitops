# System Architecture

This document describes the technical architecture and design rationale for the multi-zone GKE production stack.

## Overview

This project implements a production-grade, highly available FastAPI application on Google Kubernetes Engine with complete CI/CD automation, managed database, and comprehensive observability.

**Key Characteristics:**
- Multi-zone deployment for high availability
- Automated deployments via GitOps workflow
- Private database networking
- Security through Workload Identity
- Horizontal autoscaling
- Zero-downtime updates

## Architecture Diagram
```
┌─────────────────────────────────────────────────────────────┐
│                  Google Cloud Platform                      │
│                                                             │
│  ┌──────────────┐                                           │
│  │   GitHub     │  Push to main branch                      │
│  │  Repository  │────────┐                                  │
│  └──────────────┘        │                                  │
│                          ▼                                  │
│                   ┌─────────────┐                           │
│                   │Cloud Build  │                           │
│                   │   CI/CD     │                           │
│                   └──────┬──────┘                           │
│                          │                                  │
│                          ▼                                  │
│                   ┌─────────────┐                           │
│                   │  Artifact   │                           │
│                   │  Registry   │                           │
│                   └──────┬──────┘                           │
│                          │                                  │
│                          ▼                                  │
│    ┌─────────────────────────────────────────────┐          │
│    │   Google Kubernetes Engine (Regional)       │          │
│    │                                             │          │
│    │  ┌──────────┐  ┌──────────┐  ┌──────────┐   │          │
│    │  │  Zone A  │  │  Zone B  │  │  Zone C  │   │          │
│    │  │  2 Nodes │  │  2 Nodes │  │  2 Nodes │   │          │
│    │  │  Pods    │  │  Pods    │  │  Pods    │   │          │
│    │  └────┬─────┘  └────┬─────┘  └────┬─────┘   │          │
│    │       └─────────────┴─────────────┘         │          │
│    │                     │                       │          │
│    │          ┌──────────▼──────────┐            │          │
│    │          │   LoadBalancer      │            │          │
│    │          │   External IP       │            │          │
│    │          └─────────────────────┘            │          │
│    └─────────────────────────────────────────────┘          │
│                          │                                  │
│                          │ Private IP                       │
│                          ▼                                  │
│                   ┌─────────────┐                           │
│                   │  Cloud SQL  │                           │
│                   │ PostgreSQL  │                           │
│                   │ Regional HA │                           │
│                   └─────────────┘                           │
│                                                             │
│      ┌──────────┐   ┌──────────┐   ┌──────────┐             │
│      │ Secret   │   │  Cloud   │   │  Cloud   │             │
│      │ Manager  │   │Monitoring│   │ Logging  │             │
│      └──────────┘   └──────────┘   └──────────┘             │
└─────────────────────────────────────────────────────────────┘
```

## Core Design Decisions

### 1. Regional Multi-Zone Kubernetes Cluster

**What was chosen:**
- Regional GKE cluster spanning 3 availability zones
- 6 nodes total: 2 nodes per zone
- e2-standard-2 machine type (2 vCPU, 8GB RAM)

**Why this design:**

**High Availability:** The regional cluster architecture provides resilience against zone failures. If an entire availability zone becomes unavailable, the application continues running on nodes in the remaining two zones. This design targets 99.95% availability compared to 99.5% for single-zone deployments.

**Cost-Performance Balance:** The e2-standard-2 machine type provides sufficient resources for the application workload while remaining cost-effective. 

### 2. Application Deployment Strategy

**What was chosen:**
- 3 minimum replicas (1 per zone baseline)
- Rolling update deployment strategy
- Readiness and liveness probes
- Resource requests and limits defined

**Why this design:**

**Zero-Downtime Deployments:** Rolling updates ensure continuous availability during deployments. The deployment creates new pods with updated code before terminating old pods. With `maxUnavailable: 0`, at least 3 pods always remain available to serve traffic.

**Minimum 3 Replicas:** Three replicas provide redundancy and enable safe rolling updates. During an update with 3 replicas, at least 2 pods always serve traffic while the third updates.

**Health Checking:** Liveness probes detect and restart crashed pods automatically. Readiness probes ensure pods only receive traffic after successful startup. This prevents routing requests to pods that aren't ready to handle them.

**Resource Guarantees:** Defined resource requests ensure pods get necessary CPU and memory. Resource limits prevent pods from consuming excessive resources and affecting other workloads on the node.

### 3. Horizontal Pod Autoscaler (HPA)

**What was chosen:**
- CPU-based autoscaling
- 3 minimum replicas, 10 maximum replicas
- 70% CPU utilization target

**Why this design:**

**Automatic Capacity Management:** The HPA monitors CPU utilization and automatically adjusts pod count. When traffic increases and CPU usage exceeds 70%, new pods are created. When traffic decreases, pods are removed down to the minimum of 3.

**CPU as Scaling Metric:** CPU utilization correlates well with request load for this application. A 70% target provides headroom for traffic spikes while avoiding over-provisioning.

**Scaling Boundaries:** The 3-pod minimum maintains high availability. The 10-pod maximum prevents runaway scaling and controls costs while providing 3x capacity for traffic spikes.


### 4. Cloud SQL PostgreSQL with Regional HA

**What was chosen:**
- Managed PostgreSQL 15
- db-f1-micro instance tier
- Regional high availability configuration
- Private IP networking only
- Automated daily backups with 7-day retention

**Why this design:**

**Managed Service Benefits:** Cloud SQL eliminates operational overhead of database management. Google handles patching, backups, replication, and monitoring. 

**Regional HA Architecture:** The regional configuration maintains a standby replica in a different zone. If the primary instance fails, automatic failover. This provides database-level high availability matching the application tier.

**Private IP Security:** Using only private IP addresses ensures the database is not exposed to the public internet. The database is only accessible from within the VPC through VPC peering, significantly reducing attack surface.

**Automated Backup Strategy:** Daily automated backups with 7-day retention provide point-in-time recovery capability. Combined with transaction logs, the database can be restored to any point within the last 7 days, enabling recovery from data corruption or accidental deletions.

**Right-Sized Capacity:** The db-f1-micro tier provides adequate capacity for this workload while remaining cost-effective. The instance can be easily upgraded to larger tiers as requirements grow without architectural changes.

### 5. Private Networking Architecture

**What was chosen:**
- Custom VPC with separate CIDR ranges for nodes, pods, and services
- Private subnet for GKE nodes
- Secondary IP ranges for pod and service networks
- VPC peering to Cloud SQL
- Private Google Access enabled

**Why this design:**

**Network Isolation:** The custom VPC isolates this infrastructure from other projects and the default network. Separate CIDR ranges for nodes, pods, and services prevent IP conflicts and enable fine-grained network policies.

**Scalable IP Addressing:** The pod CIDR (10.4.0.0/14) provides 262,144 IP addresses, supporting significant cluster growth. The large address space prevents IP exhaustion as the cluster scales.

**Secure Database Communication:** VPC peering creates a private connection between the GKE network and Cloud SQL. Database traffic never traverses the public internet, improving both security and latency.

**Private Google Access:** Nodes and pods can access Google Cloud APIs without requiring external IP addresses. This maintains security while enabling access to services like Secret Manager, Cloud Logging, and Cloud Monitoring.

**Load Balancer Integration:** The external load balancer provides a single public entry point while keeping the underlying infrastructure on private networks. Only the load balancer has a public IP address.

### 6. Workload Identity for Authentication

**What was chosen:**
- Workload Identity enabled on the cluster
- Kubernetes service account annotated with Google service account
- IAM binding between Kubernetes and Google service accounts
- No service account key files

**Why this design:**

**Elimination of Static Credentials:** Workload Identity removes the need for service account key JSON files. Static keys present security risks through potential exposure, difficult rotation, and broad permissions.

**Automatic Credential Management:** Pods automatically receive short-lived tokens that are cryptographically bound to their Kubernetes identity. Tokens are automatically refreshed, eliminating manual rotation.

**Granular Permissions:** Each application workload has its own Google service account with specific permissions. The FastAPI application service account only has permission to access database secrets, following the principle of least privilege.

**Audit Trail:** API calls made by pods are clearly attributed to their service account, providing transparency in logs and audit trails. This enables tracking which pod made which API calls.

**Cloud-Native Best Practice:** Workload Identity is Google's recommended authentication mechanism for GKE workloads, providing the highest security standard for pod-to-GCP authentication.

### 7. Secret Manager for Credentials

**What was chosen:**
- Database password stored in Secret Manager
- Application retrieves secret at startup via API
- Automatic replication across regions
- Version control for secrets

**Why this design:**

**Centralized Secret Storage:** Secret Manager provides a single, secure location for sensitive data. Secrets are encrypted at rest and in transit, with access controlled through IAM.

**No Secrets in Code or Configuration:** The database password never appears in source code, Kubernetes manifests, or environment variables in plaintext. The application retrieves it programmatically at startup.

**Access Control:** IAM policies control which service accounts can access which secrets. The application's service account has read-only access to only the database password secret.

**Audit and Versioning:** Secret Manager tracks all access attempts and maintains versions of secrets. This enables auditing who accessed secrets and when, plus the ability to roll back to previous secret values if needed.

**Rotation Support:** Secrets can be updated in Secret Manager without redeploying the application. A pod restart picks up the new value, enabling credential rotation without code changes.

### 8. CI/CD with Cloud Build

**What was chosen:**
- GitHub integration with Cloud Build
- Automated trigger on push to main branch
- Build, tag, push, and deploy in single pipeline
- Dedicated service account for builds

**Why this design:**

**GitOps Workflow:** Every deployment originates from a git commit. This creates a complete audit trail and enables easy rollback by reverting commits. The main branch always represents the deployed state.

**Automated Testing and Deployment:** The pipeline eliminates manual steps and potential human error. 

**Immutable Artifacts:** Each commit creates a uniquely tagged container image. Images are tagged with the git commit SHA, enabling exact version tracking and rollback to any previous version.

**Zero-Downtime Deployments:** The pipeline updates the Kubernetes deployment, which performs a rolling update. New pods are created and verified before old pods are terminated, maintaining continuous availability.

### 9. Monitoring and Observability

**What was chosen:**
- Cloud Monitoring dashboard with 4 key metrics
- Structured JSON logging to stdout
- Cloud Logging for log aggregation
- Application-level health checks

**Why this design:**

**Essential Metrics Focus:** The dashboard displays the minimum viable set of metrics needed to understand system health: CPU usage, memory usage, pod count, and network traffic. This prevents metric overload while covering critical indicators.

**Structured Logging:** JSON-formatted logs enable programmatic parsing and searching. Fields like `status_code` can be queried in Cloud Logging, making troubleshooting faster and more precise.

**Stdout for Logs:** Writing logs to stdout follows the twelve-factor app methodology. Kubernetes automatically captures and forwards these logs to Cloud Logging without requiring log shippers or agents.

**Health Endpoints:** The `/health` endpoint provides a simple HTTP-based mechanism for readiness and liveness checks. This standard pattern enables Kubernetes to automatically detect and recover from failures.


### 10. Container Image Build Strategy

**What was chosen:**
- Slim Python base image
- Images stored in Artifact Registry

**Why this design:**

**Slim Base Image:** Using `python:3.11-slim` instead of full Python image reduces attack surface and image size while including all necessary runtime components.

**Faster Deployments:** Smaller images pull faster from the registry, reducing pod startup time. This improves scaling responsiveness and deployment speed.

**Private Registry:** Artifact Registry provides a private, regional container registry. Images are stored close to the GKE cluster for fast pulls, and access is controlled through IAM.


## Design Principles Applied

### Immutability

All infrastructure is defined in code (Terraform). Container images are immutable and tagged by version. Changes are deployed as new resources rather than modifying existing ones.

### Automation

Manual operations are minimized. Deployments, scaling, healing, and backups all happen automatically.

### Defense in Depth

Multiple security layers provide redundancy: network isolation, workload identity, secret management, and RBAC all contribute to security.

### Observability

The system provides visibility into its behavior through metrics, logs, and health checks. Problems are detectable before they impact users.

### Fault Tolerance

The architecture anticipates and handles failures automatically. Single points of failure are eliminated through redundancy across zones.

### Cost Optimization

Automatic scaling ensures capacity matches demand. Managed services reduce operational overhead. Resource limits prevent waste.