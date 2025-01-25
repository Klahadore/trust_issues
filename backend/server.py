from typing import Union

from fastapi import FastAPI

app = FastAPI()

@app.get("/check_root_url/{root_url}")
def check_root_url(root_url: str):
    pass

@app.get("/get_warning/{root_url}")
def get_warning(root_url: str):
    pass
