import os

if __name__ == "__main__":
    milvus_uri = os.getenv("MILVUS_URI")
    print(f"MILVUS_URI from os.getenv: {milvus_uri}")
    print(f"Type of MILVUS_URI: {type(milvus_uri)}")
