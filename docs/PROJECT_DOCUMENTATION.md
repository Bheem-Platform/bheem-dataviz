# Bheem DataViz - Technical Documentation

> **AI-Powered Business Intelligence & Data Visualization Platform**
> Version: 1.3.0 | Last Updated: 2026-01-28

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Technology Stack](#2-technology-stack)
3. [Project Structure](#3-project-structure)
4. [Backend Architecture](#4-backend-architecture)
5. [Frontend Architecture](#5-frontend-architecture)
6. [Database Design](#6-database-design)
7. [API Reference](#7-api-reference)
8. [Authentication & Security](#8-authentication--security)
9. [Docker Configuration](#9-docker-configuration)
10. [Development Guide](#10-development-guide)
11. [Deployment](#11-deployment)
12. [Key Features](#12-key-features)
13. [Roadmap](#13-roadmap)
14. [Troubleshooting](#14-troubleshooting)

---

## 1. Project Overview

### 1.1 What is Bheem DataViz?

Bheem DataViz is a comprehensive, AI-powered Business Intelligence and Data Visualization Platform that enables organizations to:

- **Connect** to multiple data sources (PostgreSQL, MySQL, MongoDB, CSV, Excel, and more)
- **Transform** data using visual pipeline builders without writing code
- **Model** data with semantic layers for consistent business metrics
- **Visualize** data with 40+ chart types powered by Apache ECharts
- **Collaborate** with dashboards that can be shared publicly or privately
- **Automate** workflows via BheemFlow integration
- **Query** data using natural language (AI-powered - planned)

### 1.2 Key Differentiators

| Feature | Bheem DataViz | Competitors |
|---------|---------------|-------------|
| **Pricing** | Flat $49/month | Per-user pricing |
| **Users** | Unlimited | Limited by tier |
| **AI Assistant** | Built-in (Kodee) | Add-on or none |
| **Semantic Layer** | Cube.js integration | Often separate |
| **Workflow Automation** | BheemFlow native | Third-party |
| **Self-Hosted** | Available | Enterprise only |
| **White-Label** | Available | Enterprise only |

### 1.3 Production URLs

| Environment | URL |
|-------------|-----|
| Production App | https://dataviz.bheemkodee.com |
| Production API | https://api.dataviz.bheemkodee.com |
| Staging App | https://dataviz-staging.bheemkodee.com |
| Staging API | https://dataviz-api-staging.bheemkodee.com |

### 1.4 Bheem Platform Integration

Bheem DataViz integrates with the broader Bheem Platform ecosystem:

- **Bheem Passport** - Authentication & SSO
- **Bheem SKU** - Pricing & subscription management
- **BheemFlow** - Workflow automation & scheduling
- **Kodee** - AI assistant for natural language queries

---

## 2. Technology Stack

### 2.1 Frontend Stack

| Category | Technology | Version | Purpose |
|----------|------------|---------|---------|
| **Framework** | React | 18.x | UI library |
| **Language** | TypeScript | 5.x | Type safety |
| **Build Tool** | Vite | 5.x | Fast bundling & HMR |
| **Styling** | TailwindCSS | 3.4 | Utility-first CSS |
| **State Management** | Zustand | - | Lightweight global state |
| **Server State** | TanStack Query | 5.17 | Caching & sync |
| **Routing** | React Router | 6.x | SPA navigation |
| **HTTP Client** | Axios | - | API requests |
| **Charts** | Apache ECharts | 5.4.3 | Visualization engine |
| **Charts React** | echarts-for-react | 3.0.2 | React wrapper |
| **Code Editor** | Monaco Editor | 0.45.0 | SQL editing |
| **Layout** | GridStack | 10.0.1 | Dashboard grid |
| **Drag & Drop** | dnd-kit | - | Widget sorting |
| **UI Primitives** | Radix UI | - | Accessible components |
| **Icons** | Lucide React | - | Icon library |
| **Animation** | Framer Motion | 12.26.2 | Motion effects |
| **Tables** | TanStack Table | 8.11.2 | Data grids |
| **Date Handling** | date-fns | 3.2.0 | Date utilities |

### 2.2 Backend Stack

| Category | Technology | Version | Purpose |
|----------|------------|---------|---------|
| **Framework** | FastAPI | 0.109.0 | REST API framework |
| **Server** | Uvicorn | 0.27.0 | ASGI server |
| **Language** | Python | 3.11 | Runtime |
| **ORM** | SQLAlchemy | 2.0.25 | Database ORM (async) |
| **Migrations** | Alembic | 1.13.1 | Schema migrations |
| **PostgreSQL Driver** | asyncpg | 0.29.0 | Async PostgreSQL |
| **MySQL Driver** | aiomysql | 0.2.0 | Async MySQL |
| **MongoDB Driver** | motor | 3.3.2 | Async MongoDB |
| **Caching** | Redis | 5.0.1 | Query caching |
| **Data Processing** | Pandas | 2.1.4 | DataFrames |
| **Numerical** | NumPy | 1.26.3 | Numerical ops |
| **Excel** | openpyxl | 3.1.2 | Excel parsing |
| **JWT** | python-jose | 3.3.0 | Token handling |
| **Password** | passlib[bcrypt] | 1.7.4 | Hashing |
| **AI** | OpenAI | 1.10.0 | Kodee integration |
| **Validation** | Pydantic | 2.5.3 | Data validation |
| **HTTP** | httpx | 0.26.0 | External requests |

### 2.3 Infrastructure Stack

| Category | Technology | Purpose |
|----------|------------|---------|
| **Containerization** | Docker | Container runtime |
| **Orchestration** | Docker Compose | Multi-container apps |
| **Process Manager** | PM2 | Production process management |
| **Web Server** | Nginx | Static file serving & reverse proxy |
| **Primary Database** | PostgreSQL 15 | Application data storage |
| **Cache** | Redis 7 | Session & query caching |

---

## 3. Project Structure

```
bheem-dataviz/
├── backend/                          # FastAPI Backend Application
│   ├── app/
│   │   ├── api/v1/
│   │   │   ├── api.py               # Router aggregator
│   │   │   └── endpoints/           # API route handlers
│   │   │       ├── auth.py          # Authentication endpoints
│   │   │       ├── connections.py   # Data source management
│   │   │       ├── dashboards.py    # Dashboard CRUD
│   │   │       ├── charts.py        # Chart rendering
│   │   │       ├── queries.py       # SQL execution
│   │   │       ├── datasets.py      # Dataset management
│   │   │       ├── transforms.py    # Data transformations
│   │   │       ├── semantic_models.py # Semantic layer
│   │   │       ├── kpi.py           # KPI calculations
│   │   │       └── ai.py            # AI/NL endpoints
│   │   ├── core/
│   │   │   └── config.py            # Application settings
│   │   ├── database.py              # SQLAlchemy configuration
│   │   ├── models/                  # ORM Models
│   │   │   ├── connection.py        # Connection model
│   │   │   ├── dashboard.py         # Dashboard & Chart models
│   │   │   ├── semantic.py          # Semantic layer models
│   │   │   ├── transform.py         # Transform models
│   │   │   └── user.py              # User model
│   │   ├── schemas/                 # Pydantic Schemas
│   │   │   ├── connection.py
│   │   │   ├── dashboard.py
│   │   │   ├── semantic_model.py
│   │   │   ├── transform.py
│   │   │   └── query.py
│   │   └── services/                # Business Logic
│   │       ├── postgres_service.py  # PostgreSQL operations
│   │       ├── mysql_service.py     # MySQL operations
│   │       ├── mongodb_service.py   # MongoDB operations
│   │       ├── transform_service.py # Transform execution
│   │       ├── semantic_model_service.py
│   │       ├── auth_service.py      # Authentication
│   │       ├── encryption_service.py # Password encryption
│   │       └── file_service.py      # CSV/Excel handling
│   ├── alembic/                     # Database Migrations
│   │   ├── versions/                # Migration scripts
│   │   └── env.py                   # Alembic configuration
│   ├── main.py                      # Application entry point
│   ├── Dockerfile                   # Backend container
│   └── requirements.txt             # Python dependencies
│
├── frontend/                        # React Frontend Application
│   ├── src/
│   │   ├── App.tsx                 # Router configuration
│   │   ├── main.tsx                # React entry point
│   │   ├── index.css               # Global styles
│   │   ├── components/
│   │   │   ├── auth/               # Authentication components
│   │   │   │   └── PrivateRoute.tsx
│   │   │   ├── common/             # Shared components
│   │   │   │   ├── Layout.tsx      # App shell
│   │   │   │   ├── Navbar.tsx
│   │   │   │   ├── Hero.tsx
│   │   │   │   └── TrustedPartners.tsx
│   │   │   ├── dashboard/          # Dashboard components
│   │   │   │   ├── ChartWidget.tsx
│   │   │   │   ├── KPICard.tsx
│   │   │   │   └── KPIBuilder.tsx
│   │   │   └── ui/                 # UI primitives
│   │   ├── contexts/
│   │   │   └── AuthContext.tsx     # Auth state provider
│   │   ├── lib/
│   │   │   ├── api.ts              # API client
│   │   │   └── utils.ts            # Utilities
│   │   ├── pages/                  # Page components
│   │   │   ├── LandingPage.tsx     # Marketing page
│   │   │   ├── Login.tsx           # Login page
│   │   │   ├── Register.tsx        # Registration
│   │   │   ├── HomePage.tsx        # Dashboard home
│   │   │   ├── DashboardList.tsx   # Dashboard list
│   │   │   ├── DashboardBuilder.tsx # Dashboard editor
│   │   │   ├── ChartBuilder.tsx    # Chart editor (166KB)
│   │   │   ├── TransformBuilder.tsx # Transform editor
│   │   │   ├── SemanticModels.tsx  # Semantic layer
│   │   │   ├── DataConnections.tsx # Connection manager
│   │   │   ├── Datasets.tsx        # Dataset management
│   │   │   ├── SQLLab.tsx          # SQL editor
│   │   │   ├── KPIs.tsx            # KPI management
│   │   │   ├── Explore.tsx         # Data exploration
│   │   │   ├── KodeeAnalytics.tsx  # AI insights
│   │   │   └── Workflows.tsx       # BheemFlow
│   │   └── services/
│   │       └── auth.ts             # Auth service
│   ├── Dockerfile                  # Dev container
│   ├── Dockerfile.prod             # Production container
│   ├── nginx.conf                  # Nginx configuration
│   ├── package.json                # Dependencies
│   ├── vite.config.ts              # Vite configuration
│   ├── tailwind.config.js          # Tailwind configuration
│   └── tsconfig.json               # TypeScript configuration
│
├── docker/                         # Docker Compose Files
│   ├── docker-compose.yml          # Production
│   ├── docker-compose.dev.yml      # Development
│   └── docker-compose.databases.yml # Databases only
│
├── docs/                           # Documentation
│   ├── API.md                      # API documentation
│   └── DEPLOYMENT.md               # Deployment guide
│
├── sdk/                            # Client SDKs (planned)
│
├── README.md                       # Project overview
├── agentbheem.md                   # Project memory
├── scope.md                        # Project scope
├── DATABASES_README.md             # Database setup
├── DB_CONFIG.md                    # Database config
├── DATAVIZ_TROUBLESHOOTING.md      # Troubleshooting
└── ecosystem.config.js             # PM2 configuration
```

---

## 4. Backend Architecture

### 4.1 Application Entry Point

**File:** `backend/main.py`

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router
from app.core.config import settings

app = FastAPI(
    title="Bheem DataViz API",
    version="1.3.0",
    description="AI-powered Business Intelligence Platform"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routes
app.include_router(api_router, prefix="/api/v1")
```

### 4.2 Configuration Management

**File:** `backend/app/core/config.py`

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Bheem DataViz"
    VERSION: str = "1.3.0"
    DEBUG: bool = False

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8008

    # Database
    DATABASE_URL: str  # postgresql+asyncpg://user:pass@host/db
    REDIS_URL: str = "redis://localhost:6379"

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # External Services
    BHEEMPASSPORT_URL: str
    COMPANY_CODE: str = "BHM001"
    OPENAI_API_KEY: str = ""

    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:3008",
        "http://localhost:5173",
        "https://dataviz.bheemkodee.com",
        "https://dataviz-staging.bheemkodee.com",
    ]

    class Config:
        env_file = ".env"

settings = Settings()
```

### 4.3 Database Configuration

**File:** `backend/app/database.py`

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_recycle=300,  # 5 minutes TTL
)

AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
```

### 4.4 API Router Organization

**File:** `backend/app/api/v1/api.py`

```python
from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth, connections, dashboards, charts, queries,
    datasets, transforms, semantic_models, kpi, ai
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(connections.router, prefix="/connections", tags=["connections"])
api_router.include_router(dashboards.router, prefix="/dashboards", tags=["dashboards"])
api_router.include_router(charts.router, prefix="/charts", tags=["charts"])
api_router.include_router(queries.router, prefix="/queries", tags=["queries"])
api_router.include_router(datasets.router, prefix="/datasets", tags=["datasets"])
api_router.include_router(transforms.router, prefix="/transforms", tags=["transforms"])
api_router.include_router(semantic_models.router, prefix="/models", tags=["semantic-models"])
api_router.include_router(kpi.router, prefix="/kpi", tags=["kpi"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
```

### 4.5 Service Layer Pattern

Services encapsulate business logic and database operations:

```
┌─────────────────────────────────────────────────────────────┐
│                     API Endpoints                           │
│  (connections.py, dashboards.py, charts.py, etc.)          │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      Services                               │
│  postgres_service, mysql_service, mongodb_service          │
│  transform_service, semantic_model_service, auth_service   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Database Layer                            │
│  SQLAlchemy Models, asyncpg, aiomysql, motor               │
└─────────────────────────────────────────────────────────────┘
```

### 4.6 Data Flow for Chart Rendering

```
1. Request: GET /charts/{chart_id}/render?filters=...
                    │
                    ▼
2. Load SavedChart from database
                    │
                    ▼
3. Get Connection credentials (decrypt password)
                    │
                    ▼
4. Build Query:
   ┌─────────────────────────────────────────┐
   │ Priority Order:                         │
   │ a) SemanticModel → Build from model     │
   │ b) TransformRecipe → Generate SQL       │
   │ c) query_config → Visual query config   │
   └─────────────────────────────────────────┘
                    │
                    ▼
5. Execute SQL on target database
                    │
                    ▼
6. Return: { columns, rows, execution_time, chart_data }
```

---

## 5. Frontend Architecture

### 5.1 Application Entry Point

**File:** `frontend/src/main.tsx`

```tsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { AuthProvider } from './contexts/AuthContext'
import App from './App'
import './index.css'

const queryClient = new QueryClient()

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <QueryClientProvider client={queryClient}>
        <AuthProvider>
          <App />
        </AuthProvider>
      </QueryClientProvider>
    </BrowserRouter>
  </React.StrictMode>,
)
```

### 5.2 Routing Configuration

**File:** `frontend/src/App.tsx`

```tsx
import { Routes, Route } from 'react-router-dom'
import Layout from './components/common/Layout'
import PrivateRoute from './components/auth/PrivateRoute'

// Pages
import LandingPage from './pages/LandingPage'
import Login from './pages/Login'
import HomePage from './pages/HomePage'
import DashboardBuilder from './pages/DashboardBuilder'
import ChartBuilder from './pages/ChartBuilder'
// ... more imports

function App() {
  return (
    <Routes>
      {/* Public Routes */}
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/auth/callback" element={<OAuthCallback />} />

      {/* Protected Routes */}
      <Route element={<PrivateRoute><Layout /></PrivateRoute>}>
        <Route path="/home" element={<HomePage />} />
        <Route path="/dashboards" element={<DashboardList />} />
        <Route path="/dashboards/new" element={<DashboardBuilder />} />
        <Route path="/dashboards/:id" element={<DashboardBuilder />} />
        <Route path="/charts/new" element={<ChartBuilder />} />
        <Route path="/charts/:id" element={<ChartBuilder />} />
        <Route path="/connections" element={<DataConnections />} />
        <Route path="/datasets" element={<Datasets />} />
        <Route path="/sql-lab" element={<SQLLab />} />
        <Route path="/transforms" element={<TransformBuilder />} />
        <Route path="/transforms/:id" element={<TransformBuilder />} />
        <Route path="/models" element={<SemanticModels />} />
        <Route path="/models/:id" element={<SemanticModels />} />
        <Route path="/kpis" element={<KPIs />} />
        <Route path="/kodee" element={<KodeeAnalytics />} />
        <Route path="/workflows" element={<Workflows />} />
      </Route>
    </Routes>
  )
}
```

### 5.3 API Client Configuration

**File:** `frontend/src/lib/api.ts`

```typescript
import axios from 'axios'

// Main API instance
const api = axios.create({
  baseURL: '/api/v1',
  headers: { 'Content-Type': 'application/json' }
})

// Request interceptor - Add JWT token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response interceptor - Handle 401 redirects
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// API Clients
export const connectionsApi = {
  list: () => api.get('/connections'),
  create: (data) => api.post('/connections', data),
  get: (id) => api.get(`/connections/${id}`),
  update: (id, data) => api.put(`/connections/${id}`, data),
  delete: (id) => api.delete(`/connections/${id}`),
  test: (id) => api.post(`/connections/${id}/test`),
  getTables: (id) => api.get(`/connections/${id}/tables`),
}

export const dashboardsApi = {
  list: () => api.get('/dashboards'),
  create: (data) => api.post('/dashboards', data),
  get: (id) => api.get(`/dashboards/${id}`),
  update: (id, data) => api.patch(`/dashboards/${id}`, data),
  delete: (id) => api.delete(`/dashboards/${id}`),
}

export const chartsApi = {
  list: () => api.get('/charts'),
  create: (data) => api.post('/charts', data),
  get: (id) => api.get(`/charts/${id}`),
  update: (id, data) => api.patch(`/charts/${id}`, data),
  delete: (id) => api.delete(`/charts/${id}`),
  render: (id, filters?) => api.get(`/charts/${id}/render`, { params: filters }),
}

// ... more API clients
```

### 5.4 Component Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         App.tsx                             │
│                    (Router Provider)                        │
└─────────────────────────────────────────────────────────────┘
                            │
            ┌───────────────┴───────────────┐
            ▼                               ▼
    ┌───────────────┐               ┌───────────────┐
    │ Public Routes │               │PrivateRoute   │
    │ (Landing,     │               │   (Auth Check)│
    │  Login, etc.) │               └───────────────┘
    └───────────────┘                       │
                                            ▼
                                    ┌───────────────┐
                                    │   Layout.tsx  │
                                    │ (Sidebar +    │
                                    │  Navbar)      │
                                    └───────────────┘
                                            │
                                            ▼
                            ┌───────────────────────────┐
                            │       Page Components      │
                            │  (ChartBuilder, Dashboard, │
                            │   SQLLab, etc.)            │
                            └───────────────────────────┘
                                            │
                                            ▼
                            ┌───────────────────────────┐
                            │    Shared Components      │
                            │  (ChartWidget, KPICard,   │
                            │   UI primitives)          │
                            └───────────────────────────┘
```

### 5.5 State Management Strategy

| State Type | Solution | Use Case |
|------------|----------|----------|
| **Server State** | TanStack Query | API data caching, refetching |
| **Global UI State** | Zustand | Theme, sidebar, user preferences |
| **Auth State** | AuthContext | User session, tokens |
| **Form State** | Local useState | Component-specific forms |
| **URL State** | React Router | Filters, pagination, IDs |

---

## 6. Database Design

### 6.1 Entity Relationship Diagram

```
┌──────────────────────────────────────────────────────────────────────────┐
│                            CONNECTIONS                                    │
├──────────────────────────────────────────────────────────────────────────┤
│ id (UUID, PK)                                                            │
│ name, type, host, port, database, username, encrypted_password           │
│ ssl_enabled, additional_config (JSONB)                                   │
│ status (connected|disconnected|error|syncing)                            │
│ table_count, last_sync_at                                                │
│ tenant_id, user_id, created_at, updated_at                               │
└──────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
                    ▼               ▼               ▼
┌────────────────────────┐  ┌─────────────┐  ┌─────────────────────────┐
│    TRANSFORM_RECIPES   │  │  DASHBOARDS │  │    SEMANTIC_MODELS      │
├────────────────────────┤  ├─────────────┤  ├─────────────────────────┤
│ id (UUID, PK)          │  │ id (PK)     │  │ id (UUID, PK)           │
│ connection_id (FK)     │  │ name        │  │ connection_id (FK)      │
│ name, description      │  │ description │  │ transform_recipe_id(FK) │
│ source_table, schema   │  │ icon        │  │ name, description       │
│ steps (JSONB)          │  │ layout(JSON)│  │ schema_name, table_name │
│ result_columns (JSONB) │  │ is_public   │  │ joined_transforms(JSON) │
│ cache_enabled, ttl     │  │ is_featured │  │ is_active               │
│ last_executed_at       │  │ user_id     │  │ user_id, timestamps     │
│ execution_time_ms      │  │ timestamps  │  └─────────────────────────┘
│ row_count              │  └─────────────┘              │
└────────────────────────┘          │           ┌───────┴───────┐
            │                       │           ▼               ▼
            │               ┌───────────────────┐  ┌─────────────────────┐
            │               │   SAVED_CHARTS    │  │ SEMANTIC_DIMENSIONS │
            │               ├───────────────────┤  ├─────────────────────┤
            │               │ id (UUID, PK)     │  │ id (UUID, PK)       │
            └───────────────│ dashboard_id (FK) │  │ model_id (FK)       │
                            │ connection_id     │  │ name, description   │
                            │ chart_type        │  │ column_name         │
                            │ chart_config(JSON)│  │ expression          │
                            │ query_config(JSON)│  │ display_format      │
                            │ semantic_model_id │  │ sort_order, hidden  │
                            │ transform_id      │  └─────────────────────┘
                            │ position_x/y/w/h  │
                            │ is_favorite       │  ┌─────────────────────┐
                            │ view_count        │  │ SEMANTIC_MEASURES   │
                            │ timestamps        │  ├─────────────────────┤
                            └───────────────────┘  │ id (UUID, PK)       │
                                                   │ model_id (FK)       │
┌──────────────────────────┐                       │ name, description   │
│      SAVED_KPIS          │                       │ column_name         │
├──────────────────────────┤                       │ aggregation         │
│ id (UUID, PK)            │                       │ display_format      │
│ name, description        │                       └─────────────────────┘
│ connection_id            │
│ semantic_model_id        │
│ transform_recipe_id      │
│ kpi_config (JSONB)       │
│ is_favorite, timestamps  │
└──────────────────────────┘

┌──────────────────────────┐
│   SUGGESTED_QUESTIONS    │
├──────────────────────────┤
│ id (UUID, PK)            │
│ question, description    │
│ icon, connection_id      │
│ query_config (JSONB)     │
│ chart_type, category     │
│ sort_order, is_active    │
└──────────────────────────┘
```

### 6.2 Connection Types (Enum)

```python
class ConnectionType(str, Enum):
    postgresql = "postgresql"
    mysql = "mysql"
    mongodb = "mongodb"
    bigquery = "bigquery"      # Not yet implemented
    snowflake = "snowflake"    # Not yet implemented
    redshift = "redshift"      # Not yet implemented
    clickhouse = "clickhouse"  # Not yet implemented
    elasticsearch = "elasticsearch"  # Not yet implemented
    csv = "csv"
    excel = "excel"
    rest = "rest"              # Not yet implemented
    cubejs = "cubejs"          # Not yet implemented
```

### 6.3 Transform Step Types

```python
TRANSFORM_STEP_TYPES = [
    "filter",       # WHERE clause
    "select",       # Column selection
    "rename",       # Column renaming
    "cast",         # Type conversion
    "sort",         # ORDER BY
    "limit",        # LIMIT
    "offset",       # OFFSET
    "deduplicate",  # DISTINCT
    "replace",      # Value replacement
    "fill_null",    # NULL handling
    "group_by",     # GROUP BY with aggregations
    "join",         # Table joins (planned)
    "union",        # UNION operations (planned)
    "computed",     # Computed columns
]
```

### 6.4 Aggregation Types

```python
class AggregationType(str, Enum):
    sum = "sum"
    count = "count"
    avg = "avg"
    min = "min"
    max = "max"
    count_distinct = "count_distinct"
```

---

## 7. API Reference

### 7.1 Authentication (`/api/v1/auth`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/login` | User login |
| POST | `/auth/register` | User registration |
| POST | `/auth/logout` | User logout |
| GET | `/auth/me` | Get current user |
| POST | `/auth/refresh` | Refresh token |

### 7.2 Connections (`/api/v1/connections`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/connections` | List all connections |
| POST | `/connections` | Create new connection |
| GET | `/connections/{id}` | Get connection details |
| PUT | `/connections/{id}` | Update connection |
| DELETE | `/connections/{id}` | Delete connection |
| POST | `/connections/{id}/test` | Test connection |
| POST | `/connections/test` | Test connection (without saving) |
| GET | `/connections/{id}/tables` | List tables with FK relationships |
| GET | `/connections/{id}/tables/{schema}/{table}/columns` | Get column info |
| GET | `/connections/{id}/tables/{schema}/{table}/preview` | Preview table data |
| POST | `/connections/upload-preview` | Upload CSV/Excel for preview |
| POST | `/connections/upload-confirm` | Confirm file upload |

**Create Connection Request:**
```json
{
  "name": "Production Database",
  "type": "postgresql",
  "host": "localhost",
  "port": 5432,
  "database": "myapp",
  "username": "user",
  "password": "secret",
  "ssl_enabled": true,
  "additional_config": {}
}
```

### 7.3 Dashboards (`/api/v1/dashboards`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/dashboards/home` | Home page content |
| GET | `/dashboards` | List dashboards |
| POST | `/dashboards` | Create dashboard |
| GET | `/dashboards/{id}` | Get dashboard with charts |
| PATCH | `/dashboards/{id}` | Update dashboard |
| DELETE | `/dashboards/{id}` | Delete dashboard |

**Create Dashboard Request:**
```json
{
  "name": "Sales Dashboard",
  "description": "Q4 sales metrics",
  "icon": "📊",
  "is_public": false,
  "is_featured": false,
  "layout": []
}
```

### 7.4 Charts (`/api/v1/charts`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/charts` | List all charts |
| POST | `/charts` | Create chart |
| GET | `/charts/{id}` | Get chart details |
| PATCH | `/charts/{id}` | Update chart |
| DELETE | `/charts/{id}` | Delete chart |
| GET | `/charts/{id}/render` | Render chart data |
| POST | `/charts/{id}/render` | Render with filters |
| GET | `/charts/{id}/filter-options` | Get filter options |
| POST | `/charts/{id}/favorite` | Toggle favorite |

**Create Chart Request:**
```json
{
  "name": "Monthly Sales",
  "description": "Sales by month",
  "dashboard_id": "uuid",
  "connection_id": "uuid",
  "chart_type": "bar",
  "chart_config": {
    "title": { "text": "Monthly Sales" },
    "xAxis": { "type": "category" },
    "yAxis": { "type": "value" },
    "series": [{ "type": "bar" }]
  },
  "query_config": {
    "dimensions": [{ "column": "month", "alias": "Month" }],
    "measures": [{ "column": "revenue", "aggregation": "sum", "alias": "Revenue" }],
    "filters": [],
    "sort": [{ "column": "month", "direction": "asc" }],
    "limit": 12
  }
}
```

### 7.5 Queries (`/api/v1/queries`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/queries/execute` | Execute SQL query |
| POST | `/queries/preview` | Preview query (limited) |
| GET | `/queries/saved` | List saved queries |
| POST | `/queries/saved` | Save query |
| GET | `/queries/saved/{id}` | Get saved query |
| DELETE | `/queries/saved/{id}` | Delete saved query |

**Execute Query Request:**
```json
{
  "connection_id": "uuid",
  "sql": "SELECT * FROM sales WHERE year = 2024",
  "limit": 1000
}
```

### 7.6 Transforms (`/api/v1/transforms`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/transforms` | List transform recipes |
| POST | `/transforms` | Create transform recipe |
| GET | `/transforms/{id}` | Get transform details |
| PUT | `/transforms/{id}` | Update transform |
| DELETE | `/transforms/{id}` | Delete transform |
| POST | `/transforms/{id}/execute` | Execute transform preview |
| POST | `/transforms/{id}/validate` | Validate transform steps |

**Create Transform Request:**
```json
{
  "name": "Clean Sales Data",
  "description": "Filter and aggregate sales",
  "connection_id": "uuid",
  "source_table": "raw_sales",
  "source_schema": "public",
  "steps": [
    { "type": "filter", "config": { "column": "status", "operator": "=", "value": "completed" } },
    { "type": "select", "config": { "columns": ["date", "product", "amount"] } },
    { "type": "group_by", "config": { "group_columns": ["date", "product"], "aggregations": [{ "column": "amount", "function": "sum" }] } }
  ]
}
```

### 7.7 Semantic Models (`/api/v1/models`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/models` | List semantic models |
| POST | `/models` | Create semantic model |
| GET | `/models/{id}` | Get model details |
| PUT | `/models/{id}` | Update model |
| DELETE | `/models/{id}` | Delete model |
| POST | `/models/{id}/dimensions` | Add dimension |
| POST | `/models/{id}/measures` | Add measure |
| POST | `/models/{id}/joins` | Add join |
| GET | `/models/{id}/preview` | Preview model query |

### 7.8 KPIs (`/api/v1/kpi`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/kpi/calculate` | Calculate single KPI |
| POST | `/kpi/batch` | Calculate multiple KPIs |

**Calculate KPI Request:**
```json
{
  "connection_id": "uuid",
  "metric": "revenue",
  "aggregation": "sum",
  "filters": [{ "column": "year", "value": "2024" }],
  "comparison": {
    "type": "previous_period",
    "period": "month"
  }
}
```

---

## 8. Authentication & Security

### 8.1 Authentication Flow

```
┌─────────────┐       ┌─────────────────┐       ┌─────────────────┐
│   Frontend  │       │  Bheem DataViz  │       │ Bheem Passport  │
│   (React)   │       │    Backend      │       │   (OAuth)       │
└─────────────┘       └─────────────────┘       └─────────────────┘
      │                       │                         │
      │  1. Login Request     │                         │
      │──────────────────────>│                         │
      │                       │  2. Redirect to OAuth   │
      │                       │────────────────────────>│
      │                       │                         │
      │<──────────────────────────────────────────────────
      │              3. OAuth Consent Page              │
      │                       │                         │
      │  4. Authorization Code                          │
      │──────────────────────>│                         │
      │                       │  5. Exchange for Token  │
      │                       │────────────────────────>│
      │                       │<────────────────────────│
      │                       │      6. JWT Token       │
      │<──────────────────────│                         │
      │      7. JWT Token     │                         │
      │                       │                         │
```

### 8.2 JWT Token Structure

```json
{
  "sub": "user_id",
  "email": "user@example.com",
  "name": "John Doe",
  "company_code": "BHM001",
  "workspace_id": "uuid",
  "roles": ["admin", "editor"],
  "exp": 1735689600,
  "iat": 1735603200
}
```

### 8.3 Security Measures

| Measure | Implementation |
|---------|----------------|
| **Password Encryption** | Fernet symmetric encryption for stored DB passwords |
| **Transport Security** | HTTPS only in production |
| **CORS** | Whitelist of allowed origins |
| **Rate Limiting** | Planned (not yet implemented) |
| **Query Timeout** | 30-second limit on transform/query execution |
| **SQL Injection** | Parameterized queries via SQLAlchemy |
| **XSS Prevention** | React's built-in escaping |

### 8.4 Encryption Service

**File:** `backend/app/services/encryption_service.py`

```python
from cryptography.fernet import Fernet
import hashlib
import base64

class EncryptionService:
    def __init__(self, secret_key: str):
        # Derive key from secret
        key = hashlib.sha256(secret_key.encode()).digest()
        self.fernet = Fernet(base64.urlsafe_b64encode(key))

    def encrypt(self, data: str) -> str:
        return self.fernet.encrypt(data.encode()).decode()

    def decrypt(self, encrypted: str) -> str:
        return self.fernet.decrypt(encrypted.encode()).decode()
```

---

## 9. Docker Configuration

### 9.1 Development Setup

**File:** `docker/docker-compose.dev.yml`

```yaml
version: '3.8'

services:
  frontend:
    build:
      context: ../frontend
      dockerfile: Dockerfile
    ports:
      - "3008:3008"
    volumes:
      - ../frontend:/app
      - /app/node_modules
    environment:
      - VITE_API_URL=http://localhost:8008
    depends_on:
      - backend

  backend:
    build:
      context: ../backend
      dockerfile: Dockerfile
    ports:
      - "8008:8008"
    volumes:
      - ../backend:/app
    environment:
      - DATABASE_URL=postgresql+asyncpg://dataviz:dataviz@db:5432/dataviz
      - REDIS_URL=redis://redis:6379
      - SECRET_KEY=dev-secret-key
    depends_on:
      - db
      - redis
    command: uvicorn main:app --host 0.0.0.0 --port 8008 --reload

  db:
    image: postgres:15-alpine
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_USER=dataviz
      - POSTGRES_PASSWORD=dataviz
      - POSTGRES_DB=dataviz
    volumes:
      - pgdata:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  pgdata:
```

### 9.2 Production Setup

**File:** `docker/docker-compose.yml`

```yaml
version: '3.8'

services:
  frontend:
    build:
      context: ../frontend
      dockerfile: Dockerfile.prod
      args:
        - VITE_API_URL=${VITE_API_URL}
    ports:
      - "3008:80"
    depends_on:
      - backend

  backend:
    build:
      context: ../backend
      dockerfile: Dockerfile
    ports:
      - "8008:8008"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - SECRET_KEY=${SECRET_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - BHEEMPASSPORT_URL=${BHEEMPASSPORT_URL}
    depends_on:
      - db
      - redis

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - POSTGRES_DB=${DB_NAME}
    volumes:
      - pgdata:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine

volumes:
  pgdata:
```

### 9.3 Backend Dockerfile

**File:** `backend/Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

EXPOSE 8008

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8008"]
```

### 9.4 Frontend Production Dockerfile

**File:** `frontend/Dockerfile.prod`

```dockerfile
# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

ARG VITE_API_URL
ENV VITE_API_URL=${VITE_API_URL}

RUN npm run build

# Production stage
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

---

## 10. Development Guide

### 10.1 Prerequisites

- Node.js 20+
- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 15+ (or use Docker)
- Redis 7+ (or use Docker)

### 10.2 Local Setup

**1. Clone Repository:**
```bash
git clone https://github.com/your-org/bheem-dataviz.git
cd bheem-dataviz
```

**2. Backend Setup:**
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
DATABASE_URL=postgresql+asyncpg://dataviz:dataviz@localhost:5432/dataviz
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-dev-secret-key
BHEEMPASSPORT_URL=https://platform.bheem.co.uk/api/v1/auth
COMPANY_CODE=BHM001
EOF

# Run database migrations
alembic upgrade head

# Start development server
uvicorn main:app --reload --port 8008
```

**3. Frontend Setup:**
```bash
cd frontend

# Install dependencies
npm install

# Create .env file
cat > .env << EOF
VITE_API_URL=http://localhost:8008
VITE_BHEEMFLOW_API_URL=https://platform.bheem.co.uk/api/v1
EOF

# Start development server
npm run dev
```

**4. Using Docker (Recommended):**
```bash
# Development
docker-compose -f docker/docker-compose.dev.yml up

# Production build
docker-compose -f docker/docker-compose.yml up -d
```

### 10.3 Database Migrations

```bash
cd backend

# Create new migration
alembic revision --autogenerate -m "Add new table"

# Apply migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1

# View migration history
alembic history
```

### 10.4 Code Style

**Frontend:**
- ESLint + Prettier
- Run: `npm run lint` and `npm run format`

**Backend:**
- Black for formatting
- isort for imports
- Run: `black .` and `isort .`

### 10.5 Testing

**Frontend:**
```bash
npm run test        # Run tests
npm run test:watch  # Watch mode
npm run test:coverage  # Coverage report
```

**Backend:**
```bash
pytest              # Run tests
pytest --cov=app    # With coverage
pytest -v           # Verbose output
```

---

## 11. Deployment

### 11.1 Production Checklist

- [ ] Set strong `SECRET_KEY`
- [ ] Configure `DATABASE_URL` for production PostgreSQL
- [ ] Set up Redis for caching
- [ ] Configure `CORS_ORIGINS` for production domains
- [ ] Enable HTTPS
- [ ] Set up monitoring (Prometheus + Grafana)
- [ ] Configure log aggregation
- [ ] Set up backup strategy for PostgreSQL
- [ ] Configure rate limiting
- [ ] Review security headers

### 11.2 Environment Variables

**Required:**
```env
# Backend
DATABASE_URL=postgresql+asyncpg://user:pass@host/db
SECRET_KEY=your-production-secret
BHEEMPASSPORT_URL=https://platform.bheem.co.uk/api/v1/auth
COMPANY_CODE=BHM001

# Frontend (build-time)
VITE_API_URL=https://api.dataviz.bheemkodee.com
```

**Optional:**
```env
REDIS_URL=redis://redis:6379
OPENAI_API_KEY=sk-...
DEBUG=false
```

### 11.3 PM2 Configuration

**File:** `ecosystem.config.js`

```javascript
module.exports = {
  apps: [
    {
      name: 'dataviz-backend',
      cwd: './backend',
      script: 'uvicorn',
      args: 'main:app --host 0.0.0.0 --port 8008',
      interpreter: 'python3',
      env: {
        NODE_ENV: 'production',
      },
    },
    {
      name: 'dataviz-frontend',
      cwd: './frontend',
      script: 'npm',
      args: 'run preview',
      env: {
        NODE_ENV: 'production',
      },
    },
  ],
}
```

### 11.4 Nginx Configuration

**File:** `frontend/nginx.conf`

```nginx
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    # SPA routing
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API proxy (if needed)
    location /api {
        proxy_pass http://backend:8008;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Static assets caching
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

---

## 12. Key Features

### 12.1 Supported Chart Types

| Category | Chart Types |
|----------|-------------|
| **Basic** | Bar, Line, Area, Pie, Donut |
| **Advanced** | Scatter, Heatmap, Treemap, Sunburst, Radar |
| **Financial** | Candlestick (OHLC), Waterfall |
| **Statistical** | Box Plot, Funnel, Gauge |
| **Flow** | Sankey |
| **Geographic** | Map (with geospatial data) |
| **Data** | Table, KPI Card |

### 12.2 Data Sources

| Source | Status | Driver |
|--------|--------|--------|
| PostgreSQL | Implemented | asyncpg |
| MySQL | Implemented | aiomysql |
| MongoDB | Implemented | motor |
| CSV | Implemented | pandas |
| Excel | Implemented | openpyxl |
| BigQuery | Planned | google-cloud-bigquery |
| Snowflake | Planned | snowflake-connector |
| Redshift | Planned | redshift-connector |
| ClickHouse | Planned | clickhouse-driver |

### 12.3 Transform Operations

| Category | Operations |
|----------|------------|
| **Column** | Select, Rename, Drop, Reorder, Cast, Computed |
| **Row** | Filter, Sort, Limit, Offset, Deduplicate |
| **Cleaning** | Replace Values, Fill Null, Type Conversion |
| **Aggregation** | Group By, Sum, Count, Avg, Min, Max |

### 12.4 Semantic Layer

The semantic layer provides:
- Business-friendly naming for columns
- Pre-defined aggregations and metrics
- Consistent calculations across dashboards
- Hierarchies for drill-down analysis
- Multi-table join definitions

---

## 13. Roadmap

### Phase 1: Core Platform (Current)
- [x] Data connectors (PostgreSQL, MySQL, MongoDB, CSV, Excel)
- [x] Dashboard builder with drag-and-drop
- [x] Chart editor with 40+ chart types
- [x] SQL Lab with Monaco editor
- [x] Semantic layer with dimensions and measures
- [x] Transform recipe builder
- [x] KPI cards with trends
- [x] BheemFlow integration
- [ ] File upload improvements
- [ ] Advanced filtering

### Phase 2: AI Features (Next)
- [ ] Natural language to SQL (Kodee)
- [ ] Automatic insights generation
- [ ] Anomaly detection
- [ ] Smart chart recommendations
- [ ] Data quality analysis
- [ ] AI-powered chat interface

### Phase 3: Enterprise Features
- [ ] Scheduled reports & alerts
- [ ] Email distribution
- [ ] Advanced permissions (row-level security)
- [ ] Audit logging
- [ ] SSO (SAML, OIDC)
- [ ] Multi-tenancy

### Phase 4: Advanced
- [ ] Real-time collaboration
- [ ] Mobile apps (iOS, Android)
- [ ] Embedded analytics SDK
- [ ] Plugin architecture
- [ ] dbt integration
- [ ] DataOps workflows

---

## 14. Troubleshooting

### 14.1 Common Issues

**Connection Test Fails:**
```
Error: Connection refused
```
- Verify host, port, and credentials
- Check if database server is running
- Ensure firewall allows connection
- For Docker, use service name (e.g., `db` not `localhost`)

**CORS Errors:**
```
Access-Control-Allow-Origin error
```
- Add your domain to `CORS_ORIGINS` in backend config
- Ensure protocol matches (http vs https)

**Query Timeout:**
```
Error: Query execution timeout
```
- Optimize your query with indexes
- Add filters to reduce data volume
- Increase timeout (not recommended)

**File Upload Fails:**
```
Error: File too large
```
- Maximum file size: 50MB
- Split large files
- Use database connection instead

### 14.2 Debug Mode

**Backend:**
```bash
# Enable debug logging
DEBUG=true uvicorn main:app --reload
```

**Frontend:**
```bash
# Enable verbose logging
VITE_DEBUG=true npm run dev
```

### 14.3 Health Checks

**API Health:**
```bash
curl http://localhost:8008/api/v1/health
```

**Database Health:**
```bash
curl http://localhost:8008/api/v1/health/db
```

### 14.4 Logs

**Docker Compose:**
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
```

**PM2:**
```bash
pm2 logs dataviz-backend
pm2 logs dataviz-frontend
```

---

## Appendix

### A. File Size Analysis

| File | Size | Complexity |
|------|------|------------|
| `frontend/src/pages/ChartBuilder.tsx` | 166 KB | High |
| `frontend/src/pages/TransformBuilder.tsx` | 85 KB | High |
| `frontend/src/pages/DashboardBuilder.tsx` | 57 KB | Medium |
| `frontend/src/pages/SemanticModels.tsx` | 71 KB | Medium |
| `backend/app/services/mongodb_service.py` | 28 KB | Medium |
| `backend/app/services/transform_service.py` | 27 KB | Medium |

### B. API Response Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 422 | Validation Error |
| 500 | Server Error |

### C. Environment Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes | - | PostgreSQL connection string |
| `SECRET_KEY` | Yes | - | Encryption key |
| `REDIS_URL` | No | `redis://localhost:6379` | Redis connection |
| `OPENAI_API_KEY` | No | - | OpenAI API key |
| `BHEEMPASSPORT_URL` | Yes | - | Auth service URL |
| `COMPANY_CODE` | Yes | `BHM001` | Company identifier |
| `DEBUG` | No | `false` | Debug mode |

---

**Document Version:** 1.0.0
**Last Updated:** 2026-01-28
**Maintained By:** Bheem Development Team
