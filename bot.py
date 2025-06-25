import yaml
import os
import cbpro
import logging
import time
from prometheus_client import Counter, Gauge, start_http_server
from rl_agent import RLAgent
from onchain_analyzer import OnChainAnalyzer
from utils import fetch_product_limits, fetch_ohlcv, add_indicators, calculate_size

# Load config
with open('config.yaml', 'r') as f:
    cfg = yaml.safe_load(f)

# Override with env vars
api_key = os.getenv('CB_API_KEY', cfg['api_key'])
api_secret = os.getenv('CB_API_SECRET', cfg['api_secret'])
passphrase = os.getenv('CB_PASSPHRASE', cfg['passphrase'])
use_sandbox = cfg.get('use_sandbox', False)
base_url = cfg.get('api_base_url') if use_sandbox else 'https://api.pro.coinbase.com'

# Logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s',
                    handlers=[logging.FileHandler('bot.log'), logging.StreamHandler()])
logger = logging.getLogger('short_bot')

# Prometheus metrics
start_http_server(cfg['prometheus_port'])
trades_executed = Counter('trades_executed_total', 'Total trades executed')
trades_failed = Counter('trades_failed_total', 'Total trades failed')
current_pnl = Gauge('current_pnl', 'Current profit and loss')
open_positions = Gauge('open_positions', 'Number of open positions')

# Clients and modules
client = cbpro.AuthenticatedClient(api_key, api_secret, passphrase, api_url=base_url)
rl_agent = RLAgent(cfg['rl_model_path'])
onchain = OnChainAnalyzer(cfg['onchain_api'])

def run_bot():
    limits = fetch_product_limits(cfg['product_id'])
    while True:
        try:
            df = add_indicators(fetch_ohlcv(cfg['product_id']))
            metrics = onchain.get_metrics(cfg['product_id'].split('-')[0])
            state = rl_agent._construct_state(df, metrics)

            action = rl_agent.select_action(state)
            if action == 'short':
                balance = float(client.get_account('USD')['available'])
                price = df['close'].iloc[-1]
                atr = df['atr'].iloc[-1]
                size = calculate_size(balance, cfg['risk_pct'], atr, price, limits)

                order = client.sell(size=size, order_type='market', product_id=cfg['product_id'])
                logger.info(f"Executed short: size={size} price={price}")
                trades_executed.inc()
                open_positions.inc()
            else:
                logger.debug("No trade signal")

        except Exception as e:
            logger.exception(f"Error in main loop: {e}")
            trades_failed.inc()

        time.sleep(60)

if __name__ == '__main__':
    logger.info("Starting Coinbase Short Bot...")
    run_bot()
