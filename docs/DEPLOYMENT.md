# Deployment Guide

## Docker Compose (Recommended)

```yaml
version: '3.8'

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
      args:
        VITE_API_URL: https://api.dataviz.bheemkodee.com
    ports:
      - "80:80"

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://user:pass@db:5432/dataviz
      REDIS_URL: redis://redis:6379
    depends_on:
      - db
      - redis

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: dataviz
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - pgdata:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine

volumes:
  pgdata:
```

## Manual Deployment

### Frontend

```bash
cd frontend
npm install
npm run build

# Serve with nginx or any static server
```

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Environment Variables

### Frontend
- `VITE_API_URL` - Backend API URL

### Backend
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `OPENAI_API_KEY` - OpenAI API key for Kodee AI
- `CORS_ORIGINS` - Allowed origins (JSON array)
