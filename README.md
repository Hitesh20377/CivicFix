# CivicFix

Industry-ready civic issue reporting and resolution platform built with React, Flask, PostgreSQL, Redis, Celery, JWT authentication, and Docker.

CivicFix connects citizens with municipal officers to streamline the resolution of public issues like potholes, broken streetlights, and drainage blockages.

## Project Structure

This is a monorepo containing both the frontend and backend services, orchestrated with Docker Compose.

- `frontend/`: React frontend application built with Vite and Tailwind CSS.
- `backend/`: Python Flask backend application using the application factory pattern.
- `database/`: Database configuration and migration scripts (PostgreSQL/PostGIS).
- `docs/`: Architecture and design documentation.
- `tests/`: End-to-end integration tests.

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Node.js (for local frontend development)
- Python 3.11+ (for local backend development)

### Setup

1. **Clone the repository** (if you haven't already).
2. **Set up environment variables:**

```bash
cp .env.example .env
```

3. **Run the application using Docker:**

```bash
docker-compose up --build
```

This will spin up:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:5000
- **PostgreSQL Database**: localhost:5432
- **Redis Cache**: localhost:6379

You can verify the backend is running by navigating to the health endpoint: http://localhost:5000/api/health

## Tech Stack

**Frontend:**
- React (JavaScript)
- Vite
- Tailwind CSS
- React Router
- Axios

**Backend:**
- Python Flask
- PostgreSQL + PostGIS
- Redis

## Permissions Matrix

| Feature | Citizen | Officer | Field Worker | Admin |
|---|---|---|---|---|
| Create issue | Yes | Yes | No | Yes |
| View own issues | Yes | Yes | Yes | Yes |
| View all issues | No | Limited | No | Yes |
| Assign worker | No | Yes | No | Yes |
| Manage users | No | No | No | Yes |
| View analytics | Own data | Ward/department | Own work | All data |

---
*Note: This repository implements foundational business logic, analytics, and robust security/observability as part of the CivicFix architecture.*
