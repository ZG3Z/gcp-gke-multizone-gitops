# Cost Analysis Report

This document provides a detailed breakdown of monthly costs for running the multi-zone GKE production stack in its current configuration.

## Monthly Cost Breakdown

### Infrastructure Configuration

**Region:** us-east1  
**Environment:** Production  
**Cluster Type:** GKE Standard  
**Architecture:** Multi-zone (3 availability zones)

### Detailed Cost Table

| Resource | Configuration | Unit Cost | Quantity | Monthly Cost |
|----------|--------------|-----------|----------|--------------|
| **Compute (GKE)** | | | | |
| GKE cluster management | Standard cluster fee | $0.10/hour | 730 hours | $73.00 |
| Worker nodes | e2-standard-2 (2 vCPU, 8GB RAM) | $48.54 | 6 nodes | $291.24 |
| Node storage | 50GB pd-standard per node | Included | 6 | $0 |
| **Database (Cloud SQL)** | | | | |
| PostgreSQL instance | db-f1-micro (0.6GB RAM, shared CPU) | $7.67 | 1 | $7.67 |
| Regional HA | Standby replica | $7.67 | 1 | $7.67 |
| Storage | 10GB SSD | $0.17/GB | 10GB | $1.70 |
| Automated backups | 7-day retention | ~$0.08/GB | ~10GB | $0.80 |
| **Networking** | | | | |
| Network Load Balancer | Forwarding rule | $0.025/hour | 730 hours | $18.25 |
| Data processed | Per GB | $0.008/GB | Variable | ~$5.00 |
| Egress traffic | Premium tier, same continent | $0.01/GB | ~100GB | $1.00 |
| **Artifact Registry** | | | | |
| Container storage | Docker images | $0.10/GB | ~10GB | $1.00 |
| **Cloud Build** | | | | |
| Build time | e2-standard-2 machine | $0.006/min | ~500 min/month | $3.00 |
| Build time discount | First 2,500 min/month free | -$0.006/min | -500 min | -$3.00 |
| **Monitoring & Logging** | | | | |
| Cloud Monitoring | Metric ingestion | $0 | <150MB (free tier) | $0 |
| Cloud Logging | Log ingestion | $0 | <50GB (free tier) | $0 |
| Dashboard | Custom dashboard | $0 | 1 | $0 |
| **Security** | | | | |
| Secret Manager | Active secret versions | $0.06 | 1 | $0.06 |
| Secret access operations | Per 10,000 operations | $0.03 | <10k | $0 |
| | | | | |
| **SUBTOTAL** | | | | **$407.39** |
| **Tax (estimated)** | Varies by location | ~5% | | **~$20.37** |
| **TOTAL** | | | | **~$427.76/month** |

### Annual Projection

| Period | Cost |
|--------|------|
| Monthly | $427.76 |
| Quarterly | $1,283.28 |
| Annual | $5,133.12 |

## Cost Distribution

### By Service

| Service | Monthly Cost | Percentage |
|---------|--------------|------------|
| GKE Compute Nodes | $291.24 | 71.5% |
| GKE Management Fee | $73.00 | 17.9% |
| Load Balancer | $23.25 | 5.7% |
| Cloud SQL | $17.84 | 4.4% |
| Network Egress | $1.00 | 0.2% |
| Artifact Registry | $1.00 | 0.2% |
| Cloud Build | $0.00 | 0.0% |
| Other (Secrets) | $0.06 | <0.1% |

### By Resource Type

| Type | Monthly Cost | Percentage |
|------|--------------|------------|
| Compute (nodes + management) | $364.24 | 89.4% |
| Networking | $24.25 | 6.0% |
| Storage | $17.84 | 4.4% |
| Other Services | $0.06 | <0.1% |