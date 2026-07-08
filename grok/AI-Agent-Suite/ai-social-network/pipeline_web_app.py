from fastapi import FastAPI
from app.pipeline_api import router as pipeline_router

app = FastAPI(title="Super_LH Model3 Control Room")
app.include_router(pipeline_router)

@app.get('/health')
def health():
    return {'ok': True, 'service': 'pipeline_web'}
