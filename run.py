import configparser

from fastapi import FastAPI

from net import WSConn

import uvicorn

app = FastAPI()

app.include_router(WSConn.router)

if __name__ == "__main__":
    uvicorn.run('run:app', host='0.0.0.0', port=9996, reload=True)
