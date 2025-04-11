import json
import spacy
from collections import Counter
import en_core_web_sm

def load_data(arxiv_file, hackernews_file):
    data = {'arxiv': [], 'hackernews': []}
    with open(arxiv_file, "r") as f:
        arxiv_papers = json.load(f)
        data['arxiv'] = arxiv_papers
    with open(hackernews_file, "r") as f:
        hackernews_articles = json.load(f)
        data['hackernews'] = hackernews_articles
    return data

def extract_entities(data_source):
    # 加载spacy模型
    nlp = en_core_web_sm.load()

    entities = {
        'arxiv': {
            'PERSON': [],      # 人名
            'ORG': [],        # 组织
            'GPE': [],        # 地理政治实体
            'PRODUCT': [],    # 产品
            'WORK_OF_ART': [] # 作品
        },
        'hackernews': {
            'PERSON': [],
            'ORG': [],
            'GPE': [],
            'PRODUCT': [],
            'WORK_OF_ART': []
        }
    }
    # process arxiv
    for paper in data_source['arxiv']:
        text = paper['title'] + ". " + paper['summary']
        doc = nlp(text)
        for ent in doc.ents:
            if ent.label_ in entities['arxiv']:
                entity_info = {
                    "text": ent.text,
                    "paper_title": paper['title'],
                    "paper_id": paper['id'],
                    "type": 'arxiv'
                }
                entities['arxiv'][ent.label_].append(entity_info)

    # process hackernews
    for article in data_source['hackernews']:
        text = article['title']
        doc = nlp(text)
        for ent in doc.ents:
            if ent.label_ in entities['hackernews']:
                entity_info = {
                    "text": ent.text,
                    "paper_title": article['title'],
                    "paper_id": article['id'],
                    "type": 'hackernews'
                }
                entities['hackernews'][ent.label_].append(entity_info)
    
    return entities

def analyze_entities(entities):
    stats = {}
    
    for source in ['arxiv', 'hackernews']:
        stats[source] = {
            'counts': {},
            'most_common': {}
        }
        
        for entity_type, entity_list in entities[source].items():
            # 计算总数
            stats[source]['counts'][entity_type] = len(entity_list)
            
            # 计算最常见实体
            counter = Counter([e['text'].lower() for e in entity_list])
            stats[source]['most_common'][entity_type] = counter.most_common(10)
    
    return stats

def save_result(entities, stats, output_file):
    output = {
        'statistics': stats,
        'detailed_entities': entities
    }
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=4, ensure_ascii=False)
    
    # 打印统计信息
    for source in ['arxiv', 'hackernews']:
        print(f"\n{source.upper()} entities:")
        for entity_type, count in stats[source]['counts'].items():
            print(f"{entity_type}: {count} entities")
        
        print(f"\n{source.upper()} most common entities:")
        for entity_type, entities in stats[source]['most_common'].items():
            print(f"\n{entity_type}:")
            for entity, count in entities:
                print(f"  - {entity}: {count} times")

def main():
    data = load_data("arxiv_papers_clear.json", "HackerNews_top500.json")
    entities = extract_entities(data)
    stats = analyze_entities(entities)
    save_result(entities, stats, "entity_all.json")

if __name__ == "__main__":
    main()