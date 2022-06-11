import uvicorn
from fastapi import FastAPI, UploadFile, HTTPException, status
app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post('/frames/')
async def create_upload_files(files: list[UploadFile]):
    print(len(files))
    if len(files) > 15:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Нельзя больше 15 файлов")
    for i in files:
        if '.jpg' not in i.filename:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Нельзя формат кроме jpg")
    return {"filenames": [file.filename for file in files]}



if __name__ == '__main__':
    uvicorn.run('main:app', host='127.0.0.1', port=8000, reload=True)