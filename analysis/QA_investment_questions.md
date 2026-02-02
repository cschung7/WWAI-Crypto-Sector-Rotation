# Investment Questions & Answers (Crypto Market)
**Based on Analysis Date**: 2026-02-02

**Dashboard**: http://localhost:8003

---

## Terminology Guide
| Term | Description |
|------|-------------|
| Cohesion | Category internal correlation strength (Fiedler eigenvalue) |
| SuperTrend | BB(220, 2.0) crossover - price above upper Bollinger Band |
| Breakout | Momentum stage based on trend signals |
| Signal | Trading signal from category rotation analysis |
| TIER | Category quality classification (1=Best, 4=Worst) |
| Category | CoinGecko classification (228 total categories) |

---

## Token Selection Questions

### Q1: Which tokens have the highest SuperTrend momentum today?
**Answer**: Tokens crossing above BB(220, 2.0) upper band with min $5 price

| Rank | Token | Category | BB Deviation | Signal |
|------|-------|----------|--------------|--------|
| 1 | VNXAU | tokenized_gold | +12.5% | BB Crossover |
| 2 | PAXG | tokenized_gold | +8.2% | BB Crossover |
| 3 | XAUT | tokenized_gold | +7.8% | BB Crossover |
| 4 | CGO | other | +6.1% | BB Crossover |
| 5 | INSURANCE | insurance | +5.4% | BB Crossover |
| 6 | MGC29839 | other | +4.9% | BB Crossover |

**Total**: 6 tokens crossing above BB upper (2026-02-02)

**Filter Criteria**: min_date >= 2026-01-25, min_price >= $5, valid BB(220, 2.0) calculation

**Source**: `/mnt/nas/AutoGluon/AutoML_Crypto/CRYPTONOTTRAINED/`

---

### Q2: What are the top picks in Zero Knowledge Proofs category?
**Answer**: TIER 1 category with strong privacy/ZK exposure

| Token | Ticker | Action | Combined Score |
|-------|--------|--------|----------------|
| ZEN | Horizen | AGGRESSIVE BUY | 0.281 |
| CELO | Celo | AGGRESSIVE BUY | 0.281 |
| STRK | StarkNet | AGGRESSIVE BUY | 0.281 |
| ZEC | Zcash | AGGRESSIVE BUY | 0.281 |
| ALEO | Aleo | AGGRESSIVE BUY | 0.281 |
| WLD | Worldcoin | AGGRESSIVE BUY | 0.281 |

**Source**: `/mnt/nas/WWAI/Sector-Rotation/Sector-Rotation-Crypto/data/actionable_tickers_*.csv`

---

### Q3: Which AI tokens should I buy?
**Answer**: Top AI category tokens by tier

| Token | Category | Tier | Action |
|-------|----------|------|--------|
| AI16Z | ai_memes | Tier 1 | AGGRESSIVE BUY |
| TURBO | ai_memes | Tier 1 | AGGRESSIVE BUY |
| ZEREBRO | ai_memes | Tier 1 | AGGRESSIVE BUY |
| FET | ai_&_big_data | Tier 2 | ACCUMULATE |
| RENDER | ai_&_big_data | Tier 2 | ACCUMULATE |
| NEAR | ai_&_big_data | Tier 2 | ACCUMULATE |
| ICP | ai_&_big_data | Tier 2 | ACCUMULATE |

**Note**: AI memes (ai_memes) is TIER 1 with score 0.257, while core AI (ai_&_big_data) is TIER 2

---

### Q4: What are the best DeFi tokens?
**Answer**: DeFi category tokens by performance

| Token | Category | Tier | Notable |
|-------|----------|------|---------|
| AAVE | defi | Tier 2-3 | Top lending |
| UNI | defi | Tier 2-3 | AMM leader |
| MKR | defi | Tier 2-3 | DAI stablecoin |
| GMX | derivatives | Tier 2-3 | Perps trading |
| DYDX | derivatives | Tier 2-3 | DEX leader |
| LDO | liquid_staking | Tier 2-3 | ETH staking |

**Note**: DeFi categories have mixed cohesion - individual token selection preferred

---

### Q5: Which meme tokens are trending?
**Answer**: Meme category leaders

| Token | Category | Tier | Action |
|-------|----------|------|--------|
| PONKE | ip_memes | Tier 1 | AGGRESSIVE BUY |
| NEIRO | ip_memes | Tier 1 | AGGRESSIVE BUY |
| FARTCOIN | pump_fun_ecosystem | Tier 1 | AGGRESSIVE BUY |
| PNUT | pump_fun_ecosystem | Tier 1 | AGGRESSIVE BUY |
| MOODENG | pump_fun_ecosystem | Tier 1 | AGGRESSIVE BUY |
| DOGE | memes | Tier 2-3 | ACCUMULATE |
| SHIB | memes | Tier 2-3 | ACCUMULATE |
| PEPE | memes | Tier 2-3 | ACCUMULATE |

**Note**: IP memes and pump_fun_ecosystem show strong TIER 1 signals

---

## Category/Sector Analysis Questions

### Q6: Which categories have strongest cohesion (Fiedler)?
**Answer**: Fiedler eigenvalue ranking (higher = stronger cohesion)

| Rank | Category | Fiedler | Sector | Interpretation |
|------|----------|---------|--------|----------------|
| 1 | ai_&_big_data | 7.0 | AI | Very strong cohesion |
| 2 | a16z_portfolio | 5.5 | VC_Portfolio | Strong cohesion |
| 3 | ai_agents | 5.4 | AI | Strong cohesion |
| 4 | ai_agent_launchpad | 4.0 | AI | Moderate-strong |
| 5 | ip_memes | 3.6 | Memes | Moderate cohesion |
| 6 | ai_memes | 3.1 | AI | Moderate cohesion |
| 7 | fenbushi_capital_portfolio | 2.0 | VC_Portfolio | Moderate |

**Cohesion Interpretation Guide**:
- Fiedler ≥ 7.5: Very strong (tokens move together - TIER 1)
- Fiedler 3.0-7.5: Strong (TIER 2)
- Fiedler 1.0-3.0: Moderate (TIER 3)
- Fiedler < 1.0: Weak (dispersed category - TIER 4)

---

### Q7: Which TIER 1 categories should I focus on?
**Answer**: Highest quality categories passing combined score filter

| Category | Combined Score | Fiedler | Recommendation |
|----------|----------------|---------|----------------|
| fenbushi_capital_portfolio | 0.414 | 2.0 | Focus - VC picks |
| ledgerprime_portfolio | 0.335 | 1.0 | VC exposure |
| hacken_foundation | 0.304 | 1.0 | Security focus |
| social_token | 0.298 | 0.0 | Social tokens |
| zero_knowledge_proofs | 0.281 | 1.0 | Privacy/ZK |
| ai_memes | 0.257 | 3.1 | AI + memes |
| cybersecurity | 0.251 | 1.9 | Security |
| ip_memes | 0.236 | 3.6 | Meme coins |

**Dashboard**: Signals tab → TIER breakdown

---

### Q8: Which categories failed quality filtering?
**Answer**: Categories with low combined scores (TIER 4)

| Category | Score | Fiedler | Reason |
|----------|-------|---------|--------|
| account_abstraction | -0.031 | 0.0 | Weak cohesion + negative momentum |
| USD stablecoins | ~0 | ~0 | No rotation value |
| Many smaller categories | < 0 | < 1.0 | Negative momentum |

**Note**: 421 tokens classified as TIER 4 - these have weak cohesion or negative momentum

---

### Q9: What's the current tier distribution?
**Answer**: From consolidated analysis (2026-02-02)

| Tier | Token Count | % | Action |
|------|-------------|---|--------|
| Tier 1 | 225 | 14.9% | AGGRESSIVE BUY |
| Tier 2 | 512 | 34.0% | ACCUMULATE |
| Tier 3 | 348 | 23.1% | RESEARCH |
| Tier 4 | 421 | 28.0% | MONITOR |

**Total**: 1,506 tokens across 228 categories

---

## Risk Assessment Questions

### Q10: Which tokens have highest volatility risk?
**Answer**: High volatility tokens to watch

| Token | Category | Volatility | Recent Return |
|-------|----------|------------|---------------|
| RLY | ledgerprime_portfolio | 120.2% | +214.6% |
| AI16Z | ai_memes | 49.1% | +60.5% |
| ZEREBRO | ai_memes | 49.1% | +60.5% |
| UXLINK | social_token | 34.8% | -50.0% |

**Interpretation**: High volatility = larger swings, adjust position size accordingly

---

### Q11: Which categories have weak cohesion (avoid sector plays)?
**Answer**: Fiedler < 1.0 indicates weak cohesion

| Category | Fiedler | Risk |
|----------|---------|------|
| account_abstraction | 0.0 | Very weak |
| social_token | 0.0 | Very weak |
| retail | 0.0 | Very weak |
| pump_fun_ecosystem | 1.0 | Borderline |

**Implication**: Low cohesion means tokens in category don't move together - use individual token selection

---

### Q12: What are the biggest losers (negative momentum)?
**Answer**: Categories with negative momentum

| Category | Momentum | Action |
|----------|----------|--------|
| social_token | -38.6% | AVOID |
| ai_agents | -33.1% | CAUTION |
| zero_knowledge_proofs | -28.9% | RESEARCH |
| ai_applications | -22.5% | RESEARCH |

**Note**: Negative momentum doesn't always mean avoid - check combined score

---

## Historical Performance Questions

### Q13: Which VC portfolio categories perform best?
**Answer**: VC-backed category performance

| Category | Score | Tokens |
|----------|-------|--------|
| fenbushi_capital_portfolio | 0.414 | ZEC, VET, DOT, ICP, SC, BICO |
| ledgerprime_portfolio | 0.335 | RLY, CVP, FLOW, RGT, SFI |
| a16z_portfolio | -0.043 | Various |

**Note**: VC portfolios show high trend scores but mixed momentum

---

### Q14: How do tokenized gold tokens perform?
**Answer**: Tokenized gold category (SuperTrend candidates)

| Token | Signal | Deviation |
|-------|--------|-----------|
| VNXAU | BB Crossover | +12.5% |
| PAXG | BB Crossover | +8.2% |
| XAUT | BB Crossover | +7.8% |

**Note**: Tokenized gold showing strong BB crossover signals

---

### Q15: What categories should I avoid?
**Answer**: Negative combined score categories

| Category | Score | Momentum | Recommendation |
|----------|-------|----------|----------------|
| social_token | 0.298 | -38.6% | High risk |
| ai_agents | -0.152 | -33.1% | Declining |
| ai_applications | -0.034 | -22.5% | Weak |

---

## Portfolio Construction Questions

### Q16: How to prioritize between SuperTrend and Category picks?
**Answer**: Use priority tiers

| Priority | Strategy | Criteria | Rationale |
|----------|----------|----------|-----------|
| HIGH | SuperTrend | BB crossover + min $5 | Technical breakout |
| MEDIUM | TIER 1 | Combined score > 0.20 | Category rotation |
| LOW | TIER 2 | Score 0.10-0.20 | Accumulation zone |

**Suggested Allocation**:
- 30-40% to SuperTrend (BB crossover) - currently 6 tokens
- 40-50% to TIER 1 categories
- 10-20% to TIER 2 selective

---

### Q17: Which categories have overlap (diversification risk)?
**Answer**: Multi-category exposure tokens

| Token | Categories | Risk |
|-------|------------|------|
| ZEC | zero_knowledge_proofs, fenbushi | Correlated |
| RLY | ledgerprime, social_token | Correlated |
| HAPI | hacken_foundation, cybersecurity | Correlated |
| AI16Z | ai_memes, ai_agents | Correlated |

**Implication**: Holding overlapping tokens reduces diversification benefit

---

### Q18: How many tokens passed all quality filters?
**Answer**: Filtering pipeline summary

| Stage | Count | Pass Rate |
|-------|-------|-----------|
| Universe | 1,506 | 100% |
| BB Crossover (SuperTrend) | 6 | 0.4% |
| TIER 1 (Aggressive Buy) | 225 | 14.9% |
| TIER 2 (Accumulate) | 512 | 34.0% |
| Final Actionable (T1+T2) | 737 | 48.9% |

---

## Questions NOT Answerable (Need Additional Analysis)

| Question | Missing Data | How to Get |
|----------|--------------|------------|
| Exact on-chain metrics? | Blockchain data | Use DeFiLlama, Dune |
| Trading volume analysis? | Volume data | CoinGecko API |
| Optimal position sizing? | Portfolio constraints | Risk management model |
| Smart contract risk? | Audit reports | Security audit providers |
| Exchange liquidity? | Order book data | Exchange APIs |
| Intraday entry timing? | Tick data | Real-time data feed |

---

## Quick Reference: Data File Locations

| Data | File Path |
|------|-----------|
| Actionable tickers | `/mnt/nas/WWAI/Sector-Rotation/Sector-Rotation-Crypto/data/actionable_tickers_*.csv` |
| Consolidated analysis | `/mnt/nas/WWAI/Sector-Rotation/Sector-Rotation-Crypto/data/consolidated_ticker_analysis_*.json` |
| Tier 1 tokens | `/mnt/nas/WWAI/Sector-Rotation/Sector-Rotation-Crypto/data/tier1_buy_now_*.csv` |
| Combined score ranking | `/mnt/nas/WWAI/Sector-Rotation/Sector-Rotation-Crypto/data/combined_score_ranking_*.csv` |
| Category mapping | `/mnt/nas/WWAI/Sector-Rotation/Sector-Rotation-Crypto/theme_ticker_master.csv` |
| Price data | `/mnt/nas/AutoGluon/AutoML_Crypto/CRYPTONOTTRAINED/` |

---

## Dashboard Navigation

| Tab | URL | Key Feature |
|-----|-----|-------------|
| Overview | http://localhost:8003/ | Market summary, top categories |
| Breakout | http://localhost:8003/breakout.html | SuperTrend + Breakout candidates |
| Signals | http://localhost:8003/signals.html | Quality funnel, TIER breakdown |
| Cohesion | http://localhost:8003/cohesion.html | Category cohesion analysis |
| Network | http://localhost:8003/network.html | Category network visualization |

---

*Generated: 2026-02-02*
*Analysis Framework: Sector-Rotation-Crypto*
*Dashboard: http://localhost:8003*
