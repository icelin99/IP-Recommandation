import json
import spacy
from collections import defaultdict
import en_core_web_sm
import faiss
from transformers import AutoTokenizer, AutoModel
import torch
import numpy as np
from tqdm import tqdm

class DocumentSimilaritySearch:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained('sentense-transformers/all-MiniLM-L12-v2')
        self.model = AutoModel.from_pretrained('sentense-transformers/all-MiniLM-L6-v2')
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)
    
    def get_embedding(self, texts, batch_size=16):
        """生成文本嵌入向量
            Args:
                texts: 文本列表
                batch_size: 批处理大小
                
            Returns:
                numpy.ndarray: 文本嵌入向量矩阵
        """
        embeddings = []

        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i+batch_size]
            encoded = self.tokenizer(
                batch_texts,
                padding=True,
                truncation=True,
                max_length=512,
                return_tensors='pt'
            )
            encoded.to(self.device)
            
            # 获取BERT输出
            with torch.no_grad():
                outputs = self.model(**encoded)
                # 获取注意力掩码
                attention_mask = encoded['attention_mask']

                # 使用平均池化获取文档表示
                # 最后一层隐藏状态: [batch_size, sequence_length, hidden_size]
                last_hidden = outputs.last_hidden_state

                # 扩展注意力掩码维度以匹配隐藏状态
                attention_mask_expanded = attention_mask.unsqueeze(-1).expand(last_hidden.size()).float()
                
                # 应用掩码并计算平均值
                sum_embeddings = torch.sum(last_hidden * attention_mask_expanded, 1)
                sum_mask = torch.clamp(attention_mask_expanded.sum(1), min=1e-9)
                batch_embeddings = (sum_embeddings / sum_mask).cpu().numpy()
                
                embeddings.append(batch_embeddings)

        return np.vstack(embeddings)
    

def find_related_documents(data_source):
    """使用FAISS查找相关文档"""
    similarity_search = DocumentSimilaritySearch()

    arxiv_texts = []
    arxiv_papers = []
    # 创建id到索引的映射
    id_to_idx = {}
    for idx, paper in enumerate(tqdm(data_source['arxiv'], desc="处理arXiv文档")):
        arxiv_texts.append(paper['title'] + ". " + paper['summary'])
        arxiv_papers.append({
            'url': str(paper['id']),  # 论文URL
            'title': paper['title']
        })
        id_to_idx[str(paper['id'])] = idx
    # 获取embeddings
    arxiv_embeddings = similarity_search.get_embedding(arxiv_texts)

    # 构建FAISS索引
    dimension = arxiv_embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(arxiv_embeddings.astype('float32'))

    document_relations = []
    batch_size = 16

    # 批量处理HackerNews
    hn_articles = [(article['id'], article['title']) for article in data_source['hackernews']]
    for i in tqdm(range(0, len(hn_articles), batch_size), 
                 desc="计算文档相似度", 
                 total=(len(hn_articles) + batch_size - 1) // batch_size):
        batch_articles = hn_articles[i:i+batch_size]
        batch_texts = [article[1] for article in batch_articles]

        query_embeddings = similarity_search.get_embedding(batch_texts)
        k = 5 # 返回最相似的5个文档
        distances, indices = index.search(query_embeddings.astype('float32'), k)

        for j, (article_id, article_title) in enumerate(batch_articles):
            top_related = [
                {
                    'arxiv_url': arxiv_papers[idx]['url'],
                    'similarity': float(1 / (1 + distances[j][i])),
                    'paper_title': arxiv_papers[idx]['title']
                }
                for i, idx in enumerate(indices[j])
                if idx < len(arxiv_papers)
            ]
            document_relations.append({
                'hackernews_id': str(article_id),
                'hackernews_title': article_title,
                'related_arxiv': top_related
            })
    return document_relations


def load_data(arxiv_file, hackernews_file):
    data = {'arxiv': [], 'hackernews': []}
    with open(arxiv_file, 'r', encoding='utf-8') as f:
        data['arxiv'] = json.load(f)
    with open(hackernews_file, 'r', encoding='utf-8') as f:
        data['hackernews'] = json.load(f)
    return data

def extract_relations(data_source):
    nlp = en_core_web_sm.load()
    relations = {
        'arxiv': {
            'subject_verb_object': [],
            'entity_entity': [],
            'entity_action': []
        },
        'hackernews': {
            'subject_verb_object': [],
            'entity_entity': [],
            'entity_action': []
        }
    }

    # process arxiv
    for paper in data_source['arxiv']:
        text = paper['title'] + ". " + paper['summary']
        doc = nlp(text)
        # extract subject-verb-object relations
        for sent in doc.sents:
            for token in sent:
                if token.dep_ == 'nsubj' and token.head.dep_ == 'VERB':
                    for child in token.head.children:
                        if child.dep_ == 'dobj':
                            relation = {
                                'subject': token.text,
                                'verb': token.head.text,
                                'object': child.text,
                                'sentence': sent.text,
                                'paper_id': paper['id'],
                                'paper_title': paper['title']
                            }
                            relations['arxiv']['subject_verb_object'].append(relation)

        # extract entity-entity relations
        entities = list(doc.ents)
        for i in range(len(entities)):
            for j in range(i+1, len(entities)):
                if entities[i].label_ in ['ORG', 'PERSON', 'PRODUCT'] and \
                   entities[j].label_ in ['ORG', 'PERSON', 'PRODUCT']:
                    relation = {
                        'entity1': {
                            'text': entities[i].text,
                            'type': entities[i].label_
                        },
                        'entity2': {
                            'text': entities[j].text,
                            'type': entities[j].label_
                        },
                        'paper_id': paper['id'],
                        'paper_title': paper['title']
                    }
                    relations['arxiv']['entity_entity'].append(relation)

        # extract entity-action relations
        for ent in doc.ents:
            if ent.label_ in ['ORG', 'PERSON', 'PRODUCT']:
                for token in doc:
                    if token.dep_ == "VERB" and token.head.pos_ == "VERB":
                        relation = {
                            'entity': {
                                'text': ent.text,
                                'type': ent.label_
                            },
                            'action': token.text,
                            'paper_id': paper['id'],
                            'paper_title': paper['title']
                        }
                        relations['arxiv']['entity_action'].append(relation)

    # process hackernews
    for article in data_source['hackernews']:
        text = article['title']
        doc = nlp(text)
        for sent in doc.sents:
            for token in sent:
                if token.dep_ == 'nsubj' and token.head.dep_ == 'VERB':
                    for child in token.head.children:
                        if child.dep_ == 'dobj':
                            relation = {
                                'subject': token.text,
                                'verb': token.head.text,
                                'object': child.text,
                                'sentence': sent.text,
                                'article_id': article['id'],
                                'article_title': article['title']
                            }
                            relations['hackernews']['subject_verb_object'].append(relation)
        entities = list(doc.ents)
        for i in range(len(entities)):
            for j in range(i + 1, len(entities)):
                if entities[i].label_ in ['ORG', 'PERSON', 'PRODUCT'] and \
                   entities[j].label_ in ['ORG', 'PERSON', 'PRODUCT']:
                    relation = {
                        'entity1': {
                            'text': entities[i].text,
                            'type': entities[i].label_
                        },
                        'entity2': {
                            'text': entities[j].text,
                            'type': entities[j].label_
                        },
                        'article_id': article['id'],
                        'article_title': article['title']
                    }
                    relations['hackernews']['entity_entity'].append(relation)

    return relations

def analyze_relations(relations):
    stats = {}
    for source in ['arxiv', 'hackernews']:
        stats[source] = {
            'relation_counts': {
                'subject_verb_object': len(relations[source]['subject_verb_object']),
                'entity_entity': len(relations[source]['entity_entity']),
                'entity_action': len(relations[source]['entity_action'])
            },
            'common_patterns': {
                'subject_verb': defaultdict(int),
                'entity_pairs': defaultdict(int)
            }
        }
        for rel in relations[source]['subject_verb_object']:
            pattern = f"{rel['subject']}_{rel['verb']}"
            stats[source]['common_patterns']['subject_verb'][pattern] += 1
        for rel in relations[source]['entity_entity']:
            pair = f"{rel['entity1']['text']}_{rel['entity2']['text']}"
            stats[source]['common_patterns']['entity_pairs'][pair] += 1
        stats[source]['common_patterns']['subject_verb'] = sorted(
            stats[source]['common_patterns']['subject_verb'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        stats[source]['common_patterns']['entity_pairs'] = sorted(
            stats[source]['common_patterns']['entity_pairs'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
    
    return stats

def save_relations(relations, stats, output_file):
    output = {
        'statistics': stats,
        'detailed_relations': relations
    }
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=4)

    for source in ['arxiv', 'hackernews']:
        print(f"\n{source.upper()} 关系统计:")
        for rel_type, count in stats[source]['relation_counts'].items():
            print(f"{rel_type}: {count} 个关系")
        
        print(f"\n{source.upper()} 常见主谓模式:")
        for pattern, count in stats[source]['common_patterns']['subject_verb']:
            print(f"  - {pattern}: {count}次")
        
        print(f"\n{source.upper()} 常见实体对:")
        for pair, count in stats[source]['common_patterns']['entity_pairs']:
            print(f"  - {pair}: {count}次")

def save_document_relations(document_relations, output_file):
    output = {
        'document_relations': document_relations,
        'statistics': {
            'total_relations': len(document_relations),
            'average_similarity': sum(
                sum(paper['similarity'] for paper in rel['related_papers']) 
                for rel in document_relations
            ) / sum(len(rel['related_papers']) for rel in document_relations)
        }
    }
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=4)
    
    print(f"文档关系已保存到: {output_file}")
    print(f"总关系数: {output['statistics']['total_relations']}")
    print(f"平均相似度: {output['statistics']['average_similarity']:.3f}")

def main():
    data = load_data('arxiv_papers_clear.json', 'HackerNews_best200.json')
    relations = find_related_documents(data)
    save_document_relations(relations, 'document_relations.json')

if __name__ == "__main__":
    main()
