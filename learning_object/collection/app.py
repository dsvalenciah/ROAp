
"""
Contains roap app and his db run class.
"""

import os

from config.learning_object import learning_object_populate

import falcon
from falcon_cors import CORS

from pymongo import MongoClient

from resources.learning_object import LearningObject
from resources.learning_object_collection import LearningObjectCollection


class Roap():
    """Main Roap class."""

    def __init__(self, db_host='DB_HOST', db_port=27017, db_name='roap'):
        """Create db and api for Roap."""
        self.client = MongoClient(os.getenv(db_host), db_port)
        self.db = self.client[db_name]

        learning_object_populate(self.db)

        self.api = falcon.API(middleware=[
            CORS(
                allow_all_origins=True,
                allow_all_methods=True,
                allow_all_headers=True
            ).middleware
        ])

        self.api.add_route(
            '/learning-object-collection', LearningObjectCollection(self.db)
        )
        self.api.add_route(
            '/learning-object-collection/{_id}', LearningObject(self.db)
        )

    def get_db(self):
        """Obtain roap db."""
        return self.db

    def get_api(self):
        """Obtain roap api."""
        return self.api


roap = Roap()
api = roap.get_api()
