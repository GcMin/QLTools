import uvicorn
from fastapi import FastAPI
from tools import app

r = FastAPI()
r.include_router(app, prefix='/JD', tags=['京东应用'])

if __name__ == '__main__':
    uvicorn.run('run:r', host='0.0.0.0', port=8000, reload=True)
