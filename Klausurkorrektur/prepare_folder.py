import os
import re
import zipfile
import logging
from datetime import datetime

# Initialisiere Logging mit Timestamp
log_filename = f"log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename),  # Log-Datei
        logging.StreamHandler()            # Konsole
    ]
)
def list_directory_contents(directory):
    """Listet den Inhalt eines Verzeichnisses auf."""
    try:
        contents = os.listdir(directory)
        logging.info(f"Inhalt von '{directory}': {contents}")
        return contents
    except FileNotFoundError:
        logging.error(f"Verzeichnis '{directory}' nicht gefunden.")
        return []

def find_zip_file(contents):
    """Sucht nach einer Datei im Format Kxxxxxx.zip."""
    for file in contents:
        if re.match(r"K\d{6}\.zip", file):
            logging.info(f"Gefundene ZIP-Datei: {file}")
            return file
    logging.error("Keine Datei im Format Kxxxxxx.zip gefunden.")
    return None

def extract_zip_file(zip_path, target_dir):
    """Entpackt die ZIP-Datei in ein Zielverzeichnis."""
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(target_dir)
        logging.info(f"ZIP-Datei '{zip_path}' erfolgreich nach '{target_dir}' entpackt.")
    except zipfile.BadZipFile:
        logging.error(f"Fehler beim Entpacken der Datei '{zip_path}'.")

def list_html_files(src_dir):
    """Listet alle .html-Dateien in einem Verzeichnis und seinen Unterverzeichnissen auf."""
    html_files = []
    for root, _, files in os.walk(src_dir):
        for file in files:
            if file.endswith(".html"):
                html_file_path = os.path.join(root, file)
                html_file_relative = os.path.relpath(html_file_path, src_dir)
                logging.info(f"Gefundene .html-Datei: {html_file_relative}")
                # Open the file to check if it has more than 7 lines
                with open(html_file_path, 'r', encoding='utf-8') as f:
                    line_count = sum(1 for _ in f)
                logging.info(f"Anzahl der Zeilen in {html_file_relative}: {line_count}")
                if line_count <= 7:
                    logging.warning(f"ACHTUNG: Die Datei {html_file_relative} hat weniger als 8 Zeilen, in der Regel fehlt dann was, denn das Template hat 8 Zeilen.")

                html_files.append(html_file_relative)
    if html_files:
        logging.info(f"Gefundene .html-Dateien: {html_files}")
        logging.info(f"Anzahl der .html-Dateien: {len(html_files)}")
    else:
        logging.error("Keine .html-Dateien gefunden.")
    return html_files

def list_png_files(src_dir):
    """Listet alle .png-Dateien in einem Verzeichnis und seinen Unterverzeichnissen auf."""
    png_files = []
    for root, _, files in os.walk(src_dir):
        for file in files:
            if file.endswith(".png"):
                png_file_path = os.path.join(root, file)
                # Open the file to check if it is a valid PNG file and 
                # log the dimensions
                try:
                    with open(png_file_path, 'rb') as f:
                        header = f.read(8)
                        if header.startswith(b'\x89PNG\r\n\x1a\n'):
                            logging.info(f"Die Datei {file} ist eine gültige PNG-Datei.")
                            # Read the dimensions of the PNG file
                            f.seek(16)
                            width, height = int.from_bytes(f.read(4), 'big'), int.from_bytes(f.read(4), 'big')
                            logging.info(f"Dimensionen der PNG-Datei {file}: {width}x{height} Pixel")
                            if width < 100 or height < 100:
                                logging.warning(f"ACHTUNG: Die PNG-Datei {file} ist kleiner als 100x100 Pixel, was in der Regel nicht gewünscht ist.")                                
                        else:
                            logging.warning(f"Die Datei {file} ist keine gültige PNG-Datei.")
                except Exception as e:
                    logging.error(f"Fehler beim Lesen der Datei {file}: {e}")
                    continue

                png_file_relative = os.path.relpath(png_file_path, src_dir)
                logging.info(f"Gefundene .png-Datei: {png_file_relative}")
                png_files.append(png_file_relative)
    if png_files:
        logging.info(f"Gefundene .png-Dateien: {png_files}")
        logging.info(f"Anzahl der .png-Dateien: {len(png_files)}")
    else:
        logging.error("Keine .png-Dateien gefunden.")
    return png_files

def list_java_files(src_dir):
    """Listet alle .java-Dateien in einem Verzeichnis und seinen Unterverzeichnissen auf."""
    java_files = []
    for root, _, files in os.walk(src_dir):
        for file in files:
            if file.endswith(".java"):
                java_file_path = os.path.join(root, file)
                java_file_relative = os.path.relpath(java_file_path, src_dir)
                logging.info(f"Gefundene .java-Datei: {java_file_relative}")
                # count the number of lines in the file
                with open(java_file_path, 'r', encoding='utf-8') as f:
                    line_count = sum(1 for _ in f)
                logging.info(f"Anzahl der Zeilen in {java_file_relative}: {line_count}")
                if line_count <= 4:
                    logging.warning(f"ACHTUNG: Die Datei {java_file_relative} hat weniger als 5 Zeilen, in der Regel fehlt dann was, denn das Template hat 5 Zeilen.")
                java_files.append(java_file_relative)
    if java_files:
        logging.info(f"Gefundene .java-Dateien: {java_files}")
        logging.info(f"Anzahl der .java-Dateien: {len(java_files)}")
    else:
        logging.error("Keine .java-Dateien gefunden.")
    return java_files

def count_subdirectories(directory, pattern):
    """Zählt Unterverzeichnisse, die einem bestimmten Muster entsprechen."""
    subdirs = [d for d in os.listdir(directory) if os.path.isdir(os.path.join(directory, d)) and re.match(pattern, d)]
    if subdirs:
        logging.info(f"Gefundene Unterverzeichnisse: {subdirs}")
        logging.info(f"Anzahl der Unterverzeichnisse: {len(subdirs)}")
    else:
        logging.error("Keine passenden Unterverzeichnisse gefunden.")
    return len(subdirs)

def main(source, target):
    """Hauptfunktion des Skripts."""
    contents = list_directory_contents(source)
    for content in contents:
        process_submission(source, target, content)

def process_submission(source, target, content):
    """Verarbeitet eine einzelne Einreichung."""

    break_line = 20 * "*** "

    logging.info(break_line)
    logging.info(break_line)
    logging.info(f"Verarbeite Einreichung: {content}")
    logging.info(break_line)
    logging.info(break_line)
    submission_path = os.path.join(source, content)    
    entries = list_directory_contents(submission_path)
    zip_file = find_zip_file(entries)
    if zip_file:
        logging.info(f"Verarbeite ZIP-Datei: {zip_file}")
        zip_path = os.path.join(submission_path, zip_file)
        target_dir = os.path.join(target, os.path.splitext(zip_file)[0])
        os.makedirs(target_dir, exist_ok=True)
        print (f"Entpacke {zip_path} nach {target_dir}...")
        extract_zip_file(zip_path, target_dir)
       
        
        while True:        
            src_dir = os.path.join(target_dir, "src")
            sub_dir = os.path.join(target_dir, zip_file[:-4])  # Entferne .zip-Endung
            if os.path.exists(src_dir): 
                logging.info(f"Verzeichnis 'src' gefunden in '{target_dir}'.")
                break
            elif os.path.exists(sub_dir):
                target_dir = sub_dir
                logging.info(f"Verzeichnis '{sub_dir}' gefunden, wechsle zu diesem Verzeichnis.")
            else:
                logging.error(f"Kein Unterverzeichnis 'src' oder '{zip_file[:-4]}' gefunden in '{target_dir}'.")
                break
        
        if os.path.exists(src_dir):
            list_java_files(src_dir)
            list_png_files(src_dir)  # Ensure this function is defined
            list_html_files(src_dir)
            count_subdirectories(src_dir, r"A\d{2}")
        else:
            logging.error(f"Unterverzeichnis 'src' nicht gefunden in '{target_dir}'.")       
    else:
        logging.error("Keine gültige ZIP-Datei gefunden. Verarbeitung wird fortgesetzt.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Verarbeitet Dateien und Verzeichnisse gemäß den Anforderungen.")
    parser.add_argument("source", help="Pfad zum Quellverzeichnis")
    parser.add_argument("target", help="Pfad zum Zielverzeichnis")
    args = parser.parse_args()
    main(args.source, args.target)