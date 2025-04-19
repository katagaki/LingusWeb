import os
from os import environ, path
from pathlib import Path
from subprocess import run as run_subprocess
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse, HTMLResponse

app = FastAPI()

input_directory: str = f"./{environ.get('INPUT_DIRECTORY', 'docs')}"
output_directory: str = f"./{environ.get('OUTPUT_DIRECTORY', 'outputs')}"
Path(input_directory).mkdir(parents=True, exist_ok=True)


@app.get("/")
async def serve_index():
    with open("/app/web/index.html", "r") as f:
        return HTMLResponse(content=f.read())


@app.post("/api/process-files")
async def process_files(files: list[UploadFile] = File(...)):
    filenames: list[str] = []
    file_paths: list[str] = []

    for uploaded_file in files:
        file_path: str = path.join(input_directory, uploaded_file.filename)
        file_bytes: bytes = uploaded_file.file.read()

        with open(file_path, "wb") as local_file:
            local_file.write(file_bytes)

        filenames.append(uploaded_file.filename)
        file_paths.append(file_path)

    run_subprocess([
        "uv",
        "run",
        "app.py"
    ])

    for file_path in file_paths:
        try:
            os.remove(file_path)
        except FileNotFoundError:
            print(f"Could not delete file: {file_path}")

    return {
        "files": filenames
    }


@app.get("/api/download-file/{filename}")
async def download_file(filename: str):
    markdown_filename = Path(filename).with_suffix('.md')
    file_path = path.join(str(output_directory), "markdown", str(markdown_filename))

    if not path.exists(file_path):
        raise HTTPException(404, "File not found")

    return FileResponse(file_path, filename=filename)
