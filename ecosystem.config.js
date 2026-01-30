module.exports = {
  apps: [
    {
      name: "dataviz-frontend",
      cwd: "/home/coder/bheem-dataviz/frontend",
      script: "npm",
      args: "run dev -- --host 0.0.0.0 --port 3008",
      watch: false,
      autorestart: true,
      max_restarts: 10,
      restart_delay: 3000,
      env: {
        NODE_ENV: "development"
      }
    },
    {
      name: "dataviz-backend",
      cwd: "/home/coder/bheem-dataviz/backend",
      script: "/home/coder/bheem-dataviz/backend/venv/bin/uvicorn",
      args: "main:app --host 0.0.0.0 --port 8008 --reload",
      watch: false,
      autorestart: true,
      max_restarts: 10,
      restart_delay: 3000,
      interpreter: "none",
      env: {
        PATH: "/home/coder/bheem-dataviz/backend/venv/bin:/usr/local/bin:/usr/bin:/bin"
      }
    }
  ]
}
