from opensearchpy import OpenSearch

class OpenSearchConnector:
    def __init__(self, host='localhost', port=9200):
        self.host = host
        self.port = port
        self.client = OpenSearch([{'host': self.host, 'port': self.port}])

    def search(self, index, body):
        return self.client.search(index=index, body=body)

    def index_document(self, index, doc_id, body):
        return self.client.index(index=index, id=doc_id, body=body)

    def get_document(self, index, doc_id):
        return self.client.get(index=index, id=doc_id)

    def delete_document(self, index, doc_id):
        return self.client.delete(index=index, id=doc_id)