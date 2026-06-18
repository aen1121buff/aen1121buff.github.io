"""
AnimalShelter CRUD module for the CS 340 Grazioso Salvare dashboard.
Enhanced for CS 499 Milestone Three.

This version keeps the original MongoDB CRUD purpose while adding safer validation,
controlled projections, and helper methods that support ranked rescue candidates.
"""

import os
from typing import Any, Dict, List, Optional
from pymongo import MongoClient, ASCENDING
from pymongo.collection import Collection
from pymongo.errors import PyMongoError


class AnimalShelter:
    """Reusable MongoDB access layer for the Austin Animal Center animals collection."""

    def __init__(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        host: str = "localhost",
        port: int = 27017,
        database: str = "aac",
        collection: str = "animals",
        auth_source: str = "admin",
    ) -> None:
        self.username = username or os.getenv("AAC_USERNAME", "aacuser")
        self.password = password or os.getenv("AAC_PASSWORD", "SNHU1234")
        self.host = host
        self.port = port
        self.database_name = database
        self.collection_name = collection
        self.auth_source = auth_source
        self.client = self._connect()
        self.database = self.client[self.database_name]
        self.collection: Collection = self.database[self.collection_name]

    def _connect(self) -> MongoClient:
        """Create a MongoDB client using supplied or environment based credentials."""
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
            return MongoClient(host=self.host, port=self.port, serverSelectionTimeoutMS=5000)
        except PyMongoError as error:
            raise ConnectionError(f"Unable to connect to MongoDB: {error}") from error

    @staticmethod
    def _validate_document(document: Dict[str, Any]) -> None:
        if not isinstance(document, dict) or not document:
            raise ValueError("A non empty dictionary is required.")

    def create(self, data: Dict[str, Any]) -> bool:
        """Insert one animal record into the collection."""
        self._validate_document(data)
        try:
            result = self.collection.insert_one(data)
            return result.acknowledged
        except PyMongoError as error:
            raise RuntimeError(f"Create operation failed: {error}") from error

    def read(self, query: Optional[Dict[str, Any]] = None, projection: Optional[Dict[str, int]] = None) -> List[Dict[str, Any]]:
        """Return a list of documents that match the supplied MongoDB query."""
        query = query or {}
        if not isinstance(query, dict):
            raise ValueError("Query must be a dictionary.")
        try:
            return list(self.collection.find(query, projection))
        except PyMongoError as error:
            raise RuntimeError(f"Read operation failed: {error}") from error

    def update(self, query: Dict[str, Any], update_values: Dict[str, Any]) -> int:
        """Update records matching the query and return the modified count."""
        self._validate_document(query)
        self._validate_document(update_values)
        try:
            result = self.collection.update_many(query, {"$set": update_values})
            return result.modified_count
        except PyMongoError as error:
            raise RuntimeError(f"Update operation failed: {error}") from error

    def delete(self, query: Dict[str, Any]) -> int:
        """Delete records matching the query and return the deleted count."""
        self._validate_document(query)
        try:
            result = self.collection.delete_many(query)
            return result.deleted_count
        except PyMongoError as error:
            raise RuntimeError(f"Delete operation failed: {error}") from error

    def count(self, query: Optional[Dict[str, Any]] = None) -> int:
        """Count documents matching a query."""
        query = query or {}
        if not isinstance(query, dict):
            raise ValueError("Query must be a dictionary.")
        try:
            return self.collection.count_documents(query)
        except PyMongoError as error:
            raise RuntimeError(f"Count operation failed: {error}") from error

    def create_filter_indexes(self) -> None:
        """Create useful indexes for fields used by the dashboard filters and scoring logic."""
        try:
            self.collection.create_index([("animal_type", ASCENDING)])
            self.collection.create_index([("breed", ASCENDING)])
            self.collection.create_index([("sex_upon_outcome", ASCENDING)])
            self.collection.create_index([("age_upon_outcome_in_weeks", ASCENDING)])
            self.collection.create_index([("outcome_type", ASCENDING)])
        except PyMongoError as error:
            raise RuntimeError(f"Index creation failed: {error}") from error
