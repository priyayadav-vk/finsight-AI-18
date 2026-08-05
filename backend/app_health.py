from fastapi import FastAPI

app = FastAPI(title="FinSight AI Health")


@app.get("/health")
async def health():
    return {"status": "ok"}
