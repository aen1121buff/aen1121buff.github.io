"""
AnimalShelter CRUD module for the CS 340 Grazioso Salvare dashboard.
Enhanced for CS 499 Milestone Four: Databases.

This version builds on the Milestone Three artifact and focuses on the database
category. It improves MongoDB connection handling, validation, indexed lookup
support, controlled projections, safer update and delete behavior, and reusable
methods that support dashboard filtering and reporting.
"""

import os
from typing import Any, Dict, Iterable, List, Optional, Tuple

from pymongo import ASCENDING, MongoClient
from pymongo.collection import Collection
from pymongo.errors import PyMongoError, ServerSelectionTimeoutError


DEFAULT_PROJECTION: Dict[str, int] = {
    "animal_id": 1,
    "animal_type": 1,
    "breed": 1,
    "name": 1,
    "sex_upon_outcome": 1,
    "age_upon_outcome_in_weeks": 1,
    "outcome_type": 1,
    "location_lat": 1,
    "location_long": 1,
}

INDEX_FIELDS: Tuple[str, ...] = (
    "animal_type",
    "breed",
    "sex_upon_outcome",
    "age_upon_outcome_in_weeks",
    "outcome_type",
)


class AnimalShelter:
    """Reusable MongoDB access layer for the Austin Animal Center animals collection."""

    def __init__(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
        database: Optional[str] = None,
        collection: Optional[str] = None,
        auth_source: Optional[str] = None,
        validate_connection: bool = True,
    ) -> None:
        self.username = username or os.getenv("AAC_USERNAME", "aacuser")
        self.password = password or os.getenv("AAC_PASSWORD", "SNHU1234")
        self.host = host or os.getenv("AAC_HOST", "localhost")
        self.port = int(port or os.getenv("AAC_PORT", "27017"))
        self.database_name = database or os.getenv("AAC_DATABASE", "aac")
        self.collection_name = collection or os.getenv("AAC_COLLECTION", "animals")
        self.auth_source = auth_source or os.getenv("AAC_AUTH_SOURCE", "admin")

        self.client = self._connect()
        self.database = self.client[self.database_name]
        self.collection: Collection = self.database[self.collection_name]

        if validate_connection:
            self.ping()

    def _connect(self) -> MongoClient:
        """Create a MongoDB client using environment based or supplied credentials."""
        try:
            if self.username and self.password:
                return MongoClient(
                    host=self.host,
                    port=self.port,
                    username=self.username,
                    password=self.password,
                    authSource=self.auth_source,
                    serverSelectionTimeoutMS=5000,
                )
            return MongoClient(
                host=self.host,
                port=self.port,
                serverSelectionTimeoutMS=5000,
            )
        except PyMongoError as error:
            raise ConnectionError(f"Unable to create MongoDB client: {error}") from error

    def ping(self) -> bool:
        """Validate that the MongoDB server can be reached before dashboard queries run."""
        try:
            self.client.admin.command("ping")
            return True
        except ServerSelectionTimeoutError as error:
            raise ConnectionError(f"MongoDB server is not reachable: {error}") from error
        except PyMongoError as error:
            raise ConnectionError(f"MongoDB connection check failed: {error}") from error

    @staticmethod
    def _validate_document(document: Dict[str, Any], name: str = "Document") -> None:
        if not isinstance(document, dict) or not document:
            raise ValueError(f"{name} must be a non empty dictionary.")

    @staticmethod
    def _validate_query(query: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        if query is None:
            return {}
        if not isinstance(query, dict):
            raise ValueError("Query must be a dictionary.")
        return query

    @staticmethod
    def _validate_projection(projection: Optional[Dict[str, int]]) -> Optional[Dict[str, int]]:
        if projection is None:
            return None
        if not isinstance(projection, dict):
            raise ValueError("Projection must be a dictionary.")
        for field_name, include_value in projection.items():
            if not isinstance(field_name, str) or include_value not in (0, 1):
                raise ValueError("Projection fields must map string field names to 0 or 1.")
        return projection

    @staticmethod
    def _validate_sort(sort_fields: Optional[Iterable[Tuple[str, int]]]) -> Optional[List[Tuple[str, int]]]:
        if sort_fields is None:
            return None
        normalized_sort = list(sort_fields)
        for field_name, direction in normalized_sort:
            if not isinstance(field_name, str) or direction not in (1, -1, ASCENDING):
                raise ValueError("Sort fields must contain a field name and a valid direction.")
        return normalized_sort

    def create(self, data: Dict[str, Any]) -> str:
        """Insert one animal record and return the inserted document id."""
        self._validate_document(data, "Create data")
        try:
            result = self.collection.insert_one(data)
            return str(result.inserted_id)
        except PyMongoError as error:
            raise RuntimeError(f"Create operation failed: {error}") from error

    def read(
        self,
        query: Optional[Dict[str, Any]] = None,
        projection: Optional[Dict[str, int]] = None,
        limit: int = 0,
        sort_fields: Optional[Iterable[Tuple[str, int]]] = None,
    ) -> List[Dict[str, Any]]:
        """Return documents that match the supplied MongoDB query."""
        safe_query = self._validate_query(query)
        safe_projection = self._validate_projection(projection)
        safe_sort = self._validate_sort(sort_fields)

        if limit < 0:
            raise ValueError("Limit cannot be negative.")

        try:
            cursor = self.collection.find(safe_query, safe_projection)
            if safe_sort:
                cursor = cursor.sort(safe_sort)
            if limit:
                cursor = cursor.limit(limit)
            return list(cursor)
        except PyMongoError as error:
            raise RuntimeError(f"Read operation failed: {error}") from error

    def update(self, query: Dict[str, Any], update_values: Dict[str, Any], allow_many: bool = True) -> int:
        """Update matching records and return the modified count."""
        self._validate_document(query, "Update query")
        self._validate_document(update_values, "Update values")
        try:
            if allow_many:
                result = self.collection.update_many(query, {"$set": update_values})
            else:
                result = self.collection.update_one(query, {"$set": update_values})
            return result.modified_count
        except PyMongoError as error:
            raise RuntimeError(f"Update operation failed: {error}") from error

    def delete(self, query: Dict[str, Any], allow_many: bool = False) -> int:
        """Delete matching records and return the deleted count.

        Delete defaults to one record only. This prevents accidental bulk deletion
        when the dashboard or a future admin tool passes an overly broad query.
        """
        self._validate_document(query, "Delete query")
        try:
            if allow_many:
                result = self.collection.delete_many(query)
            else:
                result = self.collection.delete_one(query)
            return result.deleted_count
        except PyMongoError as error:
            raise RuntimeError(f"Delete operation failed: {error}") from error

    def count(self, query: Optional[Dict[str, Any]] = None) -> int:
        """Count documents matching a query."""
        safe_query = self._validate_query(query)
        try:
            return self.collection.count_documents(safe_query)
        except PyMongoError as error:
            raise RuntimeError(f"Count operation failed: {error}") from error

    def distinct_values(self, field_name: str, query: Optional[Dict[str, Any]] = None) -> List[Any]:
        """Return unique database values for a field used in dashboard reporting."""
        if not isinstance(field_name, str) or not field_name:
            raise ValueError("Field name must be a non empty string.")
        safe_query = self._validate_query(query)
        try:
            return sorted(self.collection.distinct(field_name, safe_query))
        except PyMongoError as error:
            raise RuntimeError(f"Distinct value lookup failed: {error}") from error

    def aggregate(self, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Run a safe aggregation pipeline for reporting views."""
        if not isinstance(pipeline, list) or not pipeline:
            raise ValueError("Aggregation pipeline must be a non empty list.")
        if not all(isinstance(stage, dict) for stage in pipeline):
            raise ValueError("Each aggregation stage must be a dictionary.")
        try:
            return list(self.collection.aggregate(pipeline))
        except PyMongoError as error:
            raise RuntimeError(f"Aggregation failed: {error}") from error

    def create_filter_indexes(self) -> List[str]:
        """Create indexes for fields used by dashboard filters and rescue scoring."""
        created_indexes: List[str] = []
        try:
            for field_name in INDEX_FIELDS:
                index_name = self.collection.create_index([(field_name, ASCENDING)])
                created_indexes.append(index_name)
            compound_name = self.collection.create_index(
                [
                    ("animal_type", ASCENDING),
                    ("breed", ASCENDING),
                    ("sex_upon_outcome", ASCENDING),
                    ("age_upon_outcome_in_weeks", ASCENDING),
                ]
            )
            created_indexes.append(compound_name)
            return created_indexes
        except PyMongoError as error:
            raise RuntimeError(f"Index creation failed: {error}") from error

    def get_dashboard_records(
        self,
        query: Optional[Dict[str, Any]] = None,
        limit: int = 500,
    ) -> List[Dict[str, Any]]:
        """Read records for the dashboard with only fields needed by table, chart, and map."""
        return self.read(
            query=query,
            projection=DEFAULT_PROJECTION,
            limit=limit,
            sort_fields=[("breed", ASCENDING), ("name", ASCENDING)],
        )

    def close(self) -> None:
        """Close the MongoDB client connection."""
        self.client.close()

    def __enter__(self) -> "AnimalShelter":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()
