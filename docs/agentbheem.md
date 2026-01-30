# Bheem DataViz - Project Memory

## Overview
AI-Powered Business Intelligence & Data Visualization Platform - part of the Bheem Platform ecosystem.

## Live URLs
- **Production:** https://dataviz.bheemkodee.com
- **API:** https://api.dataviz.bheemkodee.com
- **BheemFlow API:** https://platform.bheem.co.uk/api/v1

## Repository
- **GitHub:** https://github.com/Bheem-Platform/bheem-dataviz
- **Organization:** Bheem-Platform

## Tech Stack

### Frontend
- **Framework:** React 18 with TypeScript
- **Build Tool:** Vite 5
- **Styling:** TailwindCSS 3.4
- **Charts:** Apache ECharts (echarts-for-react)
- **State:** Zustand
- **HTTP Client:** Axios
- **UI Components:** Radix UI primitives
- **Icons:** Lucide React
- **Code Editor:** Monaco Editor
- **Drag & Drop:** dnd-kit
- **Dashboard Grid:** GridStack

### Backend
- **Framework:** FastAPI (Python)
- **Database:** PostgreSQL
- **Cache:** Redis

## Key Features

### Pages
1. **LandingPage** (`/`) - Marketing page with USPs, competitor comparison, pricing
2. **DashboardList** (`/dashboards`) - List of user dashboards
3. **DashboardBuilder** (`/dashboards/:id`) - Drag-and-drop dashboard editor
4. **ChartGallery** (`/gallery`) - Browse 40+ chart types
5. **Explore** (`/explore`) - Ad-hoc data exploration
6. **SQLLab** (`/sql-lab`) - SQL editor with AI assistance
7. **KodeeAnalytics** (`/kodee`) - AI-powered insights
8. **Workflows** (`/workflows`) - BheemFlow automation integration
9. **DataConnections** (`/connections`) - Database connection management
10. **Datasets** (`/datasets`) - Dataset management
11. **ChartBuilder** (`/charts/:id`) - Individual chart editor
12. **AIChat** (`/ai`) - Conversational analytics

### Integrations
- **BheemFlow** - Workflow automation (module: 'dataviz')
- **Kodee AI** - Natural language queries
- **Cube.js** - Semantic layer

## API Structure

### Main API (`/api/v1`)
```typescript
// lib/api.ts
connectionsApi  - CRUD for data connections
dashboardsApi   - CRUD for dashboards
datasetsApi     - CRUD for datasets
chartsApi       - CRUD for charts
queriesApi      - Execute SQL queries
aiApi           - AI/NL query endpoints
```

### BheemFlow API
```typescript
// lib/api.ts - workflowsApi
workflowsApi.list()           - List workflows (module=dataviz)
workflowsApi.execute(id)      - Execute workflow
workflowsApi.getExecutions()  - Get execution history
workflowsApi.getAnalytics()   - Get workflow analytics
```

## Environment Variables

```env
# Frontend (.env)
VITE_API_URL=https://api.dataviz.bheemkodee.com
VITE_BHEEMFLOW_API_URL=https://platform.bheem.co.uk/api/v1

# Backend
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
```

## Deployment

### PM2 (Current Production)
```bash
pm2 restart dataviz-frontend
pm2 restart dataviz-backend
```

### Docker
```bash
# Development
docker build -t bheem-dataviz:dev -f frontend/Dockerfile frontend/
docker run -p 5173:5173 bheem-dataviz:dev

# Production
docker build -t bheem-dataviz:prod -f frontend/Dockerfile.prod \
  --build-arg VITE_API_URL=https://api.dataviz.bheemkodee.com frontend/
docker run -p 80:80 bheem-dataviz:prod
```

### Server
- **IP:** 46.62.171.247
- **User:** root
- **SSH Key:** ~/.ssh/sundeep

## Design System

### Landing Page Theme
- **Style:** Light & clean with gradient accents
- **Colors:** Indigo/Violet gradients (`from-indigo-600 to-violet-600`)
- **Background:** White (`bg-white`)
- **Typography:** Inter font family
- **Components:** Rounded corners (2xl), shadows, hover effects

### App Theme
- **Style:** Dark sidebar, light content area
- **Primary:** Indigo/Blue tones

## Competitors
- Power BI ($10/user/month)
- Tableau ($70/user/month)
- Looker (custom pricing)

## USPs
1. **Flat pricing** - $49/month for unlimited users (vs per-user pricing)
2. **AI-powered** - Kodee AI for natural language queries
3. **Workflow automation** - BheemFlow integration
4. **Self-hosted option** - Enterprise can deploy on-prem
5. **Semantic layer** - Cube.js built-in
6. **White-label** - Enterprise can rebrand

## Pricing Tiers
1. **Starter** - $0/forever (5 dashboards, 3 sources)
2. **Pro** - $49/month (unlimited, AI, SQL Lab, BheemFlow)
3. **Enterprise** - Custom (self-hosted, SSO, white-label)

## Related Repositories
- **bheem-platform** (monorepo): https://github.com/Bheem-Platform/bheem-platform
- **bheem-workspace**: https://github.com/Bheem-Platform/bheem-workspace
- **bheem-academy**: https://github.com/Bheem-Platform/bheem-academy

## File Structure
```
bheem-dataviz/
├── frontend/
│   ├── src/
│   │   ├── App.tsx              # Router setup
│   │   ├── main.tsx             # Entry point
│   │   ├── index.css            # Global styles + Tailwind
│   │   ├── components/
│   │   │   ├── common/
│   │   │   │   └── Layout.tsx   # App shell with sidebar
│   │   │   └── dashboard/
│   │   │       └── ChartWidget.tsx
│   │   ├── pages/
│   │   │   ├── LandingPage.tsx  # Marketing page
│   │   │   ├── DashboardList.tsx
│   │   │   ├── DashboardBuilder.tsx
│   │   │   ├── ChartGallery.tsx
│   │   │   ├── Explore.tsx
│   │   │   ├── SQLLab.tsx
│   │   │   ├── KodeeAnalytics.tsx
│   │   │   ├── Workflows.tsx
│   │   │   └── ...
│   │   ├── lib/
│   │   │   ├── api.ts           # API clients
│   │   │   └── utils.ts         # Utilities (cn, etc.)
│   │   └── types/
│   │       └── index.ts         # TypeScript types
│   ├── Dockerfile               # Dev container
│   ├── Dockerfile.prod          # Prod container (nginx)
│   ├── nginx.conf               # SPA routing
│   ├── package.json
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   └── vite.config.ts
├── backend/
├── sdk/
├── docs/
├── README.md
└── CLAUDE.md                    # This file
```

## Common Commands

```bash
# Development
cd frontend && npm run dev

# Build
cd frontend && npm run build

# Deploy to production
ssh root@46.62.171.247
cd /root/bheem-platform/modules/bheem-dataviz/frontend
npm run build && pm2 restart dataviz-frontend

# Check logs
pm2 logs dataviz-frontend
```

## Notes
- tsconfig.json has `noUnusedLocals: false` to allow unused imports during development
- Landing page was redesigned to be different from bheemkodee.com (dark/purple) and socialselling.ai (FOMO style)
- BheemFlow uses workspace_id from localStorage (default: 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11')
