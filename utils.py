import yaml
import requests
import pandas as pd

def load_config(path='config.yaml'):
    with open(path) as f:
        for doc in yaml.safe_load_all(f):
            if isinstance(doc, dict):
                return doc
    return {}

cfg = load_config()
api_url = cfg.get('api_base_url')

def fetch_product_limits(product_id: str) -> dict:
    resp = requests.get(f"{api_url}/products/{product_id}")
    prod = resp.json()
    return {
        'min_size': float(prod.get('base_min_size', prod.get('min_size'))),
        'max_size': float(prod.get('base_max_size', prod.get('max_size'))),
        'increment': float(prod.get('base_increment', prod.get('increment'))),
    }

def fetch_ohlcv(product: str, granularity: int = 900) -> pd.DataFrame:
    resp = requests.get(f"{api_url}/products/{product}/candles", params={'granularity': granularity})
    data = resp.json()
    df = pd.DataFrame(data, columns=['time','low','high','open','close','volume'])
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df.set_index('time', inplace=True)
    return df

def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df['ema8'] = df['close'].ewm(span=8).mean()
    df['ema21'] = df['close'].ewm(span=21).mean()
    delta = df['close'].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = -delta.clip(upper=0).rolling(14).mean()
    df['rsi'] = 100 - 100 / (1 + gain / loss)
    tr = pd.concat([
        df['high'] - df['low'],
        (df['high'] - df['close'].shift()).abs(),
        (df['low'] - df['close'].shift()).abs()
    ], axis=1).max(axis=1)
    df['atr'] = tr.rolling(14).mean()
    return df

def calculate_size(balance: float, risk_pct: float, atr: float, price: float, limits: dict) -> float:
    risk_amount = balance * risk_pct
    stop_loss_dist = atr * 0.8
    raw = risk_amount / stop_loss_dist
    size = max(limits['min_size'], min(raw, limits['max_size']))
    inc = limits['increment']
    size = (size // inc) * inc
    return round(size, 8)
