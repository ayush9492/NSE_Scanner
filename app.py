"""
Stock Scanner API — RS New High + Buy Signal Scanner
FastAPI backend that runs scans and serves results via REST API.
"""

from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yfinance as yf
import talib
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os
import threading
import time

app = FastAPI(title="Stock Scanner API")

# Allow all origins for development — restrict in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── CONFIG ───────────────────────────────────────────────────────────────────

INDEX_SYMBOL = "^NSEI"

STOCK_LIST = [
    "CAMS.NS", "CONCOR.NS", "CROMPTON.NS", "CUMMINSIND.NS", "CYIENT.NS",
    "DLF.NS", "DABUR.NS", "DALBHARAT.NS", "DEEPAKNTR.NS", "DELHIVERY.NS",
    "DIVISLAB.NS", "DIXON.NS", "DRREDDY.NS", "ETERNAL.NS", "EICHERMOT.NS",
    "ESCORTS.NS", "EXIDEIND.NS", "NYKAA.NS", "GAIL.NS", "GMRAIRPORT.NS",
    "GLENMARK.NS", "GODREJCP.NS", "GODREJPROP.NS", "GRANULES.NS", "GRASIM.NS",
    "HCLTECH.NS", "HDFCAMC.NS", "HDFCBANK.NS", "HDFCLIFE.NS", "HFCL.NS",
    "HAVELLS.NS", "HEROMOTOCO.NS", "HINDALCO.NS", "HAL.NS", "HINDCOPPER.NS",
    "HINDPETRO.NS", "HINDUNILVR.NS", "HINDZINC.NS", "HUDCO.NS", "ICICIBANK.NS",
    "ICICIGI.NS", "ICICIPRULI.NS", "IDFCFIRSTB.NS", "IIFL.NS", "IRB.NS",
    "ITC.NS", "INDIANB.NS", "IEX.NS", "IOC.NS", "IRCTC.NS",
    "IRFC.NS", "IREDA.NS", "IGL.NS", "INDUSTOWER.NS", "INDUSINDBK.NS",
    "NAUKRI.NS", "INFY.NS", "INOXWIND.NS", "INDIGO.NS", "JSWENERGY.NS",
    "JSWSTEEL.NS", "JSL.NS", "JINDALSTEL.NS", "JIOFIN.NS", "JUBLFOOD.NS",
    "KEI.NS", "KPITTECH.NS", "KALYANKJIL.NS", "KOTAKBANK.NS", "LTF.NS",
    "LICHSGFIN.NS", "LTIM.NS", "LT.NS", "LAURUSLABS.NS", "LICI.NS",
    "LUPIN.NS", "MRF.NS", "LODHA.NS", "MGL.NS", "M&MFIN.NS",
    "M&M.NS", "MANAPPURAM.NS", "MARICO.NS", "MARUTI.NS", "MFSL.NS",
    "MAXHEALTH.NS", "MPHASIS.NS", "MCX.NS", "MUTHOOTFIN.NS", "NBCC.NS",
    "NCC.NS", "NHPC.NS", "NMDC.NS", "NTPC.NS", "NATIONALUM.NS",
    "NESTLEIND.NS", "OBEROIRLTY.NS", "ONGC.NS", "OIL.NS", "PAYTM.NS",
    "OFSS.NS", "POLICYBZR.NS", "PIIND.NS", "PNBHOUSING.NS", "PAGEIND.NS",
    "PATANJALI.NS", "PERSISTENT.NS", "PETRONET.NS", "PIDILITIND.NS", "PEL.NS",
    "POLYCAB.NS", "POONAWALLA.NS", "PFC.NS", "POWERGRID.NS", "PRESTIGE.NS",
    "PNB.NS", "RBLBANK.NS", "RECLTD.NS", "RELIANCE.NS", "SBICARD.NS",
    "SBILIFE.NS", "SHREECEM.NS", "SJVN.NS", "SRF.NS", "MOTHERSON.NS",
    "SHRIRAMFIN.NS", "SIEMENS.NS", "SOLARINDS.NS", "SONACOMS.NS", "SBIN.NS",
    "SAIL.NS", "SUNPHARMA.NS", "SUPREMEIND.NS", "SYNGENE.NS", "TATACONSUM.NS",
    "TITAGARH.NS", "TVSMOTOR.NS", "TATACHEM.NS", "TATACOMM.NS", "TCS.NS",
    "TATAELXSI.NS", "TATAMOTORS.NS", "TATAPOWER.NS", "TATASTEEL.NS", "TATATECH.NS",
    "TECHM.NS", "FEDERALBNK.NS", "INDHOTEL.NS", "PHOENIXLTD.NS", "RAMCOCEM.NS",
    "TITAN.NS", "TORNTPHARM.NS", "TORNTPOWER.NS", "TRENT.NS", "TIINDIA.NS",
    "UPL.NS", "ULTRACEMCO.NS", "UNIONBANK.NS", "UNITDSPR.NS", "VBL.NS",
    "VEDL.NS", "IDEA.NS", "VOLTAS.NS", "WIPRO.NS", "YESBANK.NS", "ZYDUSLIFE.NS",
    "BIOCON.NS", "APOLLOHOSP.NS", "AUBANK.NS", "BAJAJ-AUTO.NS", "BALKRISIND.NS",
    "BOSCHLTD.NS", "BRITANNIA.NS", "BHARTIARTL.NS", "APOLLOTYRE.NS", "AXISBANK.NS",
    "ASIANPAINT.NS", "CHAMBLFERT.NS", "BEL.NS", "BAJAJFINSV.NS", "COLPAL.NS",
    "CIPLA.NS", "ACC.NS", "BSE.NS", "ALKEM.NS", "ASHOKLEY.NS",
    "BANDHANBNK.NS", "CESC.NS", "COALINDIA.NS", "APLAPOLLO.NS", "DMART.NS",
    "CGPOWER.NS", "ABCAPITAL.NS", "ADANIENT.NS", "BHARATFORG.NS", "ABFRL.NS",
    "AMBUJACEM.NS", "BPCL.NS", "BAJFINANCE.NS", "CDSL.NS", "AUROPHARMA.NS",
    "ANGELONE.NS", "ABB.NS", "AARTIIND.NS", "BHEL.NS",
    "ADANIPORTS.NS", "ASTRAL.NS", "BSOFT.NS", "BANKBARODA.NS", "COFORGE.NS",
    "CHOLAFIN.NS", "ADANIGREEN.NS", "CANBK.NS", "ATGL.NS", "BANKINDIA.NS",
    "AMBER.NS",
]

# Remove duplicates
STOCK_LIST = list(set(STOCK_LIST))

# ─── GLOBAL STATE ─────────────────────────────────────────────────────────────

scan_state = {
    "status": "idle",          # idle | scanning | complete | error
    "progress": 0,             # 0-100
    "current_stock": "",
    "rs_highs": [],
    "buy_signals": [],
    "final_stocks": [],
    "stock_details": {},       # symbol -> {price, change, rs_value, etc.}
    "last_scan_time": None,
    "error": None,
    "total_stocks": len(STOCK_LIST),
    "scanned_count": 0,
}

scan_lock = threading.Lock()

# ─── HELPERS ──────────────────────────────────────────────────────────────────

def safe_array(arr):
    return np.asarray(arr, dtype=np.float64)


def get_stock_details(symbol, stock_data, index_data):
    """Get extra details for display."""
    try:
        close = stock_data['Close']
        latest_price = float(close.iloc[-1])
        prev_price = float(close.iloc[-2]) if len(close) > 1 else latest_price
        change_pct = ((latest_price - prev_price) / prev_price) * 100

        volume = float(stock_data['Volume'].iloc[-1])
        avg_volume = float(stock_data['Volume'].rolling(20).mean().iloc[-1])

        # Compute RS line value
        common = stock_data.index.intersection(index_data.index)
        if len(common) > 0:
            rs_val = float((stock_data['Close'].loc[common].iloc[-1] * 7000) / index_data['Close'].loc[common].iloc[-1])
        else:
            rs_val = 0

        return {
            "symbol": symbol.replace(".NS", ""),
            "price": round(latest_price, 2),
            "change_pct": round(change_pct, 2),
            "volume": int(volume),
            "avg_volume": int(avg_volume),
            "volume_ratio": round(volume / avg_volume, 2) if avg_volume > 0 else 0,
            "rs_value": round(rs_val, 2),
        }
    except Exception:
        return {
            "symbol": symbol.replace(".NS", ""),
            "price": 0, "change_pct": 0, "volume": 0,
            "avg_volume": 0, "volume_ratio": 0, "rs_value": 0,
        }


# ─── SCANNER LOGIC ────────────────────────────────────────────────────────────

def run_full_scan():
    global scan_state

    with scan_lock:
        scan_state["status"] = "scanning"
        scan_state["progress"] = 0
        scan_state["scanned_count"] = 0
        scan_state["rs_highs"] = []
        scan_state["buy_signals"] = []
        scan_state["final_stocks"] = []
        scan_state["stock_details"] = {}
        scan_state["error"] = None

    try:
        # Fetch index data once
        index_ticker = yf.Ticker(INDEX_SYMBOL)
        index_data_1y = index_ticker.history(period="1y")
        index_data_6mo = index_ticker.history(period="6mo")

        rs_highs = []
        buy_signals = []
        all_details = {}
        total = len(STOCK_LIST)

        for i, symbol in enumerate(STOCK_LIST):
            with scan_lock:
                scan_state["current_stock"] = symbol.replace(".NS", "")
                scan_state["scanned_count"] = i + 1
                scan_state["progress"] = int(((i + 1) / total) * 100)

            try:
                stock = yf.Ticker(symbol)
                data_1y = stock.history(period="1y")
                data_6mo = stock.history(period="6mo")

                # ── RS NEW HIGH CHECK ──
                try:
                    close_1y = data_1y['Close']
                    idx_close_1y = index_data_1y['Close']
                    common = close_1y.index.intersection(idx_close_1y.index)
                    if len(common) >= 50:
                        sc = close_1y.loc[common]
                        ic = idx_close_1y.loc[common]
                        rs = (sc * 7 * 1000) / ic
                        rs_high = rs.rolling(window=123, min_periods=1).max()
                        if rs.iloc[-1] > rs_high.shift(1).iloc[-1]:
                            rs_highs.append(symbol)
                except Exception:
                    pass

                # ── BUY SIGNAL CHECK ──
                try:
                    common_6 = data_6mo.index.intersection(index_data_6mo.index)
                    df = data_6mo.loc[common_6].copy()
                    if len(df) < 60:
                        raise ValueError("Not enough data")

                    high = safe_array(df['High'])
                    low = safe_array(df['Low'])
                    close = safe_array(df['Close'])
                    volume = safe_array(df['Volume'])

                    plus_di = talib.PLUS_DI(high, low, close, timeperiod=5)
                    minus_di = talib.MINUS_DI(high, low, close, timeperiod=5)
                    ema10 = talib.EMA(close, timeperiod=10)
                    ema20 = talib.EMA(close, timeperiod=20)
                    ema50 = talib.EMA(close, timeperiod=50)
                    sma50 = talib.SMA(close, timeperiod=50)
                    vol_sma20 = talib.SMA(volume, timeperiod=20)

                    # SMA trending up (5 consecutive higher values)
                    sma_trend = (
                        not np.isnan(sma50[-1]) and len(sma50) >= 5
                        and sma50[-1] > sma50[-2] > sma50[-3] > sma50[-4] > sma50[-5]
                    )

                    # Weekly RSI
                    weekly = stock.history(period="2y", interval="1wk")
                    weekly_rsi = talib.RSI(safe_array(weekly['Close']), timeperiod=14)
                    last_weekly_rsi = float(weekly_rsi[-1]) if len(weekly_rsi) > 0 else 0

                    # DI difference
                    di_diff = float(plus_di[-1] - plus_di[-2]) if len(plus_di) >= 2 else 0

                    # Volume value
                    vol_value = float(close[-1]) * float(volume[-1])

                    cond1 = di_diff >= 10
                    cond2 = vol_value > 50_000_000
                    cond3 = float(ema10[-1]) > float(ema20[-1]) > float(ema50[-1])
                    cond4 = last_weekly_rsi >= 59
                    cond5 = sma_trend
                    cond6 = float(volume[-1]) > float(vol_sma20[-1]) if not np.isnan(vol_sma20[-1]) else False

                    if all([cond1, cond2, cond3, cond4, cond5, cond6]):
                        buy_signals.append(symbol)
                except Exception:
                    pass

                # ── STOCK DETAILS ──
                details = get_stock_details(symbol, data_1y, index_data_1y)
                all_details[symbol] = details

            except Exception as e:
                print(f"Error scanning {symbol}: {e}")
                continue

            # Small delay to avoid rate limiting
            time.sleep(0.1)

        final = list(set(rs_highs) & set(buy_signals))

        with scan_lock:
            scan_state["rs_highs"] = [s.replace(".NS", "") for s in rs_highs]
            scan_state["buy_signals"] = [s.replace(".NS", "") for s in buy_signals]
            scan_state["final_stocks"] = [s.replace(".NS", "") for s in final]
            scan_state["stock_details"] = all_details
            scan_state["last_scan_time"] = datetime.now().isoformat()
            scan_state["status"] = "complete"
            scan_state["progress"] = 100

    except Exception as e:
        with scan_lock:
            scan_state["status"] = "error"
            scan_state["error"] = str(e)


# ─── API ROUTES ───────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"message": "Stock Scanner API is running"}


@app.post("/scan")
def start_scan(background_tasks: BackgroundTasks):
    """Kick off a background scan."""
    if scan_state["status"] == "scanning":
        return {"message": "Scan already in progress", "status": scan_state["status"]}
    background_tasks.add_task(run_full_scan)
    return {"message": "Scan started", "status": "scanning"}


@app.get("/status")
def get_status():
    """Get current scan progress."""
    with scan_lock:
        return {
            "status": scan_state["status"],
            "progress": scan_state["progress"],
            "current_stock": scan_state["current_stock"],
            "scanned_count": scan_state["scanned_count"],
            "total_stocks": scan_state["total_stocks"],
        }


@app.get("/results")
def get_results():
    """Get scan results."""
    with scan_lock:
        return {
            "status": scan_state["status"],
            "rs_highs": scan_state["rs_highs"],
            "buy_signals": scan_state["buy_signals"],
            "final_stocks": scan_state["final_stocks"],
            "stock_details": scan_state["stock_details"],
            "last_scan_time": scan_state["last_scan_time"],
            "total_rs": len(scan_state["rs_highs"]),
            "total_buy": len(scan_state["buy_signals"]),
            "total_final": len(scan_state["final_stocks"]),
        }


@app.get("/stock/{symbol}")
def get_stock_chart(symbol: str):
    """Get detailed chart data for a single stock."""
    try:
        ticker = yf.Ticker(f"{symbol}.NS")
        df = ticker.history(period="1y")
        index_df = yf.Ticker(INDEX_SYMBOL).history(period="1y")

        common = df.index.intersection(index_df.index)
        rs_line = ((df['Close'].loc[common] * 7000) / index_df['Close'].loc[common]).tolist()

        return {
            "symbol": symbol,
            "dates": [d.strftime("%Y-%m-%d") for d in df.index],
            "close": df['Close'].tolist(),
            "high": df['High'].tolist(),
            "low": df['Low'].tolist(),
            "open": df['Open'].tolist(),
            "volume": df['Volume'].tolist(),
            "rs_dates": [d.strftime("%Y-%m-%d") for d in common],
            "rs_line": rs_line,
        }
    except Exception as e:
        return {"error": str(e)}


# ─── SERVE FRONTEND ───────────────────────────────────────────────────────────
from fastapi.responses import FileResponse

@app.get("/app", response_class=FileResponse)
def serve_frontend():
    """Serve the frontend UI."""
    for path in ["index.html", "static/index.html", "../frontend/index.html"]:
        if os.path.exists(path):
            return FileResponse(path)
    return {"error": "Frontend not found"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)