from elasticsearch import Elasticsearch

from backend import settings

es_client = Elasticsearch(
    hosts=settings.ELASTICSEARCH['hosts']
)

if not es_client.indices.exists('paragraphs'):
    es_client.indices.create(
        index='paragraphs',
        body={
            'mappings': {
                'properties': {
                    'id': {'type': 'integer'},
                    'articleTitle': {'type': 'text'},
                    'content': {'type': 'text'},
                }
            }
        }
    )
