import cbpro
import pandas as pd
def fetch_product_limits(product_id: str) -> dict:
    prod = client.get_product(product_id)
    return {
        'min_size': float(prod['base_min_size']),
        'max_size': float(prod['base_max_size']),
        'increment': float(prod['base_increment']),
    }

def fetch_ohlcv(product: str, granularity: int=900) -> pd.DataFrame:
    df = pd.DataFrame(client.get_product_historic_rates(product, granularity=granularity),
                      columns=['time','low','high','open','close','volume'])
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df.set_index('time', inplace=True)
    return df

def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df['ema8'] = df['close'].ewm(span=8).mean()
    df['ema21'] = df['close'].ewm(span=21).mean()
    delta = df['close'].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = -delta.clip(upper=0).rolling(14).mean()
    df['rsi'] = 100 - 100/(1 + gain/loss)
    tr = pd.concat([df['high']-df['low'],
                    (df['high']-df['close'].shift()).abs(),
                    (df['low']-df['close'].shift()).abs()], axis=1).max(axis=1)
    df['atr'] = tr.rolling(14).mean()
    return df

def calculate_size(balance: float, risk_pct: float, atr: float, price: float, limits: dict) -> float:
    risk_amount = balance * risk_pct
    stop_loss_dist = atr * 0.8
    raw_size = risk_amount / stop_loss_dist
    size = max(limits['min_size'], min(raw_size, limits['max_size']))
    increment = limits['increment']
    size = (size // increment) * increment
    return round(size, 8)
