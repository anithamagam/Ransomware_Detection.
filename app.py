from fastapi import FastAPI
from fastapi.responses import FileResponse
import os

app = FastAPI()

@app.get("/")
def serve_ui():
    return FileResponse("index.html")

@app.get("/files")
def files():
    return os.listdir()
