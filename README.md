# Coinbase Short Bot

Automatyczny bot shortujący na Coinbase Pro z wykorzystaniem:
- Technicznych wskaźników (EMA, RSI, ATR)
- Reinforcement Learning (moduł `RLAgent`)
- Analizy on-chain (`OnChainAnalyzer`)
- Monitoringu metryk w Prometheus/Grafana

## Instalacja
```bash
git clone https://github.com/<YOUR_GITHUB_USERNAME>/coinbase-short-bot.git
cd coinbase-short-bot
python3 -m venv venv
source venv/bin/activate  # lub `.\venv\Scripts\Activate.ps1` na Windows
pip install -r requirements.txt
```

## Konfiguracja
- Skopiuj `config.yaml.example` do `config.yaml` i uzupełnij klucze API oraz ścieżki.

## Uruchomienie
```bash
python bot.py
```

## Monitoring
- Prometheus na `http://localhost:8000/metrics`
- Grafana z załadowanym dashboardem z `/monitoring/grafana_dashboard.json`
