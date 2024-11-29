from flask import Flask, render_template, request, redirect, flash, send_file
from rich.console import Console
from zipfile import ZipFile
import warnings
import pandas as pd
import numpy as np
import os
import chardet
import shutil

warnings.filterwarnings("ignore", category=FutureWarning, message=".*swapaxes.*")

app = Flask(__name__)
app.secret_key = "aduahe7432478reuidnqd1d"

OUTPUT_DIR = os.path.join(os.getcwd(), "output_files")

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def process_file(file_path, chunk_size, remove_na):
    try:
        encoding = detect_encoding(file_path)
        if file_path.endswith(".xlsx"):
            df = pd.read_excel(file_path, engine="openpyxl")
        else:
            try:
                df = pd.read_csv(file_path, encoding=encoding, sep=";")
            except pd.errors.ParserError:
                df = pd.read_csv(file_path, encoding=encoding, sep=",")
        if remove_na:
            df = df.dropna()
        chunks_dir = os.path.join(OUTPUT_DIR, "chunks")
        os.makedirs(chunks_dir, exist_ok=True)

        for i, chunk in enumerate(range(0, len(df), chunk_size)):
            chunk_df = df.iloc[chunk:chunk + chunk_size]
            output_file = os.path.join(chunks_dir, f"resultados_{i+1}.csv")
            chunk_df.to_csv(output_file, index=False, sep=";")

        zip_file = os.path.join(OUTPUT_DIR, "resultados.zip")
        with ZipFile(zip_file, "w") as zipf:
            for root, _, files in os.walk(chunks_dir):
                for file in files:
                    zipf.write(os.path.join(root, file), arcname=os.path.basename(file))
        shutil.rmtree(chunks_dir)
        return zip_file
    except Exception as e:
        print(f"Erro ao processar o arquivo: {e}")
        return None

def detect_encoding(file_path):
    with open(file_path, "rb") as file:
        file_content = file.read(1000)
    result = chardet.detect(file_content)
    return result["encoding"] or "utf-8"

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files.get("file")
        chunk_size = int(request.form.get("chunk_size", 20000))
        remove_na = request.form.get("remove_na") == "true"
        if not file:
            flash("Por favor, selecione um arquivo!", "danger")
            return redirect(request.url)
        file_path = os.path.join(OUTPUT_DIR, file.filename)
        file.save(file_path)
        zip_file = process_file(file_path, chunk_size, remove_na)
        if zip_file and os.path.exists(zip_file):
            return send_file(zip_file, as_attachment=True)
        flash("Erro ao processar o arquivo.", "danger")
        return redirect(request.url)
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
