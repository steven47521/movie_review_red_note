from fastapi import FastAPI

app = FastAPI(title="RedNote Cinema API")


@app.get("/health")
def health():
    return {"status": "ok"}
