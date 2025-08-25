from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os
from nsepython import nse_eq, nse_quote, nse_optionchain_scrapper
import yfinance as yf

app = FastAPI(title="NSE Stock API + Web UI", version="1.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.responses import FileResponse
import os

# Serve static files from /static
app.mount("/static", StaticFiles(directory="static"), name="static")

# Root should return index.html
@app.get("/")
def read_root():
    return FileResponse(os.path.join("static", "index.html"))

# ----------------- API ENDPOINTS -----------------
def validate_symbol(symbol: str):
    symbol = symbol.strip().upper()
    if not symbol.isalnum():
        return None
    return symbol

@app.get("/stock/{symbol}/quote")
def get_quote(symbol: str):
    symbol = validate_symbol(symbol)
    if not symbol:
        return {"status": "error", "message": "Invalid symbol!"}
    try:
        data = nse_quote(symbol)
        if not data:
            return {"status": "error", "message": f"Symbol '{symbol}' not found."}
        return {"status": "success", "symbol": symbol, "data": data}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/stock/{symbol}/details")
def get_details(symbol: str):
    symbol = validate_symbol(symbol)
    if not symbol:
        return {"status": "error", "message": "Invalid symbol!"}
    try:
        data = nse_eq(symbol)
        if not data:
            return {"status": "error", "message": f"Symbol '{symbol}' not found."}
        return {"status": "success", "symbol": symbol, "data": data}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/stock/{symbol}/options")
def get_options(symbol: str):
    symbol = validate_symbol(symbol)
    if not symbol:
        return {"status": "error", "message": "Invalid symbol!"}
    try:
        data = nse_optionchain_scrapper(symbol)
        if not data:
            return {"status": "error", "message": f"Option chain for '{symbol}' not found."}
        return {"status": "success", "symbol": symbol, "data": data}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/stock/{symbol}/history")
def get_history(symbol: str, period: str = "1mo", interval: str = "1d"):
    symbol = validate_symbol(symbol)
    if not symbol:
        return {"status": "error", "message": "Invalid symbol!"}
    try:
        ticker = yf.Ticker(f"{symbol}.NS")
        hist = ticker.history(period=period, interval=interval)
        if hist.empty:
            return {"status": "error", "message": f"Historical data for '{symbol}' not found."}
        return {
            "status": "success",
            "symbol": symbol,
            "period": period,
            "interval": interval,
            "history": hist.reset_index().to_dict(orient="records")
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
