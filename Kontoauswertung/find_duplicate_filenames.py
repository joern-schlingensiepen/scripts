import os

def fix_double_pdf_extension(root_dir):
    """
    Durchsucht alle Unterverzeichnisse von root_dir und benennt alle Dateien um, deren Name auf .pdf.pdf endet,
    sodass sie nur noch einmal .pdf als Extension haben.
    """
    for dirpath, _, filenames in os.walk(root_dir):
        for fname in filenames:
            if fname.lower().endswith('.pdf.pdf'):
                old_path = os.path.join(dirpath, fname)
                new_name = fname[:-4]  # Entfernt das letzte '.pdf'
                new_path = os.path.join(dirpath, new_name)
                try:
                    os.rename(old_path, new_path)
                    print(f"Umbenannt: {old_path} -> {new_path}")
                except Exception as e:
                    print(f"Fehler beim Umbenennen von {old_path}: {e}")

# Beispiel für die Nutzung:
# fix_double_pdf_extension(r"W:\Dokument-Download")
