
import uvicorn

from src.config.env import settings

from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello World"}

if __name__ == "__main__":
    uvicorn.run("src.app:app", host="0.0.0.0", port=settings.PORT, reload=True)
