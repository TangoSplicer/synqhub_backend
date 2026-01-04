# Frontend-Backend Integration Guide

## Overview

This document describes how the SynQ frontend showcase website integrates with the backend API to provide a complete quantum computing platform experience.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│         Frontend Website (React + Tailwind)             │
│     https://synq-expansion-showcase.manus.space        │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ HTTP/WebSocket
                     │ REST API Calls
                     │
┌────────────────────▼────────────────────────────────────┐
│         Backend API (FastAPI + PostgreSQL)              │
│        https://api.synq.manus.space:8000               │
└─────────────────────────────────────────────────────────┘
```

## Frontend Components

### 1. Feature Comparison Table
**Location**: Home page, "Competitive Advantages" section
**API Endpoints Used**: None (static data)
**Purpose**: Display feature comparison with competitors

### 2. Use Cases Section
**Location**: Home page, "Real-World Applications" section
**API Endpoints Used**: None (static data)
**Purpose**: Showcase real-world quantum computing applications

### 3. Code Editor (Try It Out)
**Location**: Home page, "Try It Out" section
**API Endpoints Used**:
- `POST /api/v1/qml/vqe` - Execute VQE algorithm
- `POST /api/v1/synthesis/synthesize` - Synthesize circuits
- `POST /api/v1/synthesis/transpile` - Transpile circuits

**Features**:
- Monaco Editor for code editing
- Real-time syntax highlighting
- Execute quantum algorithms
- Display results and metrics

### 4. Strategic Roadmap
**Location**: Home page, "Strategic Roadmap" section
**API Endpoints Used**: None (static data)
**Purpose**: Display development roadmap

### 5. Navigation Links
**Location**: Header and footer
**Links**:
- GitHub Repository: https://github.com/TangoSplicer/synq-backend
- API Documentation: https://api.synq.manus.space/docs
- Discussions: https://github.com/TangoSplicer/synq-backend/discussions

## API Integration Points

### Authentication

```javascript
// Frontend authentication flow
const response = await fetch('https://api.synq.manus.space/api/v1/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'password123',
  }),
});

const { access_token, token_type } = await response.json();

// Store token in localStorage
localStorage.setItem('access_token', access_token);
```

### Making Authenticated Requests

```javascript
// Helper function for authenticated API calls
async function apiCall(endpoint, options = {}) {
  const token = localStorage.getItem('access_token');
  
  const response = await fetch(`https://api.synq.manus.space${endpoint}`, {
    ...options,
    headers: {
      ...options.headers,
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });
  
  if (response.status === 401) {
    // Token expired, redirect to login
    window.location.href = '/login';
  }
  
  return response.json();
}
```

### Example: VQE Execution

```javascript
// Execute VQE algorithm from frontend
async function executeVQE(hamiltonian, ansatz) {
  const result = await apiCall('/api/v1/qml/vqe', {
    method: 'POST',
    body: JSON.stringify({
      hamiltonian: hamiltonian,
      ansatz: ansatz,
      max_iterations: 100,
    }),
  });
  
  return result;
}

// Usage
const vqeResult = await executeVQE(
  'Z0 Z1 + X0 X1',
  'RY(theta0) RY(theta1)'
);

console.log('Ground state energy:', vqeResult.ground_state_energy);
console.log('Iterations:', vqeResult.iterations);
```

### Example: Circuit Synthesis

```javascript
// Synthesize quantum circuit from frontend
async function synthesizeCircuit(description) {
  const result = await apiCall('/api/v1/synthesis/synthesize', {
    method: 'POST',
    body: JSON.stringify({
      description: description,
      optimization_level: 2,
    }),
  });
  
  return result;
}

// Usage
const synthesized = await synthesizeCircuit(
  'Create a circuit that prepares a Bell state'
);

console.log('Circuit:', synthesized.circuit);
console.log('Gate count:', synthesized.gate_count);
```

## Real-Time Features

### WebSocket Connection for Streaming Analytics

```javascript
// Connect to real-time analytics stream
const ws = new WebSocket('wss://api.synq.manus.space/api/v1/analytics/stream');

ws.onmessage = (event) => {
  const metrics = JSON.parse(event.data);
  
  // Update dashboard with real-time metrics
  updateDashboard(metrics);
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

ws.onclose = () => {
  console.log('WebSocket connection closed');
};
```

## Error Handling

### Standard Error Response Format

```javascript
// Backend returns standardized error responses
{
  "success": false,
  "error": "Invalid input",
  "details": {
    "field": "hamiltonian",
    "message": "Invalid Hamiltonian format"
  }
}
```

### Frontend Error Handling

```javascript
async function handleAPICall(endpoint, options) {
  try {
    const response = await apiCall(endpoint, options);
    
    if (!response.success) {
      // Handle error
      showErrorMessage(response.error);
      return null;
    }
    
    return response;
  } catch (error) {
    console.error('API call failed:', error);
    showErrorMessage('Failed to connect to backend');
    return null;
  }
}
```

## Development Environment Setup

### Local Development

1. **Start Backend**:
```bash
cd /home/ubuntu/synq-backend
docker-compose up -d
```

2. **Update Frontend API Base URL**:
```javascript
// In frontend .env file
VITE_API_BASE_URL=http://localhost:8000
```

3. **Start Frontend**:
```bash
cd /home/ubuntu/synq_expansion_showcase
pnpm dev
```

### Production Environment

1. **Backend**: https://api.synq.manus.space
2. **Frontend**: https://synq-expansion-showcase.manus.space

## API Endpoints for Frontend

### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/logout` - User logout

### Quantum ML Services
- `POST /api/v1/qml/vqe` - Execute VQE algorithm
- `POST /api/v1/qml/qaoa` - Execute QAOA algorithm
- `POST /api/v1/qml/qnn` - Execute QNN algorithm
- `GET /api/v1/qml/jobs/{job_id}` - Get job status

### Circuit Operations
- `POST /api/v1/synthesis/synthesize` - Synthesize circuit
- `POST /api/v1/synthesis/transpile` - Transpile circuit
- `GET /api/v1/synthesis/suggest-optimizations` - Get optimization suggestions

### Analytics
- `GET /api/v1/analytics/stream/jobs` - Stream job metrics
- `GET /api/v1/analytics/dashboard` - Get live dashboard
- `POST /api/v1/analytics/metrics` - Track custom metrics

### Plugins
- `GET /api/v1/plugins/search` - Search plugins
- `GET /api/v1/plugins/trending` - Get trending plugins
- `POST /api/v1/plugins/register` - Register plugin

## CORS Configuration

The backend is configured to accept requests from the frontend:

```python
# In app/config.py
CORS_ORIGINS = [
    "https://synq-expansion-showcase.manus.space",
    "http://localhost:3000",  # Local development
]
```

## Rate Limiting

API rate limits for frontend requests:
- **Authenticated Users**: 1,000 requests/minute
- **Anonymous Users**: 100 requests/minute
- **VQE/QAOA Execution**: 10 requests/minute

## Monitoring Integration

### Frontend Analytics
The frontend sends usage analytics to the backend:

```javascript
// Track user actions
async function trackEvent(eventName, metadata) {
  await apiCall('/api/v1/analytics/track', {
    method: 'POST',
    body: JSON.stringify({
      event_name: eventName,
      metadata: metadata,
      timestamp: new Date().toISOString(),
    }),
  });
}

// Usage
trackEvent('vqe_executed', {
  hamiltonian: 'Z0 Z1',
  iterations: 100,
  result: 'success',
});
```

## Testing Integration

### Frontend Tests with Mock Backend

```javascript
// Mock API responses for testing
import { rest } from 'msw';
import { setupServer } from 'msw/node';

const server = setupServer(
  rest.post('https://api.synq.manus.space/api/v1/qml/vqe', (req, res, ctx) => {
    return res(
      ctx.json({
        success: true,
        ground_state_energy: -1.5,
        iterations: 50,
      })
    );
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

## Deployment Checklist

- [ ] Backend API deployed and running
- [ ] Frontend website deployed and running
- [ ] CORS configuration verified
- [ ] SSL/TLS certificates configured
- [ ] Rate limiting enabled
- [ ] Monitoring and logging enabled
- [ ] Error handling tested
- [ ] WebSocket connections tested
- [ ] Authentication flow tested
- [ ] API documentation accessible

## Troubleshooting

### CORS Errors
**Problem**: "Access to XMLHttpRequest has been blocked by CORS policy"
**Solution**: Verify backend CORS configuration includes frontend URL

### Authentication Failures
**Problem**: "401 Unauthorized"
**Solution**: Check token expiration and refresh token mechanism

### WebSocket Connection Failures
**Problem**: "WebSocket connection failed"
**Solution**: Verify WebSocket support in backend and firewall rules

### Slow API Responses
**Problem**: API calls taking >1 second
**Solution**: Check backend performance metrics and database queries

## Support

For integration issues, please:
1. Check the API documentation: https://api.synq.manus.space/docs
2. Review error logs in backend
3. Open an issue on GitHub: https://github.com/TangoSplicer/synq-backend/issues
