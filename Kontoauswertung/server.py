import asyncio
import sys
import os
import uuid
from flask import Flask, send_file, abort
from nbclient import NotebookClient
from nbformat import read, v4

# Windows-Fix für asyncio + zmq
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

app = Flask(__name__)
PORT = 3580
NOTEBOOK = "Auswertung.ipynb"
OUTPUT_DIR = "output"

os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.route("/auswertung", methods=["GET"])
def run_notebook():
    try:
        # 1. Eindeutigen Dateinamen erzeugen
        run_id = str(uuid.uuid4())
        excel_path = os.path.join(OUTPUT_DIR, f"Book_{run_id}.xlsx")

        # 2. Notebook laden
        with open(NOTEBOOK, encoding="utf-8") as f:
            nb = read(f, as_version=4)

        # 3. Neue Zelle mit tmpFilename einfügen (an dritter Stelle = Index 2)
        param_code = f'tmpFilename = r"{excel_path}"'
        param_cell = v4.new_code_cell(source=param_code)

        while len(nb.cells) < 2:
            nb.cells.append(v4.new_code_cell(source="# Platzhalter"))

        nb.cells.insert(5, param_cell)

        # 4. Notebook ausführen
        client = NotebookClient(nb, timeout=300, kernel_name="python3", allow_errors=False)
        client.execute()

        # 5. Fehlerausgabe sammeln
        errors = []
        for cell in nb.cells:
            if "outputs" in cell:
                for output in cell["outputs"]:
                    if output.output_type == "error":
                        errors.append("\n".join(output.get("traceback", [])))

        # 6. Excel-Datei zurückgeben
        if not os.path.exists(excel_path):
            if errors:
                return "Excel-Datei wurde nicht erstellt." + "\n\n".join(errors), 500, {"Content-Type": "text/plain"}
            
        return send_file(
            excel_path,
            as_attachment=True,
            download_name=os.path.basename(excel_path),
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    except Exception as e:
        return f"Serverfehler:\n{str(e)}", 500, {"Content-Type": "text/plain"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)

