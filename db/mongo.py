import pymongo

class MongoDB:
    def __init__(self, database: str):
        self.client = pymongo.MongoClient("mongodb://localhost:27017/")
        self.db = self.client[database]
