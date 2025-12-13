from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.database import Base, engine
from app.routes import router
from app.cli import cli

Base.metadata.create_all(bind=engine)

app = FastAPI(title="CP Mentor API")

app.include_router(router)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def serve_home():
    return FileResponse("static/home.html")

@app.get("/problem")
def serve_problem():
    return FileResponse("static/problem.html")

if __name__ == "__main__":
    cli()
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
