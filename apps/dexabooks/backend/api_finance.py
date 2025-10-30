DexaBooks Financial API
A thin viewer API that proxies requests to Core API for financial data
"""

import os
import httpx
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import csv
import io
from datetime import datetime, timedelta

app = FastAPI(
    title="DexaBooks API",
    version="1.0.0",
    description="Financial dashboard viewer for Core Semantic OS"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Core API configuration
CORE_API_URL = os.getenv("CORE_API_URL", "http://localhost:8001")

# Pydantic models
class TransactionCreate(BaseModel):
    amount: float
    date: str
    description: str
    transaction_type: str
    category: Optional[str] = None
    vendor: Optional[str] = None
    is_recurring: Optional[bool] = False
    recurrence_pattern: Optional[str] = None

class ForecastCreate(BaseModel):
    predicted_amount: float
    predicted_date: str
    predicted_description: str
    confidence: float
    forecast_method: str