# Crypto Sector Rotation Project

## Overview

Cryptocurrency market sector rotation analysis system using Three-Layer Framework:
- **Layer 1**: Category Cohesion (Fiedler eigenvalue analysis)
- **Layer 2**: Market Regime Detection (Bull/Bear/Neutral)
- **Layer 3**: Momentum/Trend Signals (from CoinGecko data)

**Key Stats**: 228 CoinGecko categories, 1,506 tokens, 10 meta-sectors

**Dashboard Port**: 8003 (local)

---

## Dashboard Pages

### 1. Overview (`index.html`)
- Market summary with total tickers, categories, average cohesion
- Top picks by tier classification
- Quick navigation to all pages

### 2. Breakout Scanner (`breakout.html`)
- Bollinger Band BB(220, 2.0) crossover signals
- SuperTrend candidates (filtered by min_date 2026-01-25, min_price $5)
- Stage classification (Super Trend, Early Breakout, Building, etc.)
- **Current SuperTrend**: 6 candidates (VNXAU, PAXG, XAUT, CGO, INSURANCE, MGC29839)

### 3. Signals (`signals.html`)
- Category signal quality matrix
- Category-level cohesion analysis
- Tier distribution overview

### 4. Cohesion (`cohesion.html`)
- Cohesion score visualization by category (228 categories)
- Interactive bar chart with tier colors
- Category health metrics

### 5. Network (`network.html`)
- Interactive vis-network graph with token-category relationships
- Buy/Avoid signal coloring (green/red)
- Quick example buttons for popular categories (memes, defi, ai_agents)
- Category filtering and search

---

## TIER Classification (Fiedler-Based)

| Tier | Action | Fiedler | Description | Count |
|------|--------|---------|-------------|-------|
| **Tier 1** | AGGRESSIVE BUY | ≥ 7.5 | Strong cohesion, sector rotation active | 225 |
| **Tier 2** | ACCUMULATE | 3.0-7.5 | Moderate cohesion, building strength | 512 |
| **Tier 3** | RESEARCH | 1.0-3.0 | Weak cohesion, individual selection | 348 |
| **Tier 4** | MONITOR | < 1.0 | No cohesion, avoid sector plays | 421 |

---

## Stage Classification (Breakout Scanner)

Stages are determined from momentum and trend signals:

| Stage | Criteria | Priority | Action |
|-------|----------|----------|--------|
| **Super Trend** | BB(220,2) crossover + recent data + min $5 | HIGH | BUY |
| **Early Breakout** | momentum > 0.05 + bull_ratio ≥ 0.5 | HIGH | BUY |
| **Building** | momentum > 0 | MEDIUM | HOLD |
| **Consolidation** | momentum ≈ 0 | LOW | WATCH |
| **Declining** | momentum < 0 | AVOID | AVOID |

---

## Project Structure

```
Sector-Rotation-Crypto/
├── dashboard/
│   ├── backend/                    # FastAPI server
│   │   ├── main.py                 # Entry point (port 8003)
│   │   └── routers/
│   │       ├── sector_rotation.py  # Overview, category health APIs
│   │       ├── breakout.py         # BB crossover + momentum APIs
│   │       ├── network.py          # Network graph APIs
│   │       └── signals.py          # Signal matrix APIs
│   └── frontend/
│       ├── index.html              # Main dashboard
│       ├── breakout.html           # SuperTrend + Breakout scanner
│       ├── signals.html            # Signal quality matrix
│       ├── cohesion.html           # Cohesion visualization
│       └── network.html            # Interactive network graph
├── data/
│   ├── actionable_tickers_*.csv    # Ticker recommendations (1,506 rows)
│   ├── consolidated_ticker_analysis_*.json  # Category analysis (228 categories)
│   ├── tier1_buy_now_*.csv         # Tier 1 candidates
│   ├── tier2_accumulate_*.csv      # Tier 2 candidates
│   ├── tier3_research_*.csv        # Tier 3 candidates
│   ├── tier4_monitor_*.csv         # Tier 4 candidates
│   ├── combined_score_ranking_*.csv
│   └── monthly_fiedler_crypto_*.csv
├── analysis/                       # Analysis reports & QA
├── docs/                           # Documentation
├── theme_ticker_master.csv         # Category-ticker mapping
├── config.py                       # Configuration
├── requirements.txt                # Python dependencies
├── railway.json                    # Railway deployment config
├── Procfile                        # Process file for deployment
└── CLAUDE.md                       # This file
```

---

## API Endpoints

### Overview APIs
| Endpoint | Purpose |
|----------|---------|
| `GET /api/overview/summary` | Market overview stats |
| `GET /api/overview/top-picks` | Top breakout candidates |
| `GET /api/overview/theme-health` | Category health with tier/signal |
| `GET /api/overview/themes` | All category details |

### Breakout APIs
| Endpoint | Purpose |
|----------|---------|
| `GET /api/breakout/candidates` | All breakout candidates |
| `GET /api/breakout/stages` | Stage distribution (includes SuperTrend count) |
| `GET /api/breakout/supertrend` | BB(220,2) crossover candidates |
| `GET /api/breakout/by-category/{name}` | Category-specific candidates |

### Signal APIs
| Endpoint | Purpose |
|----------|---------|
| `GET /api/signals/quality` | Signal quality metrics |
| `GET /api/signals/filter-funnel` | Filtering stages visualization |
| `GET /api/signals/tier-breakdown` | Detailed TIER statistics |
| `GET /api/signals/top-signals` | Top signals by score |

### Network APIs
| Endpoint | Purpose |
|----------|---------|
| `GET /api/network/graph-data` | Network graph nodes/edges |
| `GET /api/network/graph-data?stock=BTC` | Token-centered graph |
| `GET /api/network/graph-data?theme=memes` | Category-centered graph |
| `GET /api/network/search?q=bitcoin` | Search tokens/categories |
| `GET /api/network/stock-themes?name=ETH` | Get categories for a token |
| `GET /api/network/theme-stocks?theme=defi` | Get tokens in a category |

---

## Top Categories by Performance (Dec 2025)

### By Combined Score
| Rank | Category | Score | Sector |
|------|----------|-------|--------|
| 1 | fenbushi_capital_portfolio | 0.414 | VC_Portfolio |
| 2 | ledgerprime_portfolio | 0.335 | VC_Portfolio |
| 3 | hacken_foundation | 0.304 | Other |
| 4 | social_token | 0.298 | Other |
| 5 | zero_knowledge_proofs | 0.281 | Privacy |
| 6 | ai_memes | 0.257 | AI |
| 7 | cybersecurity | 0.251 | Other |
| 8 | ip_memes | 0.236 | Memes |
| 9 | pump_fun_ecosystem | 0.225 | Ecosystem |
| 10 | retail | 0.223 | Other |

### Top TIER 1 Tokens
| Token | Category | Action |
|-------|----------|--------|
| ZEC | zero_knowledge_proofs | AGGRESSIVE BUY |
| DOT | fenbushi_capital_portfolio | AGGRESSIVE BUY |
| ICP | fenbushi_capital_portfolio | AGGRESSIVE BUY |
| FLOW | ledgerprime_portfolio | AGGRESSIVE BUY |
| AI16Z | ai_memes | AGGRESSIVE BUY |
| TURBO | ai_memes | AGGRESSIVE BUY |
| WLD | zero_knowledge_proofs | AGGRESSIVE BUY |
| STRK | zero_knowledge_proofs | AGGRESSIVE BUY |

---

## Data Sources

| Data Type | Location | Update |
|-----------|----------|--------|
| Category Rankings | `../Sector-Leaders-Crypto/results/` | Weekly |
| Category-Ticker Map | `./theme_ticker_master.csv` | As needed |
| Historical Fiedler | `./data/monthly_fiedler_crypto_*.csv` | Monthly |
| Price Data | `/mnt/nas/AutoGluon/AutoML_Crypto/CRYPTONOTTRAINED/` | Daily |

---

## Quick Commands

### Start Dashboard (Local)
```bash
cd /mnt/nas/WWAI/Sector-Rotation/Sector-Rotation-Crypto/dashboard/backend
uvicorn main:app --host 0.0.0.0 --port 8003 --reload
```

### Access Dashboard
- Local: http://localhost:8003/
- Overview: http://localhost:8003/
- Breakout: http://localhost:8003/breakout.html
- Signals: http://localhost:8003/signals.html
- Cohesion: http://localhost:8003/cohesion.html
- Network: http://localhost:8003/network.html

### Test APIs
```bash
# Search tokens
curl "http://localhost:8003/api/network/search?q=bitcoin"

# Get SuperTrend candidates
curl "http://localhost:8003/api/breakout/supertrend"

# Get category network
curl "http://localhost:8003/api/network/graph-data?theme=memes"
```

---

## Category Deep Dive

### AI Categories (7)
| Category | Top Tokens |
|----------|------------|
| ai_&_big_data | FET, RENDER, NEAR, ICP |
| ai_agents | VIRTUAL, AI16Z |
| ai_memes | TURBO, ZEREBRO, FARTCOIN |
| ai_applications | TAO, OLAS |

### DeFi Categories (10+)
| Category | Top Tokens |
|----------|------------|
| defi | AAVE, UNI, MKR |
| amm | UNI, SUSHI, CRV |
| derivatives | GMX, DYDX, SNX |
| liquid_staking | LDO, RPL |

### Memes Categories (9)
| Category | Top Tokens |
|----------|------------|
| memes | DOGE, SHIB, PEPE |
| animal_memes | DOGE, SHIB, BONK |
| ai_memes | TURBO, AI16Z |
| ip_memes | PONKE, NEIRO |

### Privacy Categories (3)
| Category | Top Tokens |
|----------|------------|
| privacy | XMR, ZEC, DASH |
| zero_knowledge_proofs | ZEN, STRK, WLD, ALEO |
| cybersecurity | HAPI, UTK |

---

## Crypto-Specific Considerations

### Market Characteristics
- **24/7 Trading**: No market close, continuous price discovery
- **High Volatility**: 40-100%+ typical, adjust thresholds accordingly
- **Correlation Regimes**: Strong bull/bear correlation patterns
- **BTC Dominance**: Market leader affects all categories

### Framework Adaptations
- **Higher Correlation Threshold**: 0.30 (vs 0.25 for equities)
- **Longer Lookback**: BB(220, 2.0) for SuperTrend calculation
- **Fiedler Thresholds**: 7.5/3.0/1.0 (adapted for crypto)
- **Price Filter**: Min $5 for SuperTrend to avoid micro-caps

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
| BB Parameters | (220, 2.0) | (220, 2.0) | (220, 2.0) | (220, 2.0) |

---

## Global Dashboard Network

| Market | URL | Port | Status |
|--------|-----|------|--------|
| KRX | Railway | 8000 | Live |
| USA | Railway | 8001 | Live |
| Japan | Local | 8002 | WIP |
| **Crypto** | Local | 8003 | **Live** |
| China | Local | 8004 | WIP |

---

## Related Projects

| Project | Path | Description |
|---------|------|-------------|
| Sector-Leaders-Crypto | `../Sector-Leaders-Crypto/` | Category rankings |
| AutoML Crypto | `/mnt/nas/AutoGluon/AutoML_Crypto/` | Price data & regime |

---

## Recent Updates (2026-02-02)

### Dashboard Setup
1. Cloned from Sector-Rotation-USA
2. Updated all routers for crypto data format
3. Fixed cohesion.html (categories array support)
4. Fixed network.html (categories array support)
5. Added BB(220, 2.0) crossover calculation with filters

### Data Processing
- Consolidated analysis: 228 categories, 1,506 tokens
- Tier distribution: 225 T1, 512 T2, 348 T3, 421 T4
- SuperTrend candidates: 6 tokens passing all filters

---

**Created**: 2026-02-02
**Data Source**: CoinGecko Categories, Sector-Leaders-Crypto
**Framework Version**: Three-Layer (Cohesion + Regime + Momentum)
