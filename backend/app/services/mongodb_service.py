"""
MongoDB service for database connections and queries.

Provides async methods for:
- Connection string parsing and building
- Connection testing
- Collection listing
- Schema inference from documents
- Query execution (find, aggregation)
- Document preview
"""

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional
from urllib.parse import quote_plus, urlparse, parse_qs

logger = logging.getLogger(__name__)


class MongoDBService:
    """Service for MongoDB database operations."""

    # Default port for MongoDB
    DEFAULT_PORT = 27017

    @staticmethod
    def parse_connection_string(conn_str: str) -> Dict[str, Any]:
        """
        Parse a MongoDB connection string into components.

        Supports formats:
        - mongodb://host:port/database
        - mongodb://user:password@host:port/database
        - mongodb://user:password@host:port/database?authSource=admin
        - mongodb+srv://user:password@cluster.mongodb.net/database

        NOTE: Special characters in passwords (like @, :, /) must be URL-encoded.
        For example, password "pass@123" should be "pass%40123" in the connection string.

        Returns:
            Dict with host, port, database, username, password, auth_source, extra
        """
        result = {
            "host": "localhost",
            "port": MongoDBService.DEFAULT_PORT,
            "database": "",
            "username": None,
            "password": None,
            "auth_source": None,
            "replica_set": None,
            "is_srv": False,
            "extra": {},
        }

        if not conn_str:
            return result

        try:
            # Check for SRV format
            is_srv = conn_str.startswith("mongodb+srv://")
            if is_srv:
                result["is_srv"] = True
                conn_str = conn_str.replace("mongodb+srv://", "mongodb://")
                result["port"] = None  # SRV doesn't use explicit port

            parsed = urlparse(conn_str)

            # Extract host and port
            if parsed.hostname:
                result["host"] = parsed.hostname
            if parsed.port:
                result["port"] = parsed.port

            # Extract credentials
            if parsed.username:
                result["username"] = parsed.username
            if parsed.password:
                result["password"] = parsed.password

            # Validate: if we have username but hostname looks wrong, password might have unencoded @
            if parsed.username and parsed.hostname:
                # Count @ in the original URL part before query
                url_part = conn_str.split('?')[0] if '?' in conn_str else conn_str
                at_count = url_part.count('@')
                if at_count > 1:
                    logger.warning(
                        f"Connection string has {at_count} '@' characters. "
                        "If your password contains '@', it must be URL-encoded as '%40'"
                    )

            # Extract database from path
            if parsed.path and parsed.path != "/":
                result["database"] = parsed.path.lstrip("/")

            # Parse query parameters
            if parsed.query:
                params = parse_qs(parsed.query)
                if "authSource" in params:
                    result["auth_source"] = params["authSource"][0]
                if "replicaSet" in params:
                    result["replica_set"] = params["replicaSet"][0]
                # Store other params
                for key, values in params.items():
                    if key not in ("authSource", "replicaSet"):
                        result["extra"][key] = values[0] if len(values) == 1 else values

        except Exception as e:
            logger.warning(f"Failed to parse MongoDB connection string: {e}")

        return result

    @staticmethod
    def build_connection_string(
        host: str = "localhost",
        port: int = 27017,
        database: str = "",
        username: Optional[str] = None,
        password: Optional[str] = None,
        auth_source: Optional[str] = None,
        replica_set: Optional[str] = None,
        is_srv: bool = False,
        **extra
    ) -> str:
        """
        Build a MongoDB connection string from components.

        Args:
            host: MongoDB host or cluster address
            port: MongoDB port (ignored for SRV)
            database: Database name
            username: Optional username
            password: Optional password
            auth_source: Optional authentication database
            replica_set: Optional replica set name
            is_srv: Whether to use mongodb+srv:// protocol
            **extra: Additional connection parameters

        Returns:
            MongoDB connection string
        """
        protocol = "mongodb+srv" if is_srv else "mongodb"

        # Build auth part
        auth = ""
        if username:
            if password:
                auth = f"{quote_plus(username)}:{quote_plus(password)}@"
            else:
                auth = f"{quote_plus(username)}@"

        # Build host part
        if is_srv:
            host_part = host
        else:
            host_part = f"{host}:{port}" if port else host

        # Build database part
        db_part = f"/{database}" if database else ""

        # Build query parameters
        params = []
        if auth_source:
            params.append(f"authSource={auth_source}")
        if replica_set:
            params.append(f"replicaSet={replica_set}")
        for key, value in extra.items():
            if value is not None:
                params.append(f"{key}={value}")

        query = f"?{'&'.join(params)}" if params else ""

        return f"{protocol}://{auth}{host_part}{db_part}{query}"

    @staticmethod
    async def test_connection(
        host: str = "localhost",
        port: int = 27017,
        database: str = "",
        username: Optional[str] = None,
        password: Optional[str] = None,
        auth_source: Optional[str] = None,
        is_srv: bool = False,
        ssl: bool = False,
        **extra
    ) -> Dict[str, Any]:
        """
        Test a MongoDB connection.

        Returns:
            Dict with success, message, collections_count, version
        """
        try:
            from motor.motor_asyncio import AsyncIOMotorClient
        except ImportError:
            return {
                "success": False,
                "message": "MongoDB driver (motor) not installed. Run: pip install motor",
                "tables_count": 0,
                "version": None,
            }

        conn_str = MongoDBService.build_connection_string(
            host=host,
            port=port,
            database=database,
            username=username,
            password=password,
            auth_source=auth_source,
            is_srv=is_srv,
            **extra
        )

        client = None
        try:
            # Create client with timeout
            # For SRV connections (Atlas), TLS is required
            use_tls = ssl or is_srv
            client = AsyncIOMotorClient(
                conn_str,
                serverSelectionTimeoutMS=10000,
                connectTimeoutMS=10000,
                tls=use_tls,
            )

            # Test connection by getting server info
            server_info = await client.server_info()
            version = server_info.get("version", "unknown")

            # Get database and count collections
            db = client[database] if database else client.get_default_database()
            if db is None:
                # If no database specified, use 'test' or list databases
                db = client["test"]

            collections = await db.list_collection_names()
            collections_count = len(collections)

            return {
                "success": True,
                "message": f"Connected to MongoDB {version}",
                "tables_count": collections_count,
                "version": version,
            }

        except Exception as e:
            error_msg = str(e)
            if "Authentication failed" in error_msg:
                return {
                    "success": False,
                    "message": "Authentication failed. Check username and password. If using connection string, ensure special characters (like @) are URL-encoded.",
                    "tables_count": 0,
                    "version": None,
                }
            elif "ServerSelectionTimeoutError" in error_msg or "timeout" in error_msg.lower():
                # Check if this might be a connection string parsing issue
                hint = ""
                if is_srv:
                    hint = " For Atlas, ensure your IP is whitelisted."
                return {
                    "success": False,
                    "message": f"Connection timeout. Check host: {host}.{hint}",
                    "tables_count": 0,
                    "version": None,
                }
            elif "Invalid URI" in error_msg or "InvalidURI" in error_msg:
                return {
                    "success": False,
                    "message": "Invalid connection string format. If password contains special characters (@, :, /), they must be URL-encoded (@ = %40).",
                    "tables_count": 0,
                    "version": None,
                }
            else:
                logger.error(f"MongoDB connection error: {e}")
                return {
                    "success": False,
                    "message": f"Connection failed: {error_msg}",
                    "tables_count": 0,
                    "version": None,
                }
        finally:
            if client:
                client.close()

    @staticmethod
    async def get_tables(
        host: str = "localhost",
        port: int = 27017,
        database: str = "",
        username: Optional[str] = None,
        password: Optional[str] = None,
        auth_source: Optional[str] = None,
        is_srv: bool = False,
        ssl: bool = False,
        **extra
    ) -> List[Dict[str, str]]:
        """
        Get list of collections in the database.

        Returns:
            List of dicts with schema, name, type
        """
        try:
            from motor.motor_asyncio import AsyncIOMotorClient
        except ImportError:
            logger.error("motor not installed")
            return []

        conn_str = MongoDBService.build_connection_string(
            host=host,
            port=port,
            database=database,
            username=username,
            password=password,
            auth_source=auth_source,
            is_srv=is_srv,
            **extra
        )

        client = None
        try:
            # For SRV connections (Atlas), TLS is required
            use_tls = ssl or is_srv
            client = AsyncIOMotorClient(
                conn_str,
                serverSelectionTimeoutMS=10000,
                tls=use_tls,
            )

            db = client[database] if database else client.get_default_database()
            if db is None:
                db = client["test"]

            collections = await db.list_collection_names()

            # Return in format compatible with existing code
            return [
                {
                    "schema": database or "default",
                    "name": collection,
                    "type": "COLLECTION",
                }
                for collection in sorted(collections)
                if not collection.startswith("system.")
            ]

        except Exception as e:
            logger.error(f"Failed to get MongoDB collections: {e}")
            return []
        finally:
            if client:
                client.close()

    @staticmethod
    async def get_table_relationships(
        host: str = "localhost",
        port: int = 27017,
        database: str = "",
        username: Optional[str] = None,
        password: Optional[str] = None,
        **extra
    ) -> Dict[str, int]:
        """
        Get table relationships (foreign key references).

        MongoDB doesn't have native FK relationships, so return empty dict.
        Could be extended to analyze $lookup patterns or DBRef fields.

        Returns:
            Empty dict (MongoDB has no FK constraints)
        """
        # MongoDB doesn't enforce foreign key relationships
        # Return empty dict for compatibility
        return {}

    @staticmethod
    async def get_table_columns(
        host: str = "localhost",
        port: int = 27017,
        database: str = "",
        collection: str = "",
        username: Optional[str] = None,
        password: Optional[str] = None,
        auth_source: Optional[str] = None,
        is_srv: bool = False,
        ssl: bool = False,
        sample_size: int = 100,
        **extra
    ) -> List[Dict[str, Any]]:
        """
        Infer schema from collection by sampling documents.

        Args:
            collection: Collection name
            sample_size: Number of documents to sample for schema inference

        Returns:
            List of dicts with name, type, nullable
        """
        try:
            from motor.motor_asyncio import AsyncIOMotorClient
        except ImportError:
            logger.error("motor not installed")
            return []

        conn_str = MongoDBService.build_connection_string(
            host=host,
            port=port,
            database=database,
            username=username,
            password=password,
            auth_source=auth_source,
            is_srv=is_srv,
            **extra
        )

        client = None
        try:
            # For SRV connections (Atlas), TLS is required
            use_tls = ssl or is_srv
            client = AsyncIOMotorClient(
                conn_str,
                serverSelectionTimeoutMS=10000,
                tls=use_tls,
            )

            db = client[database] if database else client.get_default_database()
            coll = db[collection]

            # Sample documents to infer schema
            cursor = coll.find().limit(sample_size)
            documents = await cursor.to_list(length=sample_size)

            if not documents:
                return []

            # Analyze field types across all sampled documents
            field_types: Dict[str, set] = {}
            field_nullable: Dict[str, bool] = {}

            for doc in documents:
                seen_fields = set()
                for key, value in doc.items():
                    seen_fields.add(key)
                    if key not in field_types:
                        field_types[key] = set()
                        field_nullable[key] = False

                    field_types[key].add(MongoDBService._get_bson_type(value))

                    if value is None:
                        field_nullable[key] = True

                # Mark fields not present in this document as nullable
                for field in field_types:
                    if field not in seen_fields:
                        field_nullable[field] = True

            # Convert to column info format
            columns = []
            for field, types in field_types.items():
                # Determine primary type (most common or most specific)
                primary_type = MongoDBService._get_primary_type(types)
                columns.append({
                    "name": field,
                    "type": primary_type,
                    "nullable": field_nullable.get(field, True),
                    "default": None,
                })

            # Sort: _id first, then alphabetically
            columns.sort(key=lambda x: (x["name"] != "_id", x["name"]))

            return columns

        except Exception as e:
            logger.error(f"Failed to get MongoDB collection schema: {e}")
            return []
        finally:
            if client:
                client.close()

    @staticmethod
    def _get_bson_type(value: Any) -> str:
        """Convert Python/BSON type to a type string."""
        if value is None:
            return "null"
        elif isinstance(value, bool):
            return "boolean"
        elif isinstance(value, int):
            return "integer"
        elif isinstance(value, float):
            return "double"
        elif isinstance(value, str):
            return "string"
        elif isinstance(value, list):
            return "array"
        elif isinstance(value, dict):
            return "object"
        elif hasattr(value, "__class__"):
            class_name = value.__class__.__name__
            if class_name == "ObjectId":
                return "objectId"
            elif class_name == "datetime":
                return "date"
            elif class_name == "Decimal128":
                return "decimal"
            elif class_name == "Binary":
                return "binary"
        return "unknown"

    @staticmethod
    def _get_primary_type(types: set) -> str:
        """Determine the primary type from a set of observed types."""
        # Remove null from consideration
        types = types - {"null"}

        if not types:
            return "null"
        if len(types) == 1:
            return types.pop()

        # Type priority for mixed types
        priority = ["objectId", "date", "decimal", "double", "integer", "string", "boolean", "array", "object"]
        for t in priority:
            if t in types:
                return t

        return "mixed"

    @staticmethod
    async def execute_query(
        host: str = "localhost",
        port: int = 27017,
        database: str = "",
        collection: str = "",
        query: Optional[Dict] = None,
        projection: Optional[Dict] = None,
        sort: Optional[List] = None,
        limit: int = 100,
        skip: int = 0,
        username: Optional[str] = None,
        password: Optional[str] = None,
        auth_source: Optional[str] = None,
        is_srv: bool = False,
        ssl: bool = False,
        **extra
    ) -> Dict[str, Any]:
        """
        Execute a MongoDB find query.

        Args:
            collection: Collection name
            query: MongoDB query filter (default: {})
            projection: Fields to include/exclude
            sort: Sort specification [(field, direction), ...]
            limit: Maximum documents to return
            skip: Number of documents to skip

        Returns:
            Dict with columns, rows, total, execution_time
        """
        try:
            from motor.motor_asyncio import AsyncIOMotorClient
        except ImportError:
            return {
                "columns": [],
                "rows": [],
                "total": 0,
                "error": "motor not installed",
            }

        conn_str = MongoDBService.build_connection_string(
            host=host,
            port=port,
            database=database,
            username=username,
            password=password,
            auth_source=auth_source,
            is_srv=is_srv,
            **extra
        )

        client = None
        start_time = time.time()

        try:
            # For SRV connections (Atlas), TLS is required
            use_tls = ssl or is_srv
            client = AsyncIOMotorClient(
                conn_str,
                serverSelectionTimeoutMS=10000,
                tls=use_tls,
            )

            db = client[database] if database else client.get_default_database()
            coll = db[collection]

            # Build query
            query = query or {}
            cursor = coll.find(query, projection)

            if sort:
                cursor = cursor.sort(sort)

            cursor = cursor.skip(skip).limit(limit)

            # Execute query
            documents = await cursor.to_list(length=limit)

            # Get total count
            total = await coll.count_documents(query)

            execution_time = int((time.time() - start_time) * 1000)

            # Convert documents to rows format
            rows = []
            all_columns = set()

            for doc in documents:
                row = MongoDBService._flatten_document(doc)
                rows.append(row)
                all_columns.update(row.keys())

            # Sort columns: _id first, then alphabetically
            columns = sorted(all_columns, key=lambda x: (x != "_id", x))

            return {
                "columns": columns,
                "rows": rows,
                "total": total,
                "execution_time_ms": execution_time,
            }

        except Exception as e:
            logger.error(f"MongoDB query failed: {e}")
            return {
                "columns": [],
                "rows": [],
                "total": 0,
                "error": str(e),
            }
        finally:
            if client:
                client.close()

    @staticmethod
    async def execute_aggregation(
        host: str = "localhost",
        port: int = 27017,
        database: str = "",
        collection: str = "",
        pipeline: List[Dict] = None,
        limit: int = 100,
        username: Optional[str] = None,
        password: Optional[str] = None,
        auth_source: Optional[str] = None,
        is_srv: bool = False,
        ssl: bool = False,
        **extra
    ) -> Dict[str, Any]:
        """
        Execute a MongoDB aggregation pipeline.

        Args:
            collection: Collection name
            pipeline: MongoDB aggregation pipeline stages
            limit: Maximum documents to return

        Returns:
            Dict with columns, rows, total, execution_time
        """
        try:
            from motor.motor_asyncio import AsyncIOMotorClient
        except ImportError:
            return {
                "columns": [],
                "rows": [],
                "total": 0,
                "error": "motor not installed",
            }

        conn_str = MongoDBService.build_connection_string(
            host=host,
            port=port,
            database=database,
            username=username,
            password=password,
            auth_source=auth_source,
            is_srv=is_srv,
            **extra
        )

        client = None
        start_time = time.time()

        try:
            # For SRV connections (Atlas), TLS is required
            use_tls = ssl or is_srv
            client = AsyncIOMotorClient(
                conn_str,
                serverSelectionTimeoutMS=10000,
                tls=use_tls,
            )

            db = client[database] if database else client.get_default_database()
            coll = db[collection]

            # Add limit to pipeline if not present
            pipeline = pipeline or []
            if not any("$limit" in stage for stage in pipeline):
                pipeline.append({"$limit": limit})

            # Execute aggregation
            cursor = coll.aggregate(pipeline)
            documents = await cursor.to_list(length=limit)

            execution_time = int((time.time() - start_time) * 1000)

            # Convert documents to rows format
            rows = []
            all_columns = set()

            for doc in documents:
                row = MongoDBService._flatten_document(doc)
                rows.append(row)
                all_columns.update(row.keys())

            columns = sorted(all_columns, key=lambda x: (x != "_id", x))

            return {
                "columns": columns,
                "rows": rows,
                "total": len(rows),
                "execution_time_ms": execution_time,
            }

        except Exception as e:
            logger.error(f"MongoDB aggregation failed: {e}")
            return {
                "columns": [],
                "rows": [],
                "total": 0,
                "error": str(e),
            }
        finally:
            if client:
                client.close()

    @staticmethod
    def _flatten_document(doc: Dict, prefix: str = "") -> Dict[str, Any]:
        """
        Flatten a nested MongoDB document for tabular display.

        Converts ObjectId to string, handles nested objects.
        """
        result = {}

        for key, value in doc.items():
            full_key = f"{prefix}.{key}" if prefix else key

            # Convert ObjectId to string
            if hasattr(value, "__class__") and value.__class__.__name__ == "ObjectId":
                result[full_key] = str(value)
            # Convert datetime to ISO string
            elif hasattr(value, "isoformat"):
                result[full_key] = value.isoformat()
            # Flatten nested dicts (one level only to avoid too many columns)
            elif isinstance(value, dict) and not prefix:
                nested = MongoDBService._flatten_document(value, full_key)
                result.update(nested)
            # Convert lists to JSON string for display
            elif isinstance(value, list):
                if len(value) <= 3:
                    result[full_key] = value
                else:
                    result[full_key] = f"[{len(value)} items]"
            else:
                result[full_key] = value

        return result

    @staticmethod
    async def get_table_preview(
        host: str = "localhost",
        port: int = 27017,
        database: str = "",
        collection: str = "",
        limit: int = 100,
        offset: int = 0,
        username: Optional[str] = None,
        password: Optional[str] = None,
        auth_source: Optional[str] = None,
        is_srv: bool = False,
        ssl: bool = False,
        **extra
    ) -> Dict[str, Any]:
        """
        Get a preview of documents from a collection with pagination.

        Returns:
            Dict with columns, rows, total, preview_count, execution_time
        """
        try:
            from motor.motor_asyncio import AsyncIOMotorClient
        except ImportError:
            return {
                "columns": [],
                "rows": [],
                "total": 0,
                "preview_count": 0,
                "error": "motor not installed",
            }

        conn_str = MongoDBService.build_connection_string(
            host=host,
            port=port,
            database=database,
            username=username,
            password=password,
            auth_source=auth_source,
            is_srv=is_srv,
            **extra
        )

        client = None
        start_time = time.time()

        try:
            # For SRV connections (Atlas), TLS is required
            use_tls = ssl or is_srv
            client = AsyncIOMotorClient(
                conn_str,
                serverSelectionTimeoutMS=10000,
                tls=use_tls,
            )

            db = client[database] if database else client.get_default_database()
            coll = db[collection]

            # Get documents with pagination
            cursor = coll.find().skip(offset).limit(limit)
            documents = await cursor.to_list(length=limit)

            # Get total count
            total = await coll.estimated_document_count()

            execution_time = int((time.time() - start_time) * 1000)

            # Convert documents to rows format
            rows = []
            all_columns = set()

            for doc in documents:
                row = MongoDBService._flatten_document(doc)
                rows.append(row)
                all_columns.update(row.keys())

            columns = sorted(all_columns, key=lambda x: (x != "_id", x))

            return {
                "columns": columns,
                "rows": rows,
                "total": total,
                "preview_count": len(rows),
                "execution_time": execution_time,
            }

        except Exception as e:
            logger.error(f"MongoDB preview failed: {e}")
            return {
                "columns": [],
                "rows": [],
                "total": 0,
                "preview_count": 0,
                "error": str(e),
            }
        finally:
            if client:
                client.close()


# Singleton instance
mongodb_service = MongoDBService()
