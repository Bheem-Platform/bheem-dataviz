# Dataviz Test Databases

## Quick Start

```bash
# Start all databases
docker-compose -f docker-compose.databases.yml up -d

# Check status
docker-compose -f docker-compose.databases.yml ps

# Stop all
docker-compose -f docker-compose.databases.yml down

# Stop and remove volumes (reset data)
docker-compose -f docker-compose.databases.yml down -v
```

---

## Connection Details

### PostgreSQL
| Property | Value |
|----------|-------|
| Host | localhost |
| Port | 5432 |
| Database | dataviz_test |
| Username | dataviz |
| Password | dataviz123 |
| Connection String | postgresql://dataviz:dataviz123@localhost:5432/dataviz_test |

### MySQL
| Property | Value |
|----------|-------|
| Host | localhost |
| Port | 3306 |
| Database | dataviz_test |
| Username | dataviz |
| Password | dataviz123 |
| Root Password | root123 |
| Connection String | mysql://dataviz:dataviz123@localhost:3306/dataviz_test |

### MongoDB
| Property | Value |
|----------|-------|
| Host | localhost |
| Port | 27017 |
| Database | dataviz_test |
| Username | dataviz |
| Password | dataviz123 |
| Connection String | mongodb://dataviz:dataviz123@localhost:27017/dataviz_test?authSource=admin |

### MariaDB
| Property | Value |
|----------|-------|
| Host | localhost |
| Port | 3307 |
| Database | dataviz_test |
| Username | dataviz |
| Password | dataviz123 |
| Root Password | root123 |
| Connection String | mysql://dataviz:dataviz123@localhost:3307/dataviz_test |

### Redis
| Property | Value |
|----------|-------|
| Host | localhost |
| Port | 6380 |
| Connection String | redis://localhost:6380 |

---

## CLI Access

```bash
# PostgreSQL
docker exec -it dataviz-postgres psql -U dataviz -d dataviz_test

# MySQL
docker exec -it dataviz-mysql mysql -u dataviz -pdataviz123 dataviz_test

# MongoDB
docker exec -it dataviz-mongodb mongosh -u dataviz -p dataviz123 --authenticationDatabase admin dataviz_test

# MariaDB
docker exec -it dataviz-mariadb mariadb -u dataviz -pdataviz123 dataviz_test

# Redis
docker exec -it dataviz-redis redis-cli
```

---

## Sample Data

### PostgreSQL Sample
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

INSERT INTO users (name, email) VALUES
    ("John Doe", "john@example.com"),
    ("Jane Smith", "jane@example.com");

CREATE TABLE sales (
    id SERIAL PRIMARY KEY,
    product VARCHAR(100),
    amount DECIMAL(10,2),
    sale_date DATE
);

INSERT INTO sales (product, amount, sale_date) VALUES
    ("Widget A", 99.99, "2026-01-01"),
    ("Widget B", 149.99, "2026-01-02"),
    ("Widget C", 199.99, "2026-01-03");
```

### MongoDB Sample
```javascript
db.users.insertMany([
    { name: "John Doe", email: "john@example.com", age: 30 },
    { name: "Jane Smith", email: "jane@example.com", age: 25 }
]);

db.sales.insertMany([
    { product: "Widget A", amount: 99.99, date: new Date("2026-01-01") },
    { product: "Widget B", amount: 149.99, date: new Date("2026-01-02") }
]);
```

---

## Future Databases

To add later:
- Microsoft SQL Server (requires more resources)
- Oracle Database XE (licensing)
- SQLite (file-based, no container needed)
- Firebase Emulator (uncomment in docker-compose)

---

*Last Updated: January 23, 2026*
