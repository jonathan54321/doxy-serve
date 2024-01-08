import requests
import os

SUBMIT_URL = 'http://localhost:8081/submit'
TEST_FILE_PATH = 'demo/build/html.zip'

response = requests.post(SUBMIT_URL, files=dict(submitted=open(TEST_FILE_PATH, 'rb')))
requests.post(SUBMIT_URL, params=dict(name='doxy'), files=dict(submitted=open(TEST_FILE_PATH, 'rb'))) 

print("\n\n")
print(response.content)