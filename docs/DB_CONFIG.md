# Database Configurations for Developers

> **Note:** Databases run on HOST server. From inside dev container, use host IP: **172.17.0.1** or **65.108.109.167**

---

## Test Databases

### PostgreSQL
```
Host: 172.17.0.1
Port: 5432
Database: dataviz_test
Username: dataviz
Password: dataviz123
Connection: postgresql://dataviz:dataviz123@172.17.0.1:5432/dataviz_test
```

### MySQL
```
Host: 172.17.0.1
Port: 3306
Database: dataviz_test
Username: dataviz
Password: dataviz123
Connection: mysql://dataviz:dataviz123@172.17.0.1:3306/dataviz_test
```

### MongoDB
```
Host: 172.17.0.1
Port: 27017
Database: dataviz_test
Username: dataviz
Password: dataviz123
Connection: mongodb://dataviz:dataviz123@172.17.0.1:27017/dataviz_test?authSource=admin
```

### MariaDB
```
Host: 172.17.0.1
Port: 3307
Database: dataviz_test
Username: dataviz
Password: dataviz123
Connection: mysql://dataviz:dataviz123@172.17.0.1:3307/dataviz_test
```

### Redis
```
Host: 172.17.0.1
Port: 6380
Connection: redis://172.17.0.1:6380
```

---

## Quick Test from Container

```bash
# Test PostgreSQL
psql postgresql://dataviz:dataviz123@172.17.0.1:5432/dataviz_test

# Test MongoDB
mongosh "mongodb://dataviz:dataviz123@172.17.0.1:27017/dataviz_test?authSource=admin"

# Test Redis
redis-cli -h 172.17.0.1 -p 6380 ping
```

---

## Python Connection Examples

```python
# PostgreSQL (asyncpg)
DATABASE_URL = "postgresql+asyncpg://dataviz:dataviz123@172.17.0.1:5432/dataviz_test"

# MySQL (aiomysql)
DATABASE_URL = "mysql+aiomysql://dataviz:dataviz123@172.17.0.1:3306/dataviz_test"

# MongoDB (motor)
MONGO_URL = "mongodb://dataviz:dataviz123@172.17.0.1:27017/dataviz_test?authSource=admin"

# Redis (aioredis)
REDIS_URL = "redis://172.17.0.1:6380"
```

---

## Container Management (Run from HOST only)

```bash
# SSH to host first
ssh root@65.108.109.167

# Then manage containers
docker ps | grep dataviz
docker restart dataviz-postgres
docker logs dataviz-mysql
```

---

*Databases running on: 65.108.109.167*
*Last Updated: January 23, 2026*
