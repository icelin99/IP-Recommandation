import json

def clear_arxiv_papers(input_file,output_file):
    with open(input_file, "r") as f:
        papers = json.load(f)
    cleaned_dict = {}
    for paper in papers:
        title = paper['title'].lower().strip()
        if title in cleaned_dict:
            existing_date = cleaned_dict[title]['updated']
            current_date = paper['updated']
            # 如果当前论文更新时间更新，则替换
            if current_date > existing_date:
                cleaned_dict[title] = paper
        else:
            cleaned_dict[title] = paper
    cleaned_papers = list(cleaned_dict.values())
    cleaned_papers.sort(key=lambda x: x['updated'], reverse=True)

    with open(output_file, "w") as f:
        json.dump(cleaned_papers, f, indent=4, ensure_ascii=False)

def clear_hackernews(input_file,output_file):
    with open(input_file, "r") as f:
        articles = json.load(f)
    cleaned_dict = {}
    for article in articles:
        title = article['title'].lower().strip()
        if title in cleaned_dict:
            print(f"Duplicate title: {title}")
            if article['time'] > cleaned_dict[title]['time']:
                cleaned_dict[title] = article
        else:
            cleaned_dict[title] = article
    cleaned_articles = list(cleaned_dict.values())
    with open(output_file, "w") as f:
        json.dump(cleaned_articles, f, indent=4, ensure_ascii=False)

# clear_arxiv_papers("arxiv_papers.json", "arxiv_papers_clear.json")
# clear_hackernews("HackerNews_top500.json", "HackerNews_top500_clear.json")
