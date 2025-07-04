import collections
import collections.abc
collections.Mapping = collections.abc.Mapping
collections.MutableMapping = collections.abc.MutableMapping
collections.Sequence = collections.abc.Sequence
collections.Callable = collections.abc.Callable

import yaml, logging, time, requests
from auth import get_jwt
from prometheus_client import Counter, Gauge, start_http_server
from rl_agent import RLAgent
from onchain_analyzer import OnChainAnalyzer
from utils import fetch_product_limits, fetch_ohlcv, add_indicators, calculate_size

# Load config from first YAML doc
cfg = None
for doc in yaml.safe_load_all(open('config.yaml')):
    if isinstance(doc, dict):
        cfg = doc
        break

api_url = cfg['api_base_url']

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger('short_bot')

start_http_server(cfg['prometheus_port'])
trades_executed = Counter('trades_executed_total', 'Total trades executed')
trades_failed = Counter('trades_failed_total', 'Total trades failed')
open_positions = Gauge('open_positions', 'Open positions')

session = requests.Session()
session.headers.update({'Authorization': f"Bearer {get_jwt()}", 'Content-Type': 'application/json'})

rl_agent = RLAgent(cfg['rl_model_path'])
onchain = OnChainAnalyzer(cfg['onchain_api'])

def run_bot():
    limits = fetch_product_limits(cfg['product_id'])
    while True:
        try:
            df = add_indicators(fetch_ohlcv(cfg['product_id']))
            metrics = onchain.get_metrics(cfg['product_id'].split('-')[0])
            action = rl_agent.select_action(df, metrics)
            if action == 'short':
                bal = float(session.get(f"{api_url}/accounts/USD").json()['available'])
                price = df['close'].iloc[-1]
                atr = df['atr'].iloc[-1]
                size = calculate_size(bal, cfg['risk_pct'], atr, price, limits)
                order = session.post(f"{api_url}/orders", json={'size': size, 'side': 'sell', 'product_id': cfg['product_id'], 'type': 'market'}).json()
                logger.info(f"Executed short: {order}")
                trades_executed.inc()
                open_positions.inc()
        except Exception as e:
            logger.exception(f"Error: {e}")
            trades_failed.inc()
        time.sleep(60)

if __name__ == '__main__':
    logger.info("Starting Coinbase Short Bot...")
    run_bot()
