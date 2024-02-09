import json
from app.api.v1.dependencies.opensearch import OpenSearchConnector

def index_documents_from_json(json_file, index_name):
    connector = OpenSearchConnector(host='localhost', port=9200)
    with open(json_file, 'r') as file:
        documents = json.load(file)
        for doc_id, doc_body in documents.items():
            response = connector.index_document(index=index_name, doc_id=doc_id, body=doc_body)
            print(f"Indexed document {doc_id}. Response: {response}")