"""
Crypto Sector Rotation - Configuration
Adapted from USA system for cryptocurrency market
"""

from pathlib import Path
from datetime import datetime

# ===== PATHS =====
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
REPORTS_DIR = PROJECT_ROOT / "reports"
ANALYSIS_DIR = PROJECT_ROOT / "analysis"
LOGS_DIR = PROJECT_ROOT / "logs"

# Related projects
SECTOR_LEADERS_CRYPTO = Path("/mnt/nas/WWAI/Sector-Rotation/Sector-Leaders-Crypto")
SECTOR_ROTATION_OLD = Path("/mnt/nas/WWAI/Sector-Rotation/Sector-Rotation-Crypto-2026-02-01")

# Data sources
THEME_TICKER_MASTER = PROJECT_ROOT / "theme_ticker_master.csv"
SECTOR_LEADERS_RESULTS = SECTOR_LEADERS_CRYPTO / "results"
SECTOR_LEADERS_DATA = SECTOR_LEADERS_CRYPTO / "data"

# ===== ANALYSIS PARAMETERS =====
# Fiedler eigenvalue calculation
FIEDLER_CONFIG = {
    "threshold": 0.30,          # Correlation threshold (higher for crypto volatility)
    "window": 20,               # Rolling correlation window
    "min_tokens": 3,            # Minimum tokens for valid theme
    "lookback_days": 60,        # Price data lookback (longer for crypto)
}

# TIER classification thresholds (Fiedler-based)
TIER_THRESHOLDS = {
    "tier1": 7.5,               # Fiedler >= 7.5 → TIER 1 (Strong Cohesion)
    "tier2": 3.0,               # Fiedler >= 3.0 → TIER 2 (Moderate Cohesion)
    "tier3": 1.0,               # Fiedler >= 1.0 → TIER 3 (Weak Cohesion)
    # Below tier3 → TIER 4
}

# Combined Score thresholds (alternative)
SCORE_THRESHOLDS = {
    "tier1": 0.20,              # Combined score >= 0.20 → TIER 1
    "tier2": 0.10,              # Combined score >= 0.10 → TIER 2
    "tier3": 0.05,              # Combined score >= 0.05 → TIER 3
}

# Signal filtering
SIGNAL_CONFIG = {
    "min_momentum": -0.10,      # Minimum momentum score (allow some negative)
    "min_fiedler": 1.0,         # Minimum Fiedler value for cohesion
    "min_bull_ratio": 0.2,      # Minimum bull ratio
}

# ===== CRYPTO CATEGORY CLASSIFICATION =====
# 228 CoinGecko Categories mapped to meta-categories

CATEGORY_TO_SECTOR = {
    # === AI & Big Data ===
    "ai_&_big_data": "AI",
    "ai_agents": "AI",
    "ai_applications": "AI",
    "ai_memes": "AI",
    "ai_agent_launchpad": "AI",
    "generative_ai": "AI",
    "defai": "AI",

    # === DeFi ===
    "defi": "DeFi",
    "amm": "DeFi",
    "derivatives": "DeFi",
    "yield_farming": "DeFi",
    "yield_aggregator": "DeFi",
    "liquid_staking_derivatives": "DeFi",
    "decentralized_exchange_dex_token": "DeFi",
    "restaking": "DeFi",
    "protocol-owned_liquidity": "DeFi",
    "synthetics": "DeFi",

    # === Infrastructure ===
    "depin": "Infrastructure",
    "oracles": "Infrastructure",
    "storage": "Infrastructure",
    "distributed_computing": "Infrastructure",
    "interoperability": "Infrastructure",
    "scaling": "Infrastructure",
    "layer_1": "Infrastructure",
    "rollups": "Infrastructure",
    "data_availability": "Infrastructure",
    "modular_blockchain": "Infrastructure",

    # === Gaming & Metaverse ===
    "gaming": "Gaming",
    "gaming_guild": "Gaming",
    "metaverse": "Gaming",
    "play_to_earn": "Gaming",
    "move_to_earn": "Gaming",

    # === Privacy & Security ===
    "privacy": "Privacy",
    "zero_knowledge_proofs": "Privacy",
    "cybersecurity": "Privacy",

    # === Memes ===
    "memes": "Memes",
    "animal_memes": "Memes",
    "cat-themed": "Memes",
    "celebrity_memes": "Memes",
    "political_memes": "Memes",
    "ip_memes": "Memes",
    "tron_memes": "Memes",
    "ai_memes": "Memes",
    "doggone_doggerel": "Memes",

    # === RWA & Tokenization ===
    "real_world_assets_protocols": "RWA",
    "tokenized_assets": "RWA",
    "tokenized_commodities": "RWA",
    "tokenized_gold": "RWA",
    "tokenized_real_estate": "RWA",

    # === Stablecoins ===
    "stablecoin": "Stablecoins",
    "usd_stablecoin": "Stablecoins",
    "fiat_stablecoin": "Stablecoins",
    "eur_stablecoin": "Stablecoins",
    "algorithmic_stablecoin": "Stablecoins",

    # === Ecosystems ===
    "solana_ecosystem": "Ecosystem",
    "ethereum_ecosystem": "Ecosystem",
    "bnb_chain_ecosystem": "Ecosystem",
    "bitcoin_ecosystem": "Ecosystem",
    "base_ecosystem": "Ecosystem",
    "arbitrum_ecosystem": "Ecosystem",
    "polygon_ecosystem": "Ecosystem",
    "cosmos_ecosystem": "Ecosystem",
    "aptos_ecosystem": "Ecosystem",
    "avalanche_ecosystem": "Ecosystem",
    "sui_ecosystem": "Ecosystem",
    "tron_ecosystem": "Ecosystem",
    "near_protocol_ecosystem": "Ecosystem",
    "optimism_ecosystem": "Ecosystem",
    "fantom_ecosystem": "Ecosystem",
    "cardano_ecosystem": "Ecosystem",
    "polkadot_ecosystem": "Ecosystem",

    # === VC Portfolios ===
    "a16z_portfolio": "VC_Portfolio",
    "coinbase_ventures_portfolio": "VC_Portfolio",
    "paradigm_portfolio": "VC_Portfolio",
    "polychain_capital_portfolio": "VC_Portfolio",
    "binance_launchpad": "VC_Portfolio",
    "alameda_research_portfolio": "VC_Portfolio",
    "winklevoss_capital_portfolio": "VC_Portfolio",
    "world_liberty_financial_portfolio": "VC_Portfolio",

    # === Special ===
    "us_strategic_crypto_reserve": "Special",
    "pump_fun_ecosystem": "Special",
    "virtuals_protocol_ecosystem": "Special",
    "hyperliquid_ecosystem": "Special",
}

# Level 2 Categories (from old analysis)
LEVEL2_CATEGORIES = {
    "Infrastructure": {"tokens": 335, "description": "Oracles, bridges, storage, privacy, scaling"},
    "DeFi": {"tokens": 223, "description": "Decentralized Finance protocols"},
    "CeFi": {"tokens": 52, "description": "Centralized Finance (exchanges, etc.)"},
    "Entertainment": {"tokens": 91, "description": "Gaming, NFT, metaverse, fan tokens"},
}

# ===== TIER DESCRIPTIONS =====
TIER_DESCRIPTIONS = {
    "Tier 1": {
        "action": "BUY",
        "description": "Strong cohesion (Fiedler ≥7.5), sector rotation signal active",
        "color": "#059669",  # Green
    },
    "Tier 2": {
        "action": "ACCUMULATE",
        "description": "Moderate cohesion (Fiedler 3.0-7.5), building strength",
        "color": "#10b981",  # Light green
    },
    "Tier 3": {
        "action": "RESEARCH",
        "description": "Weak cohesion (Fiedler 1.0-3.0), individual selection",
        "color": "#f59e0b",  # Amber
    },
    "Tier 4": {
        "action": "MONITOR",
        "description": "Very weak/no cohesion (Fiedler <1.0), avoid sector plays",
        "color": "#ef4444",  # Red
    },
}

# ===== TOKEN MAPPING (Top tokens per category) =====
CATEGORY_TOP_TOKENS = {
    "memes": ["DOGE", "SHIB", "BONK", "FLOKI", "WIF", "PEPE"],
    "ai_&_big_data": ["FET", "RENDER", "NEAR", "ICP", "FIL", "INJ"],
    "gaming": ["GALA", "SAND", "MANA", "AXS", "ENJ", "ILV"],
    "defi": ["AAVE", "UNI", "MKR", "COMP", "CRV", "SNX"],
    "solana_ecosystem": ["SOL", "JUP", "RENDER", "BONK", "RAY"],
    "privacy": ["XMR", "ZEC", "DASH", "ZEN", "SCRT"],
    "zero_knowledge_proofs": ["MATIC", "MINA", "IMX", "LRC"],
    "infrastructure": ["LINK", "FIL", "AR", "GRT", "RNDR"],
    "tokenized_gold": ["PAXG", "XAUT"],
}

# ===== FORMATTING =====
def format_price(price: float) -> str:
    """Format price in USD"""
    if price >= 1:
        return f"${price:,.2f}"
    elif price >= 0.01:
        return f"${price:.4f}"
    else:
        return f"${price:.8f}"

def format_market_cap(cap: float) -> str:
    """Format market cap with T/B/M suffix"""
    if cap >= 1e12:
        return f"${cap/1e12:.1f}T"
    if cap >= 1e9:
        return f"${cap/1e9:.1f}B"
    if cap >= 1e6:
        return f"${cap/1e6:.1f}M"
    return f"${cap:,.0f}"

def format_pct(value: float) -> str:
    """Format percentage"""
    return f"{value:+.2f}%"

# ===== DATE UTILITIES =====
def get_latest_date_suffix() -> str:
    """Get YYYYMMDD suffix for latest data"""
    return datetime.now().strftime("%Y%m%d")

def get_latest_analysis_file(pattern: str) -> Path:
    """Find the most recent file matching pattern in results directory"""
    files = sorted(SECTOR_LEADERS_RESULTS.glob(pattern), reverse=True)
    return files[0] if files else None
