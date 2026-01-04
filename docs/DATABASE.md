# SynQ Backend Database Schema

## Overview

The SynQ backend uses PostgreSQL as the primary database with SQLAlchemy ORM for data access. This document describes the database schema and relationships.

## Tables

### Users Table

Stores user account information.

| Column | Type | Constraints | Description |
|--------|------|-----------|-------------|
| id | UUID | PRIMARY KEY | Unique user identifier |
| email | VARCHAR(255) | UNIQUE, NOT NULL | User email address |
| password_hash | VARCHAR(255) | NOT NULL | Bcrypt hashed password |
| organization_id | UUID | NULLABLE | Associated organization |
| role | VARCHAR(50) | DEFAULT 'user' | User role (user, admin, etc.) |
| created_at | TIMESTAMP | DEFAULT NOW() | Account creation timestamp |
| updated_at | TIMESTAMP | DEFAULT NOW() | Last update timestamp |
| last_login | TIMESTAMP | NULLABLE | Last login timestamp |
| is_active | BOOLEAN | DEFAULT TRUE | Account active status |
| mfa_enabled | BOOLEAN | DEFAULT FALSE | Multi-factor auth enabled |
| api_quota_monthly | INT | DEFAULT 10000 | Monthly API request quota |
| api_quota_used | INT | DEFAULT 0 | API requests used this month |

**Indexes:**
- `idx_users_email` on email (UNIQUE)

### Jobs Table

Tracks quantum job submissions and results.

| Column | Type | Constraints | Description |
|--------|------|-----------|-------------|
| id | UUID | PRIMARY KEY | Unique job identifier |
| user_id | UUID | FOREIGN KEY, NOT NULL | Job owner |
| job_type | VARCHAR(50) | NOT NULL | Job type (vqe, qaoa, synthesis, etc.) |
| backend | VARCHAR(100) | NULLABLE | Target quantum backend |
| status | VARCHAR(50) | DEFAULT 'SUBMITTED' | Job status |
| circuit_data | JSON | NULLABLE | Quantum circuit definition |
| parameters | JSON | NULLABLE | Job parameters |
| results | JSON | NULLABLE | Job results |
| error_message | VARCHAR(1000) | NULLABLE | Error message if failed |
| created_at | TIMESTAMP | DEFAULT NOW() | Job submission timestamp |
| started_at | TIMESTAMP | NULLABLE | Job start timestamp |
| completed_at | TIMESTAMP | NULLABLE | Job completion timestamp |
| execution_time_ms | INT | NULLABLE | Execution time in milliseconds |
| resource_usage | JSON | NULLABLE | Resource usage metrics |
| metadata | JSON | NULLABLE | Additional metadata |

**Indexes:**
- `idx_jobs_user_id` on user_id
- `idx_jobs_status` on status
- `idx_jobs_created_at` on created_at

**Foreign Keys:**
- `user_id` → users.id

### Circuits Table

Stores saved quantum circuits.

| Column | Type | Constraints | Description |
|--------|------|-----------|-------------|
| id | UUID | PRIMARY KEY | Unique circuit identifier |
| user_id | UUID | FOREIGN KEY, NOT NULL | Circuit owner |
| name | VARCHAR(255) | NULLABLE | Circuit name |
| description | VARCHAR(1000) | NULLABLE | Circuit description |
| circuit_data | JSON | NOT NULL | Circuit definition |
| depth | INT | NULLABLE | Circuit depth (gate count) |
| gate_count | INT | NULLABLE | Total number of gates |
| qubit_count | INT | NULLABLE | Number of qubits |
| created_at | TIMESTAMP | DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMP | DEFAULT NOW() | Last update timestamp |
| is_public | BOOLEAN | DEFAULT FALSE | Public visibility flag |
| tags | JSON | NULLABLE | Circuit tags for organization |

**Indexes:**
- `idx_circuits_user_id` on user_id
- `idx_circuits_is_public` on is_public

**Foreign Keys:**
- `user_id` → users.id

## Relationships

```
Users (1) ──── (N) Jobs
         └──── (N) Circuits

Jobs (N) ──── (1) Users
Circuits (N) ──── (1) Users
```

## Job Status Lifecycle

```
SUBMITTED → QUEUED → RUNNING → COMPLETED
                   ↘ FAILED
```

- **SUBMITTED:** Job received and queued for processing
- **QUEUED:** Waiting for available compute resources
- **RUNNING:** Currently executing on quantum backend
- **COMPLETED:** Successfully completed with results
- **FAILED:** Execution failed with error message

## Data Types

### JSON Columns

JSON columns store structured data:

**circuit_data Example:**
```json
{
  "num_qubits": 2,
  "gates": [
    {"type": "H", "target": 0},
    {"type": "CNOT", "control": 0, "target": 1},
    {"type": "RZ", "target": 1, "parameter": 0.5}
  ]
}
```

**parameters Example:**
```json
{
  "hamiltonian": "{\"Z0\": 1.0, \"Z1\": 0.5}",
  "optimizer": "COBYLA",
  "max_iterations": 100,
  "shots": 1024
}
```

**results Example:**
```json
{
  "ground_state_energy": -1.137,
  "parameters": [0.123, 0.456],
  "iterations": 45,
  "success": true,
  "convergence_history": [-1.5, -1.3, -1.2, -1.137]
}
```

## Migrations

Database migrations are managed using Alembic. To create a new migration:

```bash
alembic revision --autogenerate -m "Description of changes"
alembic upgrade head
```

## Backup & Recovery

- **Backup Frequency:** Every 6 hours
- **Retention Period:** 30 days hot, 1 year cold storage
- **Recovery Time Objective (RTO):** 1 hour
- **Recovery Point Objective (RPO):** 15 minutes

## Performance Considerations

- Indexes are created on frequently queried columns
- JSON columns use GIN indexes for efficient querying
- Connection pooling is configured with 20 connections
- Query results are cached in Redis for 1 hour

## Security

- All passwords are hashed with bcrypt
- Sensitive data is encrypted at rest
- Database connections use SSL/TLS
- Access is restricted to authenticated users
- Audit logging tracks all data modifications
