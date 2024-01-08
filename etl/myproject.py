import os
from pathlib import Path
from flask import Flask, flash, request, redirect, url_for, Response
from werkzeug.utils import secure_filename
import json
from zipfile import ZipFile
import logging
from pprint import pprint

UPLOAD_FOLDER = Path('/data/www/uploads')
STATIC_ROOT = Path('/data/www/static')
DOCS_DIR = STATIC_ROOT / Path('docs')
DB_PATH =  Path('/data/www/db.json')
ALLOWED_EXTENSIONS = {'zip'}

app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)
app.config['UPLOAD_FOLDER'] = str(UPLOAD_FOLDER)


class FilesDatabase:
    
    class Entry:
        def __init__(self, name, path):
            self._entry = {'name': name, 'path': path}
        
        @property 
        def name(self):
            return self._entry['name']
        
        @property
        def path(self):
            return Path(self._entry['path'])

    def __init__(self, path:Path):
        self._path = str(path)

    @property
    def categories(self):
        return self.get().keys()

    def add(self, name, category, path):
        db = self.get()
        try:
            entries = db[category]
        except KeyError:
            db[category] = entries = []

        entries.append({'name': name, 'path':str(path)})
        with open(self._path, 'w') as F:
            json.dump(db, F)

    def get(self):
        try:
            with open(self._path, 'r') as F:
                db = json.load(F)
        except:
            with open(self._path, "w") as F:
                db = {}
                json.dump(db, F)
        return db
    
    def to_path(self, name:str):
        db = self.get()
        for entry_list in db.values():
            for entry in entry_list:
                if entry['name'] == name:
                    return Path(entry['path'])
        return DOCS_DIR
    
    def by_category(self, category:str):
        return (self.Entry(e['name'], Path(e['path'])) for e in self.get()[category])
    

class RelativePathTransform:
    def __init__(self, db:FilesDatabase, name:str, base:Path):
        self._name = name
        self._base = base
        self._db = db
    
    def _relative_path_to_base(self, rel:Path, path:Path):
        if path == self._base:
            return rel
        else:
            return self._relative_path_to_base(rel / Path(".."), path.parent)

    def _to_relative(self, entry:FilesDatabase.Entry):
        my_abs_path = self._db.to_path(self._name)
        try:
            my_rel_path = self._relative_path_to_base( Path(''), my_abs_path.parent)
            rel_path = entry.path.relative_to(self._base)
            return str(my_rel_path / rel_path)
        except ValueError as e:
            app.logger.error(f"Unable to find a relative path {str(e)}")
            return entry.path 
 
    def get_relative_to(self, category:str):
        filtered = filter(lambda e: e.name != self._name, self._db.by_category(category))
        contents = map(lambda e: {'name': e.name, 'path':self._to_relative(e)}, filtered)
        return [c for c in contents]
        
    def get_categorized_relative_to(self):
        contents = {category: self.get_relative_to(category) for category in self._db.categories}
        app.logger.info(str(contents))
        return contents


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


@app.route("/")
def hello():
    return "<h1 style='color:blue'>Hello World!</h1>"

@app.route("/contents/<name>")
def retrieve_contents(name:str):
    paths = RelativePathTransform( FilesDatabase(DB_PATH), name, DOCS_DIR)
    resp = Response(json.dumps(paths.get_categorized_relative_to()))
    #resp.headers['Access-Control-Allow-Origin'] = 'http://localhost:8080'
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

if __name__ == "__main__":
    app.run(host='0.0.0.0')