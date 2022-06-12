import sqlite3
import uuid
from datetime import datetime
import uvicorn
from fastapi import FastAPI, UploadFile, HTTPException, status
app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post('/frames/') #метод фреймс
async def create_upload_files(files: list[UploadFile]):
    print(len(files)) # проверяет кол-во загруженных файлов
    if len(files) > 15:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Нельзя больше 15 файлов")
    saved_files = []
    for i in files:
        if '.jpg' not in i.filename: # проверяет формат
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Нельзя формат кроме jpg")
        uid = str(uuid.uuid4())
        name = f'{uid}.jpg'
        saved_files.append(name)
    print(saved_files)
    with sqlite3.connect("sqlite.db",check_same_thread = False ) as conn:
        cur = conn.cursor()
        rows = []
        for i in saved_files:
            cur.execute(
                """
                INSERT INTO inbox (code, name) VALUES(?,?)
                """, (None, i)
            )
            rows.append(cur.lastrowid)
    return {n:v for n,v in zip(rows, saved_files)}


@app.get("/frames/")


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



if __name__ == '__main__':
    uvicorn.run('main:app', host='127.0.0.1', port=8000, reload=True)



