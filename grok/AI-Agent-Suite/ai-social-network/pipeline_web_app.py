from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from app.pipeline_api import router as pipeline_router

app = FastAPI(title="Super_LH Model3 Control Room")

# Public Model3 API is consumed from Firebase Hosting domains (lhinvest.web.app,
# legacy lhinvt/lhivt aliases). It does not use cookies, so wildcard CORS is
# safe here and avoids new hosting aliases breaking the stock-report page.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


@app.middleware("http")
async def force_public_cors(request: Request, call_next):
    if request.method == "OPTIONS":
        response = Response(status_code=204)
    else:
        response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,HEAD,OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = request.headers.get(
        "access-control-request-headers", "*"
    )
    response.headers["Access-Control-Max-Age"] = "600"
    return response


app.include_router(pipeline_router)


@app.get('/health')
def health():
    return {'ok': True, 'service': 'pipeline_web'}
