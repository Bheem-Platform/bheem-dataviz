"""
Database Configuration for Dataviz Development
==============================================
Use these connection configs for testing different database types.

Usage:
    from db_config import DATABASES, get_connection_string
    
    # Get PostgreSQL connection
    conn_str = get_connection_string("postgres")
    
    # Get all available databases
    for db_name, config in DATABASES.items():
        print(f"{db_name}: {config[connection_string]}")
"""

DATABASES = {
    "postgres": {
        "type": "postgresql",
        "host": "localhost",
        "port": 5432,
        "database": "dataviz_test",
        "username": "dataviz",
        "password": "dataviz123",
        "connection_string": "postgresql://dataviz:dataviz123@localhost:5432/dataviz_test",
        "async_connection_string": "postgresql+asyncpg://dataviz:dataviz123@localhost:5432/dataviz_test",
        "container": "dataviz-postgres"
    },
    
    "mysql": {
        "type": "mysql",
        "host": "localhost",
        "port": 3306,
        "database": "dataviz_test",
        "username": "dataviz",
        "password": "dataviz123",
        "connection_string": "mysql://dataviz:dataviz123@localhost:3306/dataviz_test",
        "async_connection_string": "mysql+aiomysql://dataviz:dataviz123@localhost:3306/dataviz_test",
        "container": "dataviz-mysql"
    },
    
    "mongodb": {
        "type": "mongodb",
        "host": "localhost",
        "port": 27017,
        "database": "dataviz_test",
        "username": "dataviz",
        "password": "dataviz123",
        "connection_string": "mongodb://dataviz:dataviz123@localhost:27017/dataviz_test?authSource=admin",
        "container": "dataviz-mongodb"
    },
    
    "mariadb": {
        "type": "mariadb",
        "host": "localhost",
        "port": 3307,
        "database": "dataviz_test",
        "username": "dataviz",
        "password": "dataviz123",
        "connection_string": "mysql://dataviz:dataviz123@localhost:3307/dataviz_test",
        "async_connection_string": "mysql+aiomysql://dataviz:dataviz123@localhost:3307/dataviz_test",
        "container": "dataviz-mariadb"
    },
    
    "redis": {
        "type": "redis",
        "host": "localhost",
        "port": 6380,
        "database": 0,
        "username": None,
        "password": None,
        "connection_string": "redis://localhost:6380/0",
        "container": "dataviz-redis"
    }
}

# Production database (external)
PRODUCTION_DB = {
    "postgres": {
        "type": "postgresql",
        "host": "65.109.167.218",
        "port": 5432,
        "database": "bheem_prod",
        "username": "your_username",
        "password": "your_password",
        "connection_string": "postgresql://user:pass@65.109.167.218:5432/bheem_prod"
    }
}


def get_connection_string(db_name: str, async_mode: bool = False) -> str:
    """Get connection string for a database."""
    if db_name not in DATABASES:
        raise ValueError(f"Unknown database: {db_name}. Available: {list(DATABASES.keys())}")
    
    config = DATABASES[db_name]
    
    if async_mode and "async_connection_string" in config:
        return config["async_connection_string"]
    
    return config["connection_string"]


def get_db_config(db_name: str) -> dict:
    """Get full configuration for a database."""
    if db_name not in DATABASES:
        raise ValueError(f"Unknown database: {db_name}. Available: {list(DATABASES.keys())}")
    
    return DATABASES[db_name]


def list_databases() -> list:
    """List all available test databases."""
    return list(DATABASES.keys())


# Quick test
if __name__ == "__main__":
    print("Available Test Databases:")
    print("=" * 50)
    for name, config in DATABASES.items():
        print(f"\n{name.upper()}:")
        print(f"  Type: {config[type]}")
        print(f"  Host: {config[host]}:{config[port]}")
        print(f"  Database: {config[database]}")
        print(f"  Connection: {config[connection_string]}")
