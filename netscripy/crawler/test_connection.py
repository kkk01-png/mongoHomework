import sys
sys.path.append(sys.path[0])

from mongodb_connection import MongoDBConnection

def test_mongodb_connection():
    print("测试MongoDB连接...")
    
    mongo = MongoDBConnection(host='localhost', port=27017, db_name='github_analysis')
    
    if mongo.connect():
        print("✓ MongoDB连接成功")
        
        print("\n检查数据库集合...")
        collections = mongo.db.list_collection_names()
        print(f"当前集合: {collections}")
        
        print("\n初始化数据库（创建集合和索引）...")
        mongo.create_collections()
        mongo.create_indexes()
        
        collections = mongo.db.list_collection_names()
        print(f"\n初始化后的集合: {collections}")
        
        print("\n✓ 数据库初始化成功")
        
        print("\n测试数据插入...")
        test_project = {
            "name": "test-project",
            "full_name": "test/test-project",
            "description": "Test project for MongoDB connection",
            "language": "Python",
            "stars_count": 100,
            "forks_count": 10,
            "open_issues_count": 1
        }
        inserted_id = mongo.insert_one("projects", test_project)
        print(f"✓ 测试数据插入成功，ID: {inserted_id}")
        
        print("\n测试数据查询...")
        result = mongo.find_one("projects", {"full_name": "test/test-project"})
        if result:
            print(f"✓ 查询成功: {result['name']}")
        
        print("\n删除测试数据...")
        mongo.db.projects.delete_one({"full_name": "test/test-project"})
        print("✓ 测试数据已删除")
        
        mongo.close()
        return True
    else:
        print("✗ MongoDB连接失败")
        return False

if __name__ == "__main__":
    success = test_mongodb_connection()
    sys.exit(0 if success else 1)