from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np

app = FastAPI()

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

@app.post("/")
async def telemetry_metrics(request: Request):
    body = await request.json()
    regions = body.get("regions", [])
    threshold_ms = body.get("threshold_ms", 180)

    # Load sample telemetry data
    data = pd.read_csv("telemetry.csv")  # Put your telemetry CSV in the repo for testing

    response = {}
    for region in regions:
        region_data = data[data["region"] == region]
        if region_data.empty:
            response[region] = {
                "avg_latency": None,
                "p95_latency": None,
                "avg_uptime": None,
                "breaches": 0
            }
            continue
        latencies = region_data["latency_ms"]
        uptimes = region_data["uptime_percent"]
        response[region] = {
            "avg_latency": round(latencies.mean(), 2),
            "p95_latency": round(np.percentile(latencies, 95), 2),
            "avg_uptime": round(uptimes.mean(), 2),
            "breaches": int((latencies > threshold_ms).sum())
        }
    return response
