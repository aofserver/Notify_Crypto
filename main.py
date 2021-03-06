#ref : https://stackpython.co/tutorial/api-python-fastapi
#doc : http://127.0.0.1:8000/docs#/
#run_dev : uvicorn main:app --reload
#run_production : python main.py

import uvicorn
from fastapi import FastAPI, Request, File, UploadFile, Form
from pydantic import BaseModel
from routers import notify, analysis
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates





# app = FastAPI(docs_url="/documentation", redoc_url=None)
app = FastAPI(docs_url="/docs")


# origins = [
#     "http://localhost:8080",
#     "http://localhost:3000",
#     "https://stackpython.co"
# ]

server = 'http://localhost:8000'
origins = ['*']


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# router api
app.include_router(notify.router)
app.include_router(analysis.router)


static_path = "static"
templates = Jinja2Templates(directory="templates")


@app.get("/")
async def root():
    return {"message": "Hello World"}

# @app.get("/", response_class=HTMLResponse)
# async def read_item(request: Request):
#     return templates.TemplateResponse("index.html", {"request": request})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
    