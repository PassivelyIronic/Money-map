from fastapi import FastAPI, HTTPException, UploadFile

from app.tasks import import_statement

app = FastAPI(title="Money Map API")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/import/{bank}")
async def import_endpoint(bank: str, file: UploadFile) -> dict:
    if bank not in ("millennium", "revolut"):
        raise HTTPException(status_code=400, detail=f"nieobslugiwany bank: {bank}")

    raw_bytes = await file.read()
    task = import_statement.delay(bank, raw_bytes)
    return {"job_id": task.id, "status": "queued"}


@app.get("/import/status/{job_id}")
def import_status(job_id: str) -> dict:
    result = import_statement.AsyncResult(job_id)
    return {"job_id": job_id, "state": result.state, "result": result.result if result.ready() else None}
