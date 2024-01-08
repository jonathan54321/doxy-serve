from datetime import date, timedelta
from jinja2 import Environment, FileSystemLoader
import os
from zipfile import ZipFile
from shutil import rmtree
import requests


def generate_archive_from_content(directory, meta, contents):
    temp_dir = os.path.join(directory, "temp")
    os.makedirs(temp_dir, exist_ok=True)
    index_path = os.path.join(temp_dir, 'index.html')
    with open(index_path, 'w') as F:
        F.write(contents)
    
    archive_file_path = os.path.join(directory, f'archive-{meta}.zip')
    with ZipFile(archive_file_path, 'w') as F:
        F.write(index_path, arcname='index.html')
    
    rmtree(temp_dir)
    return archive_file_path


dates = [date.today() + timedelta(i) for i in range(5)]

environment = Environment(loader=FileSystemLoader("./tests"))
template = environment.get_template("index.html.template")
file_contents = [template.render(date=d, i=i) for (i,d) in enumerate(dates)]

archive_dir = r'tests/data'
os.makedirs(archive_dir, exist_ok=True)
archives = [generate_archive_from_content(archive_dir, d,c) for (d,c) in zip(dates, file_contents)]

SUBMIT_URL = 'http://localhost:8081/submit'
responses = [requests.post(SUBMIT_URL,
                           params={"name":str(d)},
                           files=dict(submitted=open(a, 'rb'))) for d,a in zip(dates,archives)]

for r in responses:
    print(r.request)