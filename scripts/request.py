import csv
import os
import uuid
import urllib
import datetime
import requests
import json
import time
import htmlmin

from bs4 import BeautifulSoup, Comment

prediction_service_url = "http://localhost:5000/api/predictions"


def clean_html(html):
    soup = BeautifulSoup(html, "html.parser")
    for script in soup(["script", "style", "head"]):  # remove all javascript and stylesheet code
        script.extract()

    comments = soup.findAll(text=lambda text: isinstance(text, Comment))
    for comment in comments:
        comment.extract()

    # return htmlmin(soup.prettify()) # HTML format
    return soup.get_text()  # PLAIN text format


documents = []
questions = []

url_fetching_custom_headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'none',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive'}

with open('input/documents.csv') as documents_csvfile:
    readCSV = csv.DictReader(documents_csvfile, delimiter=',')
    for row in readCSV:
        url_fetch_request = urllib.request.Request(row['url'], headers=url_fetching_custom_headers)
        html = urllib.request.urlopen(url_fetch_request).read().decode()
        text = clean_html(html)

        documents.append({
            'document_url': row['url'],
            'document_content': text,
            'domain': row['domain'],
            'downloaded_date': datetime.datetime.now(),
            'document_id': str(uuid.uuid4())
        })

with open('input/questions.csv') as questions_csvfile:
    readCSV = csv.DictReader(questions_csvfile, delimiter=',')
    for row in readCSV:
        questions.append({
            'question': row['question'],
            'domain': row['domain']
        })

param_documents = []
for document in documents:
    param_documents.append({
        'id': document['document_id'],
        'text': document['document_content']
    })

param_questions = []
for question in questions:
    param_questions.append(question['question'])

data = {
    "documents": param_documents,
    "questions": param_questions,
    "models": "all"
}

# with open('rest_post_data.json', 'w') as f:
#    json.dump(data, f)

creationResponse = requests.post(prediction_service_url, json=data, headers={"Content-Type": "application/json"})

if creationResponse.ok:
    print(creationResponse.json()['id'])

    repeat_request = True
    response_json = None

    while repeat_request:
        print("Checking...")
        getResponse = requests.get(prediction_service_url + "/" + creationResponse.json()['id'],
                                   headers={"Content-Type": "application/json"})
        if getResponse.ok:
            response_json = getResponse.json()
            if len(response_json["models_requested"]) == len(response_json['models_completed']):
                repeat_request = False
            time.sleep(5)
        else:
            repeat_request = False

    if response_json is not None:
        print(response_json)
        if not os.path.exists('output'):
            os.makedirs('output')
        with open('output/output.csv', mode='w') as answers_csv:
            answers_writer = csv.writer(answers_csv, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            answers_writer.writerow([
                'document_url',
                'document_content',
                'domain',
                'downloaded_date',
                'question',
                'answer',
                'model'
            ])

            for document in documents:
                for qa_model_name in response_json['models_completed']:
                    for answer in [item for item in response_json['models'][qa_model_name] if
                                   item.get('document_id') == document['document_id']]:
                        answers_writer.writerow([
                            document['document_url'],
                            document['document_content'].replace("\n", "\\n"),
                            document['domain'],
                            document['downloaded_date'],
                            answer['question'],
                            answer['answer'],
                            qa_model_name,
                        ])


else:
    creationResponse.raise_for_status()
