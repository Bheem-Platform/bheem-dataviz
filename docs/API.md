# Bheem DataViz API Documentation

Base URL: `https://api.dataviz.bheemkodee.com/api/v1`

## Authentication

Include API key in header:
```
Authorization: Bearer <your-api-key>
```

## Endpoints

### Connections

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /connections | List all connections |
| POST | /connections | Create connection |
| GET | /connections/:id | Get connection |
| DELETE | /connections/:id | Delete connection |
| POST | /connections/:id/test | Test connection |

### Datasets

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /datasets | List all datasets |
| POST | /datasets | Create dataset |
| GET | /datasets/:id | Get dataset |
| GET | /datasets/:id/preview | Preview data |

### Dashboards

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /dashboards | List all dashboards |
| POST | /dashboards | Create dashboard |
| GET | /dashboards/:id | Get dashboard |
| PUT | /dashboards/:id | Update dashboard |
| DELETE | /dashboards/:id | Delete dashboard |

### Charts

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /charts | List all charts |
| POST | /charts | Create chart |
| GET | /charts/:id | Get chart |
| GET | /charts/:id/render | Render chart data |

### Queries

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /queries/execute | Execute SQL query |
| POST | /queries/preview | Preview query (limited) |
| GET | /queries/saved | List saved queries |
| POST | /queries/saved | Save query |

### AI

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /ai/nl-query | Natural language to SQL |
| POST | /ai/insights | Get AI insights |
| POST | /ai/chat | Chat with Kodee |
| POST | /ai/suggest | Get visualization suggestions |

## Examples

### Create a Connection

```bash
curl -X POST https://api.dataviz.bheemkodee.com/api/v1/connections \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Production DB",
    "type": "postgresql",
    "host": "db.example.com",
    "port": 5432,
    "database": "myapp",
    "username": "readonly"
  }'
```

### Execute Query

```bash
curl -X POST https://api.dataviz.bheemkodee.com/api/v1/queries/execute \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "connection_id": "conn_123",
    "sql": "SELECT * FROM users LIMIT 10"
  }'
```

### Natural Language Query

```bash
curl -X POST https://api.dataviz.bheemkodee.com/api/v1/ai/nl-query \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Show me total sales by region for last month",
    "dataset_id": "ds_456"
  }'
```
