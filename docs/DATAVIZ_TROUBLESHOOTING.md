# Dataviz Troubleshooting Guide

## Common Issues & Fixes

### 1. Backend API Not Responding (503/502/000)

**Symptom:** 
- https://dataviz-api-staging.bheemkodee.com returns error
- curl http://localhost:8008 returns 000

**Root Cause:**
Docker port mapping expects internal port 8000, but ecosystem.config.js may have port 8008.

**Port Mapping:**
| Internal Port | External Port | Service |
|---------------|---------------|---------|
| 3000 | 3008 | Frontend |
| 8000 | 8008 | Backend |
| 8080 | 8108 | Code-server IDE |

**Fix:**
```bash
# Check ecosystem.config.js
cat /home/coder/bheem-dataviz/ecosystem.config.js | grep -A5 dataviz-backend

# If port is 8008, change to 8000:
cd /home/coder/bheem-dataviz
sed -i "s/--port 8008/--port 8000/g" ecosystem.config.js

# Restart backend
pm2 delete dataviz-backend
pm2 start ecosystem.config.js --only dataviz-backend
pm2 save
```

---

### 2. Services Not Starting After Container Restart

**Symptom:**
- PM2 shows empty list after container restart
- Services not auto-starting

**Fix:**
```bash
cd /home/coder/bheem-dataviz
pm2 start ecosystem.config.js
pm2 save
```

---

### 3. 403 Forbidden on External URLs

**Symptom:**
- https://dataviz-staging.bheemkodee.com returns 403
- https://dataviz-api-staging.bheemkodee.com returns 403

**Root Cause:**
Traefik IP whitelist blocking access.

**Fix:**
Edit Traefik config on 37.27.40.113:
```bash
# SSH to Traefik server
ssh root@37.27.40.113

# Edit config to remove IP whitelist
nano /opt/traefik/dynamic/dataviz-staging.yml

# Remove these lines from routers:
#   middlewares:
#     - agentbheem-ipwhitelist@file
```

---

### 4. Database Connection Issues

**Symptom:**
- "connection_lost" errors
- Database queries failing

**Check:**
```bash
# Test DB connectivity
pg_isready -h 65.109.167.218 -p 5432

# Check HAProxy connections (from DB server)
ssh root@65.109.167.218
echo "show stat" | socat /var/run/haproxy/admin.sock stdio | grep patroni
```

---

## Service URLs

| Service | URL | Port |
|---------|-----|------|
| Frontend | https://dataviz-staging.bheemkodee.com | 3008 |
| Backend API | https://dataviz-api-staging.bheemkodee.com | 8008 |
| API Docs | https://dataviz-api-staging.bheemkodee.com/docs | 8008 |
| IDE | https://dev8.bheem.cloud:8108 | 8108 |

---

## Quick Commands

```bash
# Check PM2 status
pm2 list

# View logs
pm2 logs dataviz-backend --lines 50
pm2 logs dataviz-frontend --lines 50

# Restart all services
pm2 restart all

# Full restart
pm2 delete all
cd /home/coder/bheem-dataviz
pm2 start ecosystem.config.js
pm2 save
```

---

*Last Updated: January 23, 2026*
