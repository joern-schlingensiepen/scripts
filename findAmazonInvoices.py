import os
import fitz  # PyMuPDF

def find_pdfs_with_text(folder_path, search_text):
    matching_files = []

    # Alle Dateien im Ordner durchgehen
    for filename in os.listdir(folder_path):
        if filename.lower().endswith('.pdf'):
            file_path = os.path.join(folder_path, filename)
            try:
                # PDF öffnen
                with fitz.open(file_path) as doc:
                    # Jede Seite nach dem Text durchsuchen
                    for page in doc:
                        if search_text in page.get_text():
                            matching_files.append(file_path)
                            break  # Wenn gefunden, nächste Datei
            except Exception as e:
                print(f"Fehler beim Lesen von {file_path}: {e}")

    return matching_files

# Beispielhafte Nutzung
if __name__ == "__main__":
    folder = r"W:\Steuer\2024\2024 - Amazon"
    text_to_search = "028-6524976-0316301"
    result_files = find_pdfs_with_text(folder, text_to_search)

    print("PDF-Dateien mit dem gesuchten Text:")
    for file in result_files:
        print(file)
