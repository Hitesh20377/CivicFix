# Smart Meeting Assistant - Production Deployment Guide

This guide explains how to deploy the Smart Meeting Assistant in a production environment using the `docker-compose.prod.yml` architecture.

## Architecture Overview

The production deployment relies on several orchestrated containers:
- **Nginx**: Reverse proxy handling SSL termination and rate-limiting. Routes traffic to the frontend and backend.
- **Frontend (Streamlit)**: Interactive UI for meeting management and insights review.
- **Backend (Flask + Gunicorn)**: API serving web traffic and orchestrating jobs.
- **Worker & Beat (Celery)**: Asynchronous task processors for ML pipeline execution and scheduled reminders.
- **PostgreSQL**: Relational database with `pgvector` for embedding storage.
- **Redis**: In-memory message broker and cache.
- **MinIO**: High-performance, self-hosted S3-compatible object storage.
- **Prometheus & Grafana**: Operational monitoring and alerting dashboards.

## Prerequisites

Ensure you have Docker and Docker Compose installed on your host server.

## 1. Environment Configuration

Create a `.env` file in the root directory based on `.env.example`, but configure it for production. 

```env
# Security Secrets
SECRET_KEY=generate_a_very_long_random_string
GRAFANA_PASSWORD=secure_admin_password
DB_PASSWORD=secure_db_password

# Object Storage Secrets
MINIO_ACCESS_KEY=admin_access_key
MINIO_SECRET_KEY=admin_secret_key
```

## 2. Running the Stack

To build and start the entire stack in detached mode:

```bash
docker-compose -f docker-compose.prod.yml up --build -d
```

### Checking Status

Verify that all containers are healthy and running:

```bash
docker-compose -f docker-compose.prod.yml ps
```

To view the logs of a specific service (e.g., the API or worker):

```bash
docker-compose -f docker-compose.prod.yml logs -f api
docker-compose -f docker-compose.prod.yml logs -f worker
```

## 3. Scaling Workers

If meeting processing volume increases, you can easily scale the Celery workers to handle more concurrent ML tasks:

```bash
docker-compose -f docker-compose.prod.yml up -d --scale worker=3
```

## 4. Backups and Maintenance

### Database Backups
Schedule daily `pg_dump` backups for the PostgreSQL container:

```bash
docker exec -t <postgres_container_name> pg_dump -U civicfix_user civicfix_db -F c > /path/to/backups/db_backup_$(date +%Y%m%d).dump
```

### Object Storage Backups
MinIO stores data in the `minio_prod_data` Docker volume. You should mount this to a secure EBS volume or use MinIO's built-in `mc` tool to mirror the bucket to an offsite cloud provider.

## 5. Monitoring Access

- **Smart Meeting Assistant App**: Accessible at `http://<your_server_ip>`
- **API Endpoints**: Accessible at `http://<your_server_ip>/api/`
- **MinIO Console**: Accessible at `http://<your_server_ip>/minio/`
- **Grafana Dashboards**: Accessible at `http://<your_server_ip>:3000` (Map port 3000 if needed, or route through Nginx).
