# Crypto Sector Rotation Project

## Overview

Cryptocurrency market sector rotation analysis system using Three-Layer Framework:
- **Layer 1**: Category Cohesion (Fiedler eigenvalue analysis)
- **Layer 2**: Market Regime Detection (Bull/Bear/Neutral)
- **Layer 3**: Momentum Signals (from CoinGecko/regime data)

**Key Stats**: 228 CoinGecko categories, 1,559 tokens, 10 meta-sectors

**Dashboard Port**: 8003 (local)

---

## Category Classification System

### Total: 228 CoinGecko Categories + 4 Level 2 Categories

| Meta-Sector | Categories | Example Tokens |
|-------------|------------|----------------|
| AI | 7 | FET, RENDER, NEAR, ICP, VIRTUAL |
| DeFi | 10 | AAVE, UNI, MKR, COMP, CRV, SNX |
| Infrastructure | 10 | LINK, FIL, AR, GRT, RNDR |
| Gaming | 5 | GALA, SAND, MANA, AXS, ENJ |
| Privacy | 3 | XMR, ZEC, DASH, ZEN, MINA |
| Memes | 9 | DOGE, SHIB, BONK, FLOKI, WIF, PEPE |
| RWA | 5 | PAXG, XAUT, ONDO |
| Stablecoins | 5 | USDT, USDC, DAI |
| Ecosystem | 17+ | SOL, ETH, BNB, AVAX, MATIC |
| VC Portfolio | 8+ | a16z, Coinbase, Paradigm picks |

### Level 2 Categories (from historical analysis)

| Category | Tokens | Latest Fiedler | TIER |
|----------|--------|----------------|------|
| Infrastructure | 335 | 10.58 | TIER 1 |
| Entertainment | 91 | 4.79 | TIER 2 |
| DeFi | 223 | Variable | TIER 3 |
| CeFi | 52 | 1.59 | TIER 3 |

---

## TIER Classification (Fiedler-Based)

| Tier | Action | Fiedler | Description |
|------|--------|---------|-------------|
| **Tier 1** | BUY | ≥ 7.5 | Strong cohesion, sector rotation active |
| **Tier 2** | ACCUMULATE | 3.0-7.5 | Moderate cohesion, building strength |
| **Tier 3** | RESEARCH | 1.0-3.0 | Weak cohesion, individual selection |
| **Tier 4** | MONITOR | < 1.0 | No cohesion, avoid sector plays |

### Combined Score Classification (Alternative)

| Tier | Action | Score | Formula |
|------|--------|-------|---------|
| **Tier 1** | BUY | ≥ 0.20 | momentum × fiedler_norm × trend |
| **Tier 2** | ACCUMULATE | 0.10-0.20 | |
| **Tier 3** | RESEARCH | 0.05-0.10 | |
| **Tier 4** | MONITOR | < 0.05 | |

---

## Top Categories by Performance (Nov 2025)

### By Combined Score
| Rank | Category | Score | Momentum | Fiedler |
|------|----------|-------|----------|---------|
| 1 | ledgerprime_portfolio | 1.049 | -8.70% | 113.60 |
| 2 | zero_knowledge_proofs | 0.856 | -16.28% | 101.85 |
| 3 | fenbushi_capital_portfolio | 0.838 | -18.45% | 102.24 |
| 4 | masternodes | 0.565 | +4.54% | 51.93 |
| 5 | privacy | 0.503 | +6.66% | 43.64 |

### By Momentum
| Rank | Category | Momentum | Fiedler |
|------|----------|----------|---------|
| 1 | x402_ecosystem | +9.60% | 20.17 |
| 2 | privacy | +6.66% | 43.64 |
| 3 | masternodes | +4.54% | 51.93 |
| 4 | usd_stablecoin | -0.05% | 0.02 |
| 5 | tokenized_gold | -0.45% | 4.00 |

---

## Project Structure

```
Sector-Rotation-Crypto/
├── dashboard/
│   ├── backend/                    # FastAPI server
│   │   ├── main.py                 # Entry point (port 8003)
│   │   └── routers/
│   │       ├── sector_rotation.py  # Overview, category health APIs
│   │       ├── breakout.py         # Momentum breakout APIs
│   │       ├── network.py          # Network graph APIs
│   │       └── signals.py          # Signal matrix APIs
│   └── frontend/
│       ├── index.html              # Main dashboard
│       ├── breakout.html           # Momentum scanner
│       ├── signals.html            # Signal quality matrix
│       ├── cohesion.html           # Cohesion visualization
│       └── network.html            # Interactive network graph
├── data/
│   ├── crypto_category_summary.csv
│   ├── crypto_category_tickers_mapping.json
│   ├── monthly_fiedler_crypto_*.csv
│   ├── combined_score_ranking_*.csv
│   ├── momentum_only_ranking_*.csv
│   └── tier*_*.csv
├── docs/
│   ├── CRYPTO_CATEGORY_RANKINGS_TODAY.md
│   └── INVESTMENT_RECOMMENDATIONS_*.md
├── analysis/                       # Analysis reports
├── reports/                        # Generated investment memos
├── scripts/                        # Utility scripts
├── theme_ticker_master.csv         # Category-ticker mapping (1,559 rows)
├── config.py                       # Configuration
├── requirements.txt                # Python dependencies
├── railway.json                    # Railway deployment config
├── Procfile                        # Process file for deployment
└── CLAUDE.md                       # This file
```

---

## Data Sources

| Data Type | Location | Update |
|-----------|----------|--------|
| Category Rankings | `./Sector-Leaders-Crypto/results/` | Weekly |
| Category-Ticker Map | `./theme_ticker_master.csv` | As needed |
| Historical Fiedler | `./data/monthly_fiedler_crypto_*.csv` | Monthly |
| Regime Data | `/mnt/nas/AutoGluon/AutoML_Crypto/regime/` | Daily |

---

## Quick Commands

### Start Dashboard (Local)
```bash
cd /mnt/nas/WWAI/Sector-Rotation/Sector-Rotation-Crypto/dashboard/backend
uvicorn main:app --host 0.0.0.0 --port 8003 --reload
```

### Access Dashboard
- Local: http://localhost:8003/

### Weekly Analysis
```bash
# Run full weekly analysis
./run_weekly_analysis.sh

# Generate actionable tickers
python generate_actionable_tickers.py

# Generate investment reports
python generate_investment_report.py
```

---

## Category Deep Dive

### AI & Big Data (7 categories)
| Category | Description | Top Tokens |
|----------|-------------|------------|
| ai_&_big_data | General AI/ML | FET, RENDER, NEAR, ICP |
| ai_agents | Autonomous agents | VIRTUAL, AI16Z |
| ai_applications | AI apps | TAO, OLAS |
| generative_ai | Gen AI | - |
| defai | DeFi + AI | - |

### DeFi (10+ categories)
| Category | Description | Top Tokens |
|----------|-------------|------------|
| defi | General DeFi | AAVE, UNI, MKR |
| amm | AMM protocols | UNI, SUSHI, CRV |
| derivatives | Derivatives | GMX, DYDX, SNX |
| yield_farming | Yield farms | YFI, COMP |
| liquid_staking | LSDs | LDO, RPL, SFRAX |

### Gaming & Metaverse (5 categories)
| Category | Description | Top Tokens |
|----------|-------------|------------|
| gaming | Gaming tokens | GALA, SAND, MANA |
| metaverse | Virtual worlds | SAND, MANA, OVR |
| play_to_earn | P2E games | AXS, ALICE |
| gaming_guild | Guilds | YGG |

### Privacy (3 categories)
| Category | Description | Top Tokens |
|----------|-------------|------------|
| privacy | Privacy coins | XMR, ZEC, DASH |
| zero_knowledge_proofs | ZK tech | MATIC, MINA, IMX |
| cybersecurity | Security | - |

### Memes (9 categories)
| Category | Description | Top Tokens |
|----------|-------------|------------|
| memes | General memes | DOGE, SHIB, PEPE |
| animal_memes | Animal themed | DOGE, SHIB, BONK |
| ai_memes | AI memes | TURBO |
| political_memes | Political | TRUMP, MAGA |

### Ecosystem (17+ categories)
| Ecosystem | Top Tokens | Notes |
|-----------|------------|-------|
| solana_ecosystem | SOL, JUP, RAY, BONK | High activity |
| ethereum_ecosystem | ETH, AAVE, UNI | Largest |
| bnb_chain_ecosystem | BNB, CAKE | Binance |
| bitcoin_ecosystem | BTC, ORDI, RUNES | BRC-20 |
| base_ecosystem | BASE tokens | Coinbase L2 |
| arbitrum_ecosystem | ARB, GMX | Leading L2 |

---

## Investment Framework

### Actionable Categories (Oct 2025)

**TIER 1 - BUY**
- Infrastructure (Fiedler 10.58): PAXG, ZEC, DASH, ZEN, MKR, SNX

**TIER 2 - ACCUMULATE**
- Entertainment (Fiedler 4.79): AXS, SAND, MANA, ENJ

### Position Sizing by Regime

| Regime | LONG Prob | Position Size |
|--------|-----------|---------------|
| Strong LONG | ≥ 0.80 | 3-5% per token |
| LONG | 0.50-0.79 | 2-3% per token |
| NEUTRAL | 0.40-0.49 | 1-2% per token |
| SHORT | < 0.40 | 0% (avoid) |

### Portfolio Allocation

```
Total Crypto Allocation: 100%
├── 50-60% → TIER 1 Categories (Infrastructure)
├── 20-30% → TIER 2 Categories (Entertainment)
├── 10-20% → TIER 3 (Selective)
└── 10-20% → Cash/Stablecoins
```

---

## Crypto-Specific Considerations

### Market Characteristics
- **24/7 Trading**: No market close, continuous price discovery
- **High Volatility**: 65-92% typical, adjust correlation thresholds
- **Correlation Regimes**: Strong bull/bear correlation patterns
- **BTC Dominance**: Market leader affects all sectors

### Framework Adaptations
- **Higher Correlation Threshold**: 0.30 (vs 0.25 for equities)
- **Longer Lookback**: 60 days (vs 30 for equities)
- **Fiedler Thresholds**: 7.5/3.0/1.0 (adapted for crypto)
- **Disconnection Tolerance**: Crypto sectors disconnect more frequently

### Risk Factors
- **Regulatory Risk**: SEC/CFTC actions
- **Exchange Risk**: Delisting, counterparty risk
- **Smart Contract Risk**: DeFi protocol vulnerabilities
- **Liquidity Risk**: Low-cap tokens

---

## Differences from Other Markets

| Aspect | Crypto | USA | KRX | Japan |
|--------|--------|-----|-----|-------|
| Categories | 228 CoinGecko | 38 ETF themes | 266 Naver | 11 Yahoo |
| Ticker Format | `BTC-USD` | `AAPL` | `005930.KS` | `7203.T` |
| Fiedler Thresholds | 7.5/3.0/1.0 | 3.0/1.5/0.5 | 50/20/5 | 50/20/5 |
| Currency | USD | USD | KRW | JPY |
| Trading Hours | 24/7 | 9:30-16:00 ET | 9:00-15:30 KST | 9:00-15:00 JST |
| Dashboard Port | 8003 | 8001 | 8000 | 8002 |

---

## Global Dashboard Network

| Market | URL | Port | Status |
|--------|-----|------|--------|
| USA | Railway | 8001 | Live |
| KRX | Railway | 8000 | Live |
| Japan | Local | 8002 | WIP |
| China | Local | 8004 | WIP |
| India | Local | 8005 | WIP |
| Hong Kong | Railway | 8006 | Live |
| **Crypto** | Local | 8003 | **Setup** |

---

## Related Projects

| Project | Path | Description |
|---------|------|-------------|
| Sector-Leaders-Crypto | `../Sector-Leaders-Crypto/` | Category rankings |
| Old Crypto Analysis | `../Sector-Rotation-Crypto-2026-02-01/` | Historical data |
| AutoML Crypto | `/mnt/nas/AutoGluon/AutoML_Crypto/` | Regime data |

---

## Recent Analysis (Nov 2025)

### Top Performers
1. **ledgerprime_portfolio** - Score 1.049, Trend 113.60
2. **zero_knowledge_proofs** - Score 0.856, Trend 101.85
3. **privacy** - Score 0.503, Momentum +6.66%

### Momentum Leaders
1. **x402_ecosystem** - +9.60%
2. **privacy** - +6.66%
3. **masternodes** - +4.54%

### Category Distribution
- **Tier 1 (Core)**: 9 categories
- **Tier 2 (Rotational)**: 5 categories
- **Tier 3 (Research)**: 7 categories
- **Tier 4 (Monitor)**: 190+ categories

---

## Next Steps

1. [ ] Adapt dashboard frontend for crypto categories
2. [ ] Update API endpoints for CoinGecko data
3. [ ] Implement real-time price feeds
4. [ ] Add regime integration from AutoML_Crypto
5. [ ] Deploy to Railway

---

**Created**: 2026-02-02
**Data Source**: CoinGecko Categories, Sector-Leaders-Crypto
**Framework Version**: Three-Layer (Cohesion + Regime + Momentum)
