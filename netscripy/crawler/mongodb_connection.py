from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, PyMongoError

class MongoDBConnection:
    def __init__(self, host='localhost', port=27017, db_name='github_analysis'):
        self.host = host
        self.port = port
        self.db_name = db_name
        self.client = None
        self.db = None

    def connect(self):
        try:
            self.client = MongoClient(f'mongodb://{self.host}:{self.port}/', 
                                    serverSelectionTimeoutMS=5000)
            self.client.admin.command('ping')
            self.db = self.client[self.db_name]
            print(f"成功连接到MongoDB: {self.host}:{self.port}")
            return True
        except ConnectionFailure as e:
            print(f"MongoDB连接失败: {e}")
            return False

    def create_collections(self):
        collections = ['projects', 'owners', 'organizations', 'commits', 'contributors', 'analysis_results', 'search_records']
        for coll in collections:
            if coll not in self.db.list_collection_names():
                self.db.create_collection(coll)
                print(f"创建集合: {coll}")

    def create_indexes(self):
        self.db.projects.create_index([("full_name", 1)], unique=True)
        self.db.projects.create_index([("language", 1)])
        self.db.projects.create_index([("stars_count", -1)])
        self.db.projects.create_index([("updated_at", -1)])
        self.db.projects.create_index([("quality_score", -1)])
        self.db.projects.create_index([("long_term_value", -1)])
        self.db.projects.create_index([("category", 1)])

        self.db.owners.create_index([("login", 1)], unique=True)
        self.db.owners.create_index([("type", 1)])

        self.db.organizations.create_index([("login", 1)], unique=True)
        self.db.organizations.create_index([("activity_score", -1)])
        self.db.organizations.create_index([("tech_depth", -1)])
        self.db.organizations.create_index([("main_tech_stacks", 1)])

        self.db.commits.create_index([("project_id", 1)])
        self.db.commits.create_index([("date", -1)])
        self.db.commits.create_index([("author", 1)])

        self.db.contributors.create_index([("project_id", 1)])
        self.db.contributors.create_index([("contributions", -1)])
        self.db.contributors.create_index([("login", 1)])

        self.db.analysis_results.create_index([("analysis_type", 1)])
        self.db.analysis_results.create_index([("period", 1)])
        self.db.analysis_results.create_index([("created_at", -1)])

        self.db.search_records.create_index([("query", "text")])
        self.db.search_records.create_index([("query_type", 1)])
        self.db.search_records.create_index([("created_at", -1)])
        self.db.search_records.create_index([("validated", 1)])

        print("所有索引创建完成")

    def initialize_database(self):
        if self.connect():
            self.create_collections()
            self.create_indexes()
            return True
        return False

    def close(self):
        if self.client:
            self.client.close()
            print("MongoDB连接已关闭")

    def insert_one(self, collection_name, document):
        try:
            result = self.db[collection_name].insert_one(document)
            return result.inserted_id
        except PyMongoError as e:
            print(f"插入文档失败: {e}")
            return None

    def insert_many(self, collection_name, documents):
        try:
            result = self.db[collection_name].insert_many(documents)
            return result.inserted_ids
        except PyMongoError as e:
            print(f"批量插入文档失败: {e}")
            return None

    def update_one(self, collection_name, filter_query, update_query, upsert=False):
        try:
            result = self.db[collection_name].update_one(filter_query, update_query, upsert=upsert)
            return result
        except PyMongoError as e:
            print(f"更新文档失败: {e}")
            return None

    def find_one(self, collection_name, query):
        try:
            return self.db[collection_name].find_one(query)
        except PyMongoError as e:
            print(f"查询文档失败: {e}")
            return None

    def find(self, collection_name, query=None, projection=None, sort=None, limit=None):
        try:
            cursor = self.db[collection_name].find(query, projection)
            if sort:
                cursor = cursor.sort(sort)
            if limit:
                cursor = cursor.limit(limit)
            return list(cursor)
        except PyMongoError as e:
            print(f"查询文档失败: {e}")
            return None