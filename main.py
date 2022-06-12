import os
import pathlib
import sqlite3
import uuid
from datetime import datetime

import uvicorn
from fastapi import FastAPI, UploadFile, HTTPException, status

app = FastAPI()

FILE_FOLDER_NAME = "buckets"

BASE_FOLDER = pathlib.Path(__file__).resolve().parent
FILE_FOLDER = BASE_FOLDER / FILE_FOLDER_NAME


def get_or_create_bucket(bucket_name):
    bucket_folder = FILE_FOLDER / bucket_name
    bucket_folder.mkdir(parents=False, exist_ok=True)
    return bucket_folder


def delete_file(file_path):
    os.remove(file_path)


@app.post('/frames/')
async def create_frames(files: list[UploadFile]):
    if len(files) > 15:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Нельзя больше 15 файлов")

    buff_files = {}
    for file in files:
        if "jpeg" not in file.filename:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Нельзя формат кроме jpeg")
        uid = f"{uuid.uuid4()}.jpeg"
        buff_files[uid] = file

    bucket_name = datetime.now().strftime("%Y%m%d")
    bucket_folder = get_or_create_bucket(bucket_name)
    for file_name, file in buff_files.items():
        with open(bucket_folder / file_name, "wb") as f:
            data = await file.read()
            f.write(data)

    with sqlite3.connect("sqlite.db", check_same_thread=False) as conn:
        cur = conn.cursor()
        rows = []
        for file_name in buff_files:
            cur.execute("""INSERT INTO inbox (code, name) VALUES (?,?)""", (None, file_name))
            rows.append(cur.lastrowid)

    result = {row: name for row, name in zip(rows, buff_files)}
    return result


@app.get("/frames/{code}")
def get_frames(code: int):
    with sqlite3.connect("sqlite.db", check_same_thread=False) as conn:
        cur = conn.cursor()
        cur.execute("""SELECT * FROM inbox WHERE code=?""", (code,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Нет такой картинки")
        code, name, moment = row
        return {"momet": moment, "name": name}


@app.delete("/frames/{code}")
def delete_frames(code: int):
    with sqlite3.connect("sqlite.db", check_same_thread=False) as conn:
        cur = conn.cursor()
        cur.execute("""SELECT * FROM inbox WHERE code=?""", (code,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Нет такой картинки")
        code, name, moment = row
        bucket_name = datetime.now().strftime("%Y%m%d")
        bucket_folder = get_or_create_bucket(bucket_name)
        file_path = bucket_folder / name
        delete_file(file_path)
        cur.execute("""DELETE FROM inbox WHERE code=?""", (code,))

    return {"message": "ok"}


@app.on_event("startup")
def create_db():
    with sqlite3.connect("sqlite.db", check_same_thread=False) as conn:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS inbox (
                code INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                moment DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


@app.on_event("startup")
def create_folder():
    FILE_FOLDER.mkdir(parents=False, exist_ok=True)


if __name__ == '__main__':
    uvicorn.run('main:app', host='127.0.0.1', port=8000, reload=True)




