from neo4j import GraphDatabase
import json

class Neo4jImporter:
    def __init__(self, uri="bolt://localhost:7687", user="neo4j", password="your_password"):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def clear_database(self):
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")

    def import_entities(self, entity_file):
        with open(entity_file, 'r', encoding='utf-8') as f:
            entity_data = json.load(f)
        
        with self.driver.session() as session:
            # make index for entity id
            session.run("CREATE INDEX IF NOT EXISTS FOR (n:Entity) ON (n.id)")
            for source in ['arxiv', 'hackernews']:
                for entity_type in ['PERSON', 'ORG', 'GPE', 'PRODUCT', 'WORK_OF_ART']:
                    for entity in entity_data['detailed_entities'][source][entity_type]:
                        session.run("""
                            MERGE (e:Entity {id: $id})
                            SET e.text = $text,
                                e.type = $entity_type,
                                e.source = $source,
                                e.source_id = $source_id,
                                e.source_title = $source_title
                        """, {
                            'id': f"{entity['text']}_{entity_type}",
                            'text': entity['text'],
                            'entity_type': entity_type,
                            'source': source,
                            'source_id': entity['paper_id'],
                            'source_title': entity['paper_title']
                        })

    def import_relations(self, relation_file):
        with open(relation_file, 'r', encoding='utf-8') as f:
            relation_data = json.load(f)
        
        with self.driver.session() as session:
            for source in ['arxiv', 'hackernews']:
                # import entity_entity relations
                for relation in relation_data['detailed_relations'][source]['entity_entity']:
                    session.run("""
                        MATCH (e1:Entity {text: $entity1_text})
                        MATCH (e2:Entity {text: $entity2_text})
                        MERGE (e1)-[r:RELATED_TO]->(e2)
                        SET r.source = $source,
                            r.source_id = $source_id,
                            r.source_title = $source_title
                    """, {
                        'entity1_text': relation['entity1']['text'],
                        'entity2_text': relation['entity2']['text'],
                        'source': source,
                        'source_id': relation['paper_id' if source == 'arxiv' else 'article_id'],
                        'source_title': relation['paper_title' if source == 'arxiv' else 'article_title']
                    })
                # import subject_verb_object relations
                for relation in relation_data['detailed_relations'][source]['subject_verb_object']:
                    session.run("""
                        MERGE (s:Entity {text: $subject})
                        MERGE (o:Entity {text: $object})
                        MERGE (s)-[r:ACTION {verb: $verb}]->(o)
                        SET r.source = $source,
                            r.source_id = $source_id,
                            r.sentence = $sentence
                    """, {
                        'subject': relation['subject'],
                        'object': relation['object'],
                        'verb': relation['verb'],
                        'source': source,
                        'source_id': relation['paper_id' if source == 'arxiv' else 'article_id'],
                        'sentence': relation['sentence']
                    })

    def import_document_relations(self,document_relations):
        """导入文档相似度关系"""
        with self.driver.session() as session:
            session.run("CREATE INDEX IF NOT EXISTS FOR (h:HackerNews) ON (h.id)")
            session.run("CREATE INDEX IF NOT EXISTS FOR (a:ArXiv) ON (a.url)")

            for relation in document_relations:
                session.run("""
                    MERGE (h:HackerNews {id: $hn_id})
                    SET h.title = $hn_title
                """, {
                    'hn_id': relation['hackernews_id'],
                    'hn_title': relation['hackernews_title']
                })
                for paper in relation['related_arxiv']:
                    session.run("""
                        MERGE (a:ArXiv {url: $arxiv_url})
                        SET a.title = $paper_title
                        WITH a
                        MATCH (h:HackerNews {id: $hn_id})
                        MERGE (h)-[r:SIMILAR_TO]->(a)
                        SET r.similarity = $similarity
                    """, {
                        'arxiv_url': paper['arxiv_url'],
                        'paper_title': paper['paper_title'],
                        'hn_id': relation['hackernews_id'],
                        'similarity': paper['similarity']
                    })


def main():
    data = load_data('arxiv_papers_clear.json', 'HackerNews_top500.json')
    
    # 查找相关文档
    document_relations = find_related_documents(data)
    
    importer = Neo4jImporter(
        uri="bolt://localhost:7687",
        user="neo4j",
        password="@Vp34qs-y24pHeT"
    )
    try:
        importer.clear_database()
        print("Cleared database")
        importer.import_entities('entity_all.json')
        print("Imported entities")
        importer.import_relations('relation_analysis.json')
        print("Imported relations")
    finally:
        importer.close()

if __name__ == "__main__":
    main()