import os
import json
from bs4 import BeautifulSoup

name = os.environ.get('NAME')
input_file = os.environ.get('INPUT_FILE')

with open(input_file, 'r') as facebook:
    data = facebook.read()

soup = BeautifulSoup(data, 'lxml')

messages = []
for message in soup.select('div.message'):
    if message.find(class_='user').string != name:
        continue
    date = message.find(class_='meta').string
    text = message.next_sibling.string
    messages.append({
        'date': date,
        'text': text
    })

print(json.dumps(messages))
