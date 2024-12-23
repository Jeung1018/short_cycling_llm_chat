from typing import Dict, List
from pymongo import MongoClient
from config import MONGODB_URI, DB_NAME, COLLECTION_NAME

def get_mongodb_collection():
    """MongoDB 컬렉션을 가져오는 함수"""
    try:
        client = MongoClient(MONGODB_URI)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        return collection
    except Exception as e:
        print(f"MongoDB connection error: {str(e)}")
        raise e

def fetch_data_from_mongodb(query: Dict, projection: Dict = None) -> List[Dict]:
    """MongoDB에서 데이터를 가져오는 함수"""
    try:
        collection = get_mongodb_collection()
        if projection:
            cursor = collection.find(query, projection)
        else:
            cursor = collection.find(query)
        return list(cursor)
    except Exception as e:
        print(f"MongoDB fetch error: {str(e)}")
        return []

def fetch_single_document(query: Dict, projection: Dict = None) -> Dict:
    """MongoDB에서 단일 문서를 가져오는 함수"""
    try:
        collection = get_mongodb_collection()
        if projection:
            doc = collection.find_one(query, projection)
        else:
            doc = collection.find_one(query)
        return doc if doc else {}
    except Exception as e:
        print(f"MongoDB fetch error: {str(e)}")
        return {} 