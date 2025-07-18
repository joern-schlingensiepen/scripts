import datetime
import os
import filecmp
import shutil

dry_run = True
errors = []


def copytree(src, dst):
    try:
        if not dry_run: shutil.copytree(src, dst)
    except OSError as exc:
        errors.append(exc)
        print(f"Error copying {src} to {dst}: {exc}")

def copy2(src, dst):
    try:
        if not dry_run: shutil.copy2(src, dst)
    except OSError as exc:
        errors.append(exc)
        print(f"Error copying {src} to {dst}: {exc}")

def move(src, dst):
    try:
        if not dry_run: shutil.move(src, dst)
    except OSError as exc:
        errors.append(exc)
        print(f"Error moving {src} to {dst}: {exc}")

def compare_folders(source_folder, target_folder):
    for root, dirs, files in os.walk(source_folder):
        relative_path = os.path.relpath(root, source_folder)
        target_path = os.path.join(target_folder, relative_path)
        
        # Check for files only in source
        for file in files:
            source_file = os.path.join(root, file)
            target_file = os.path.join(target_path, file)
            
            basename = os.path.basename(source_file)
            if basename in ['Thumbs.db', 'desktop.ini']:
                continue

            if not os.path.exists(target_file):
                new_file(source_file, target_file)
            else:
                compare_files(source_file, target_file)
                
        # Check for folders only in source
        for dir in dirs:
            # strip leading dot from relative path
            if relative_path.startswith('.'):
                relative_path = relative_path[1:]
            source_dir = os.path.join(root, dir)
            target_dir = os.path.join(target_path, dir)
            
            if not os.path.exists(target_dir):
                new_folder(source_dir, target_dir)

def create_target_folder(target_folder):
    if not os.path.exists(target_folder):
        create_target_folder(os.path.dirname(target_folder))
        print (f"Create folder {target_folder}")
        if not dry_run: os.makedirs(target_folder)

def new_file(source_file, target_file):
    if os.path.exists(target_file):
        print (f"File {target_file} already exists.")
        return
    create_target_folder (os.path.dirname(target_file))
    print (f"Copy {source_file} to {target_file}")
    if not dry_run: copy2(source_file, target_file)

def compare_files(source_file, target_file):
    if os.path.getmtime(source_file) != os.path.getmtime(target_file) \
    or os.path.getsize(source_file) != os.path.getsize(target_file):   
        update_file(source_file, target_file)

def update_file(source_file, target_file):
    timestamp = os.path.getmtime(target_file)
    timestamp = datetime.datetime.fromtimestamp(timestamp)    
    # format timestamp in sortable format
    timestamp = timestamp.strftime('%Y-%m-%d-%H-%M-%S')
    filename = os.path.basename(target_file)
    docname = os.path.splitext(filename)[0]
    extension = os.path.splitext(filename)[1]

    dirname = os.path.dirname(target_file)
    new_target_file = os.path.join(dirname, f"{timestamp} - {filename}")    
    counter = 0
    while os.path.exists(new_target_file):
        counter += 1        
        new_target_file = os.path.join(dirname, f"{timestamp} - {docname}_{counter:02}{extension}")
    print (f"Move {target_file} to {new_target_file}")
    if not dry_run: move(target_file, new_target_file)
    new_file(source_file, target_file)

def new_folder(source_folder, target_folder):
    if os.path.exists(target_folder):
        return
    print (f"Copy folder {source_folder} to {target_folder}")
    copytree(source_folder, target_folder)    

# Usage example
source_folder = "v:/"
target_folder = "o:/data/"

compare_folders(source_folder, target_folder)

for error in errors:
    print (error)   
