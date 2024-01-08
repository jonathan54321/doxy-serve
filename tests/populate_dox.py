from shutil import rmtree, move
from os import makedirs, path
import subprocess
import requests
from pprint import pprint
import json

BUILD_DIR = "/code/build"
TEMP_DIR = "/code/temp"
ARCHIVE_DIR = '/code/archive'
SUBMIT_URL = 'http://etl:5000/submit'

rmtree(BUILD_DIR,  ignore_errors=True)
rmtree(TEMP_DIR, ignore_errors=True)
rmtree(ARCHIVE_DIR, ignore_errors=True)
makedirs(ARCHIVE_DIR, exist_ok=True)


test_values = [
    {'name': "0.0.0", 'category': 'releases'},
    {'name': "feature-ID-456", 'category': 'branches'},
    {'name': "0.1.0", 'category': 'releases'},
    {'name': "main", 'category': 'main'},
    {'name': "0.2.1-RC", 'category': 'release-candidates'},
    {'name': "feature-ID-123", 'category': 'branches'},
    {'name': "0.2.0", 'category': 'releases'},
]


def populate_dox(t:dict):
    zip_file_name = f"html-{t['name']}.zip"
    try:
        move(path.join(BUILD_DIR, "_deps"), path.join(TEMP_DIR, "_deps"))
        rmtree(BUILD_DIR)
        makedirs(BUILD_DIR)
        move(path.join(TEMP_DIR, "_deps"), path.join(BUILD_DIR, "_deps"))
    except Exception as e:
        print("Cloning dependent repos")
        pass

    try:
        subprocess.run(["cmake", f"-B{BUILD_DIR}", "-S.", f"-DAPP_VERSION:STRING={t['name']}"]).check_returncode()
        cp = subprocess.run(["make", f"-C{BUILD_DIR}"])
        print(" ".join(cp.args))
        cp.check_returncode()
        build_zip_file = path.join(BUILD_DIR, zip_file_name)
        print(f"Build artifacts are at: {build_zip_file}")
        print(f"Sending to {SUBMIT_URL}")
        resp = requests.post(SUBMIT_URL, params={"name":t['name'], 'category': t['category']}, files=dict(submitted=open(build_zip_file, 'rb')))
        archived_zip_file = path.join(ARCHIVE_DIR, zip_file_name)
        move(build_zip_file, archived_zip_file)
        return json.loads(resp.content.decode("utf-8").strip())
    except subprocess.CalledProcessError as e:
        print("Uh oh..")
        return e.output
        
results = [populate_dox(t) for t in test_values]
pprint(results)