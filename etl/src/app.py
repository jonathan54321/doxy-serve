from file_db import FilesDatabase, RelativePathTransform
import os
from pathlib import Path
from flask import Flask,  request, Response
from werkzeug.utils import secure_filename
import json
from zipfile import ZipFile
import logging


UPLOAD_FOLDER = Path('/data/www/uploads')
STATIC_ROOT = Path('/data/www/static')
DOCS_DIR = STATIC_ROOT / Path('docs')
DB_PATH =  Path('/data/www/db.json')
ALLOWED_EXTENSIONS = {'zip'}

app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)
app.config['UPLOAD_FOLDER'] = str(UPLOAD_FOLDER)



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract(name, zipfile_path):

    zipfile_name = os.path.basename(zipfile_path)
    destination_dir = str(DOCS_DIR / Path(name))
    app.logger.info(f"zipfile_name: {zipfile_name}")
    app.logger.info(f"destination_dir: {destination_dir}")
    os.makedirs(destination_dir, exist_ok=True)
    with ZipFile(zipfile_path, 'r') as F:
        F.extractall(path=destination_dir)
    dest_entry = os.path.join(destination_dir, 'index.html')
    return dest_entry


def add_to_db(name, category, path):
    db = FilesDatabase(DB_PATH)
    db.add(name, category, path)
    return None

@app.route('/submit', methods=['POST'])
def upload_file():
    result = {"error": "none"}
    try:
        name, category, file = (request.args.get('name'), 
                                request.args.get('category'), 
                                request.files['submitted'])
    except KeyError as e:
        key = next(e.args)
        result = {}
        if key == 'name':
            result['error'] = 'no name'
        elif key == 'category':
            result['error'] =  'no category'
        elif key == 'submitted':
            result['error'] = 'no file'
        return result
        
    if not allowed_file(file.filename):
        result['error'] = 'invalid filename'
        result['filename'] = file.filename
        return result

    filename = secure_filename(file.filename)
    zipfile_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(zipfile_path)
    dest_path = extract(name, zipfile_path)
    add_to_db(name, category, Path(dest_path))
    return result


@app.route("/contents/<name>")
def retrieve_contents(name:str):
    paths = RelativePathTransform(app.logger, FilesDatabase(DB_PATH), DOCS_DIR)
    resp_json = json.dumps(paths.get_categorized_relative_to(name)
    resp = Response(resp_json)
    #resp.headers['Access-Control-Allow-Origin'] = 'http://localhost:8080'
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

if __name__ == "__main__":
    app.run(host='0.0.0.0')