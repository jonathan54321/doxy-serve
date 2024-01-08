import os 
import shutil

def remove_contents_in_directory(directory_path:str):
    with os.scandir(directory_path) as paths:
        for p in paths:
            if p.is_file():
                os.remove(p.path)
            elif p.is_dir():
                shutil.rmtree(p)

def remove_directory(directory_path:str):
    try:
        shutil.rmtree("./tests/dev-archive")
    except:
        pass

def remove_file(file_path:str):
    try:
        os.remove('./www/db.json')
    except:
        pass      

preserve_dirs = ["./www/uploads", "./www/static/docs", "./tests/data"]
remove_dirs = ["./tests/dev-archive", "./tests/dev-build"]
file_paths = ['./www/db.json']

for d in preserve_dirs:
    remove_contents_in_directory(d)

for d in remove_dirs:
    remove_directory(d)

for p in file_paths:
    remove_file(p)

