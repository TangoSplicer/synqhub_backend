# SynQ Backend API Documentation

## Overview

The SynQ Backend provides a comprehensive REST API for quantum computing, machine learning, and job management. All endpoints are prefixed with `/api/v1`.

## Authentication

All protected endpoints require Bearer token authentication in the `Authorization` header:

```
Authorization: Bearer <access_token>
```

### Tokens

- **Access Token:** Valid for 24 hours, used for API requests
- **Refresh Token:** Valid for 7 days, used to obtain new access tokens

## Authentication Endpoints

### Register User

**POST** `/api/v1/auth/register`

Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "secure_password_123",
  "organization": "My Organization"
}
```

**Response (201 Created):**
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

### Login

**POST** `/api/v1/auth/login`

Authenticate user and obtain tokens.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "secure_password_123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

### Refresh Token

**POST** `/api/v1/auth/refresh`

Obtain a new access token using a refresh token.

**Request Body:**
```json
{
  "refresh_token": "eyJhbGc..."
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

### Get Current User

**GET** `/api/v1/auth/me`

Get current user profile information.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "role": "user",
  "organization_id": "org-123",
  "is_active": true,
  "created_at": "2025-01-04T10:00:00Z",
  "updated_at": "2025-01-04T10:00:00Z"
}
```

## QML (Quantum Machine Learning) Endpoints

### Submit VQE Job

**POST** `/api/v1/qml/vqe`

Submit a Variational Quantum Eigensolver job.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "hamiltonian": "{\"Z0\": 1.0, \"Z1\": 0.5}",
  "ansatz_circuit": {
    "num_parameters": 2,
    "gates": ["RY", "CNOT", "RY"]
  },
  "optimizer": "COBYLA",
  "max_iterations": 100,
  "shots": 1024
}
```

**Response (202 Accepted):**
```json
{
  "id": "job-550e8400-e29b-41d4-a716-446655440000",
  "user_id": "user-550e8400-e29b-41d4-a716-446655440000",
  "job_type": "vqe",
  "status": "SUBMITTED",
  "backend": null,
  "created_at": "2025-01-04T10:00:00Z",
  "started_at": null,
  "completed_at": null,
  "results": null
}
```

### Submit QAOA Job

**POST** `/api/v1/qml/qaoa`

Submit a Quantum Approximate Optimization Algorithm job.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "problem_graph": {
    "nodes": [0, 1, 2, 3],
    "edges": [[0, 1], [1, 2], [2, 3], [3, 0]]
  },
  "p": 2,
  "optimizer": "COBYLA",
  "shots": 1024
}
```

**Response (202 Accepted):**
```json
{
  "id": "job-550e8400-e29b-41d4-a716-446655440000",
  "user_id": "user-550e8400-e29b-41d4-a716-446655440000",
  "job_type": "qaoa",
  "status": "SUBMITTED",
  "backend": null,
  "created_at": "2025-01-04T10:00:00Z",
  "started_at": null,
  "completed_at": null,
  "results": null
}
```

### Get Job Status

**GET** `/api/v1/qml/jobs/{job_id}`

Get the status and results of a quantum job.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "id": "job-550e8400-e29b-41d4-a716-446655440000",
  "user_id": "user-550e8400-e29b-41d4-a716-446655440000",
  "job_type": "vqe",
  "status": "COMPLETED",
  "backend": null,
  "created_at": "2025-01-04T10:00:00Z",
  "started_at": "2025-01-04T10:00:05Z",
  "completed_at": "2025-01-04T10:00:30Z",
  "results": {
    "ground_state_energy": -1.137,
    "parameters": [0.123, 0.456],
    "iterations": 45,
    "success": true
  }
}
```

### List Jobs

**GET** `/api/v1/qml/jobs`

List user's quantum jobs with pagination.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `limit` (int, default: 10): Maximum number of jobs to return
- `offset` (int, default: 0): Number of jobs to skip
- `status` (str, optional): Filter by job status (SUBMITTED, QUEUED, RUNNING, COMPLETED, FAILED)

**Response (200 OK):**
```json
{
  "jobs": [
    {
      "id": "job-550e8400-e29b-41d4-a716-446655440000",
      "user_id": "user-550e8400-e29b-41d4-a716-446655440000",
      "job_type": "vqe",
      "status": "COMPLETED",
      "backend": null,
      "created_at": "2025-01-04T10:00:00Z",
      "started_at": "2025-01-04T10:00:05Z",
      "completed_at": "2025-01-04T10:00:30Z",
      "results": null
    }
  ],
  "total_count": 1,
  "has_more": false
}
```

## Error Responses

All errors follow a consistent format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common HTTP Status Codes

| Status Code | Description |
|-------------|-------------|
| 200 | OK - Request successful |
| 201 | Created - Resource created successfully |
| 202 | Accepted - Async job submitted |
| 400 | Bad Request - Invalid request parameters |
| 401 | Unauthorized - Missing or invalid authentication |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource not found |
| 409 | Conflict - Resource already exists |
| 500 | Internal Server Error - Server error |

## Rate Limiting

API requests are rate-limited to 1000 requests per hour per user. Rate limit information is included in response headers:

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1234567890
```

## Pagination

List endpoints support pagination via `limit` and `offset` query parameters:

```
GET /api/v1/qml/jobs?limit=10&offset=20
```

## Versioning

The API uses URL-based versioning. Current version is `v1`. Future versions will be available at `/api/v2`, etc.

## Webhooks (Future)

Webhook support for job completion notifications is planned for a future release.

## Support

For API support and issues, please visit: https://github.com/TangoSplicer/synq-backend/issues
