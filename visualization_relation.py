import streamlit as st
from neo4j import GraphDatabase
import pandas as pd

class Neo4jConnection:
    def __init__(self,uri="bolt://localhost:7687", user="neo4j", password="@Vp34qs-y24pHeT"):
        self.driver = GraphDatabase.driver(uri,auth=(user,password))

    def close(self):
        self.driver.close()

    def get_hackernews(self):
        with self.driver.session() as session:
            result = session.run("""
                MATCH (n:Entity)
                WHERE n.source = 'hackernews'
                RETURN DISTINCT n.source_title as title
                ORDER BY title
            """)
            return [record['title'] for record in result]
        
    def get_related_papers(self, hn_title):
        with self.driver.session() as session:
            result = session.run("""
                MATCH (n:Entity)-[r]-(m:Entity)
                WHERE n.source = 'hackernews' 
                AND n.source_title = $title
                AND m.source = 'arxiv'
                RETURN DISTINCT m.source_title as paper_title, 
                       m.paper_id as paper_id,
                       type(r) as relation_type
                LIMIT 10
            """, title=hn_title)
            papers = []
            for record in result:
                papers.append({
                    "title": record["paper_title"],
                    "id": record["paper_id"],
                    "relation": record["relation_type"]
                })
            return papers

def main():
    st.title("HackerNews & arXiv")

    try:
        conn = Neo4jConnection()

        hn_titles = conn.get_hackernews()

        selected_title = st.selectbox(
            "选择一篇感兴趣的文章",
            hn_titles,
            index=None,
            placeholder="选择文章"
        )
        if selected_title:
            st.write("### 选中的文章：")
            st.write(selected_title)

            related_papers = conn.get_related_papers(selected_title)
            if related_papers:
                st.write("### 相关的arXiv论文：")
            
                # 创建数据表格
                df = pd.DataFrame(related_papers)
                
                # 为每篇论文创建URL
                for index, row in df.iterrows():
                    paper_id = row['id']
                    title = row['title']
                    relation = row['relation']
                    
                    st.write(f"**关系类型:** {relation}")
                    url = f"https://arxiv.org/abs/{paper_id}"
                    st.write(f"**论文:** [{title}]({url})")
                    st.write("---")
            else:
                st.info("没有找到相关的arXiv论文")
    except Exception as e:
        st.error(f"连接数据库出错: {str(e)}")
    
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main()