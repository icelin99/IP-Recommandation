import requests
import json
from xml.etree import ElementTree as ET
import time

def get_arxiv_papers(start = 0, max_results = 100):
    all_papers = []
    batch_size = 2000 if max_results >= 2000 else 1
    remaining_results = max_results
    current_start = start
    while remaining_results > 0:
        current_batch_size = min(batch_size, remaining_results)
        url = "http://export.arxiv.org/api/query?"
        query_params = {
            "search_query": "cat:cs.AI",  # 查询cs.AI类别
            "start": current_start,
            "max_results": current_batch_size,
            "sortBy": "lastUpdatedDate",
            "sortOrder": "descending"
        }
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.get(url, params=query_params)
                print(f"获取第 {current_start} 到 {current_start + current_batch_size} 条数据")
                print(f"尝试 {attempt + 1}/{max_retries}, Status Code: {response.status_code}")
                if response.status_code != 200:
                    print("error request")
                    continue
                if response.status_code == 500:
                    wait_time = (attempt +1) * 2
                    time.sleep(wait_time)
                    continue
                root = ET.fromstring(response.content)
                batch_papers = []
                for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
                    try:
                        paper = {
                            "title": entry.find('{http://www.w3.org/2005/Atom}title').text.strip(),
                            "id": entry.find('{http://www.w3.org/2005/Atom}id').text,
                            "published": entry.find('{http://www.w3.org/2005/Atom}published').text,
                            "updated": entry.find('{http://www.w3.org/2005/Atom}updated').text.strip(),
                            "author": [author.find('{http://www.w3.org/2005/Atom}name').text 
                                    for author in entry.findall('{http://www.w3.org/2005/Atom}author')],
                            "summary": entry.find('{http://www.w3.org/2005/Atom}summary').text.strip(),
                        }
                        batch_papers.append(paper)
                    except (AttributeError, ET.ParseError) as e:
                        print(f"Error processing entry: {e}")
                        continue
                all_papers.extend(batch_papers)
                print(f"Got {len(batch_papers)} batch papers")
                current_start += len(batch_papers)
                remaining_results -= len(batch_papers)
                time.sleep(5)
                break
            except requests.exceptions.RequestException as e:
                print(f"请求失败: {e}")
                return None
            except ET.ParseError as e:
                print(f"XML解析失败: {e}")
                return None
    with open("arxiv_papers.json", "w") as f:
        json.dump(all_papers, f, indent=4, ensure_ascii=False)
    print(f"Got {len(all_papers)} papers")
    return all_papers
    
if __name__ == "__main__":
    papers = get_arxiv_papers(start=0, max_results=20000)