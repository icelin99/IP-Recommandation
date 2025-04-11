import requests
import json
def Spider():
    url = "https://hacker-news.firebaseio.com/v0/topstories.json"
    response = requests.get(url)
    print("Status Code: ", response.status_code)
    print("type of response: ", type(response))

    submission_dics = []
    # get news id
    submission_ids = response.json()
    print("submission_ids: ", submission_ids)

    # get news detail
    attributes = ['by', 'descendants', 'id', 'kids', 'score', 'time', 'title', 'type','url','descendants']
    for submission_id in submission_ids:
        url = f"https://hacker-news.firebaseio.com/v0/item/{submission_id}.json"
        try:
            submission_json = requests.get(url)
            submission_data = submission_json.json()
            for attribute in attributes:
                submission_data[attribute] = submission_data.get(attribute, "None")
            submission_dics.append(submission_data)
            print(f"Got submission {submission_id}, {submission_data['title']}")
        except:
            print(f"Failed to get submission {submission_id}")
    
    print(submission_dics)
    with open("HackerNews_top500.json", "w") as f:
        json.dump(submission_dics, f, indent=4, ensure_ascii=False)

Spider()
