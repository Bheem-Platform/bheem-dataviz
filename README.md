# Bheem DataViz

AI-Powered Business Intelligence & Data Visualization Platform

## Features

- **40+ Chart Types** - Bar, line, pie, heatmaps, sankey, geospatial maps powered by Apache ECharts
- **Kodee AI Assistant** - Ask questions in plain English, get instant visualizations
- **SQL Lab** - Full SQL editor with autocomplete and AI assistance
- **BheemFlow Automation** - Schedule reports, set alerts, automate data pipelines
- **Semantic Layer** - Define metrics once with Cube.js, consistent calculations everywhere
- **50+ Data Connectors** - PostgreSQL, MySQL, BigQuery, Snowflake, MongoDB, REST APIs

## Quick Start

### Frontend (React + Vite)

```bash
cd frontend
npm install
npm run dev
```

### Backend (FastAPI)

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Docker

```bash
# Development
docker build -t bheem-dataviz:dev -f frontend/Dockerfile frontend/
docker run -p 5173:5173 bheem-dataviz:dev

# Production
docker build -t bheem-dataviz:prod -f frontend/Dockerfile.prod frontend/
docker run -p 80:80 bheem-dataviz:prod
```

## Environment Variables

```env
VITE_API_URL=https://api.dataviz.bheemkodee.com
VITE_BHEEMFLOW_API_URL=https://platform.bheem.co.uk/api/v1
```

## Architecture

```
bheem-dataviz/
├── frontend/          # React + Vite + TailwindCSS
│   ├── src/
│   │   ├── pages/     # Landing, Dashboards, Explore, SQL Lab, etc.
│   │   ├── components/
│   │   └── lib/       # API clients, utilities
│   ├── Dockerfile
│   └── Dockerfile.prod
├── backend/           # FastAPI
├── sdk/               # Client SDKs
└── docs/              # Documentation
```

## Live Demo

https://dataviz.bheemkodee.com

## License

Proprietary - Bheem Platform
