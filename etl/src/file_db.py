import json
from pathlib import Path
from itertools import chain


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
        filtered = filter(lambda x: x['name'] == name, chain.from_iterable(db.values()))
        try:
            entry = next(filtered)
            return Path(entry['path'])
        except StopIteration:
            raise KeyError(f"Unable to location {name}")
    
    def by_category(self, category:str):
        return (self.Entry(e['name'], Path(e['path'])) for e in self.get()[category])
    

class RelativePathTransform:
    def __init__(self, logger, db:FilesDatabase, base:Path):
        self._base = base
        self._db = db
        self._logger = logger
    
    def _relative_path_to_base(self, rel:Path, path:Path):
        if path == self._base:
            return rel
        else:
            return self._relative_path_to_base(rel / Path(".."), path.parent)

    def _to_relative(self, name:str, entry:FilesDatabase.Entry):
        my_abs_path = self._db.to_path(name)
        try:
            my_rel_path = self._relative_path_to_base( Path(''), my_abs_path.parent)
            rel_path = entry.path.relative_to(self._base)
            return str(my_rel_path / rel_path)
        except ValueError as e:
            self._logger.error(f"Unable to find a relative path {str(e)}")
            return entry.path 
 
    def get_relative_to(self, name:str, category:str):
        filtered = filter(lambda e: e.name != name, self._db.by_category(category))
        contents = map(lambda e: {'name': e.name, 'path':self._to_relative(name, e)}, filtered)
        return [c for c in contents]
        
    def get_categorized_relative_to(self, name:str):
        contents = {category: self.get_relative_to(name, category) for category in self._db.categories}
        self._logger.info(str(contents))
        return contents