"""
Breakout/Momentum Scanner API Router - Crypto
Adapted for cryptocurrency markets with CoinGecko categories
"""

from fastapi import APIRouter, HTTPException, Query
from pathlib import Path
import pandas as pd
import json
from typing import List, Dict, Any, Optional
import math
import glob
from datetime import datetime

router = APIRouter()

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"

# AutoML Crypto paths - optional for cloud deployment
AUTOML_CRYPTO_DIR = Path("/mnt/nas/AutoGluon/AutoML_Crypto")
FILTER_DIR = AUTOML_CRYPTO_DIR / "Filter"
DB_DIR = AUTOML_CRYPTO_DIR / "DB"
PRICE_DIR = AUTOML_CRYPTO_DIR / "CRYPTONOTTRAINED"
# Check if paths exist (won't exist on Railway deployment)
HAS_PRICE_DATA = PRICE_DIR.exists()

# Cache for category lookup
_category_cache = None
# Cache for price data (used on Railway when PRICE_DIR doesn't exist)
_price_cache = None


def load_price_cache() -> dict:
    """Load price cache from data directory (for Railway deployment)"""
    global _price_cache
    if _price_cache is None:
        cache_file = DATA_DIR / "price_cache.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                    _price_cache = data.get('prices', {})
            except Exception:
                _price_cache = {}
        else:
            _price_cache = {}
    return _price_cache


def get_category_mapping() -> dict:
    """Load and cache category mapping from theme_ticker_master.csv"""
    global _category_cache
    if _category_cache is None:
        try:
            master_file = PROJECT_ROOT / "theme_ticker_master.csv"
            if master_file.exists():
                df = pd.read_csv(master_file)
                # Create ticker -> category mapping
                _category_cache = {}
                for _, row in df.iterrows():
                    ticker = row.get('ticker', '').upper()
                    if ticker:
                        _category_cache[ticker] = row.get('category', '')
            else:
                _category_cache = {}
        except Exception as e:
            print(f"Error loading category data: {e}")
            _category_cache = {}
    return _category_cache


def safe_float(value) -> float:
    """Convert to float, return 0 if NaN/None"""
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return 0.0
    return float(value)


def load_actionable_tickers() -> pd.DataFrame:
    """Load the latest actionable tickers"""
    files = sorted(DATA_DIR.glob("actionable_tickers_*.csv"), reverse=True)
    if not files:
        raise HTTPException(status_code=404, detail="No actionable tickers found")
    return pd.read_csv(files[0])


def load_consolidated() -> Dict:
    """Load consolidated analysis"""
    files = sorted(DATA_DIR.glob("consolidated_ticker_analysis_*.json"), reverse=True)
    if not files:
        raise HTTPException(status_code=404, detail="No consolidated analysis found")
    with open(files[0]) as f:
        return json.load(f)


def load_bb_filtered_tickers() -> Dict:
    """Load BB crossover filtered tickers for crypto"""
    # Try the main bb_filtered_tickers.json
    bb_file = FILTER_DIR / "bb_filtered_tickers.json"
    if not bb_file.exists():
        return {}

    try:
        with open(bb_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Convert array format to dict format if needed
        if isinstance(data, list):
            result = {}
            for item in data:
                if isinstance(item, dict) and 'date' in item and 'tickers' in item:
                    result[item['date']] = item['tickers']
            return result
        return data
    except Exception as e:
        print(f"Error loading BB filter: {e}")
        return {}


def get_ticker_price_info(ticker: str) -> Dict:
    """Get latest price info for a crypto ticker"""
    # If no local price files, use price cache
    if not HAS_PRICE_DATA:
        price_cache = load_price_cache()
        # Try ticker as-is or cleaned version
        clean_ticker = ticker.replace('-USD', '').upper()
        price = price_cache.get(clean_ticker, price_cache.get(ticker, 0))
        if price:
            return {'close': price}
        return {}

    # Crypto files are named TICKER-USD.csv
    price_file = PRICE_DIR / f"{ticker}-USD.csv"
    if not price_file.exists():
        # Try without -USD suffix
        price_file = PRICE_DIR / f"{ticker}.csv"
    if not price_file.exists():
        return {}

    try:
        df = pd.read_csv(price_file, index_col=0)
        df.columns = [col.lower() for col in df.columns]
        if 'close' not in df.columns or len(df) < 220:
            return {}

        # Calculate BB (220, 2.0)
        close = df['close']
        bb_middle = close.rolling(220).mean()
        bb_std = close.rolling(220).std(ddof=1)
        bb_upper = bb_middle + (bb_std * 2.0)

        last_close = close.iloc[-1]
        last_upper = bb_upper.iloc[-1]
        deviation_pct = (last_close - last_upper) / last_upper * 100 if last_upper else 0

        # Check for BB crossover (price crossed above upper band)
        prev_close = close.iloc[-2] if len(df) >= 2 else last_close
        prev_upper = bb_upper.iloc[-2] if len(df) >= 2 else last_upper

        # Crossover: was below, now above
        crossed_above = (prev_close <= prev_upper) and (last_close > last_upper) if not pd.isna(prev_upper) else False
        # Currently above upper band
        above_upper = last_close > last_upper if not pd.isna(last_upper) else False

        # Get price change
        change_pct = (last_close - prev_close) / prev_close * 100 if prev_close else 0

        return {
            'close': round(last_close, 4),
            'bb_upper': round(last_upper, 4) if not pd.isna(last_upper) else 0,
            'deviation_pct': round(deviation_pct, 2),
            'change_pct': round(change_pct, 2),
            'crossed_above': crossed_above,
            'above_upper': above_upper
        }
    except Exception:
        return {}


def compute_bb_crossovers(limit: int = 50, min_date: str = "2026-01-25", min_price: float = 5.0) -> List[Dict]:
    """
    Compute BB(220, 2.0) crossovers from price data.
    Returns tickers where price is above upper Bollinger Band.
    Only includes tickers with data updated on or after min_date.
    Filters out zero/missing price data before BB calculation.
    Filters out tickers with price < min_price ($5 default).
    """
    crossover_tickers = []

    # Use cached data if no price data available (cloud deployment)
    if not HAS_PRICE_DATA:
        cache_file = DATA_DIR / "bb_crossover_candidates.json"
        if cache_file.exists():
            try:
                with open(cache_file) as f:
                    cached = json.load(f)
                    category_map = get_category_mapping()
                    for t in cached.get('tickers', [])[:limit]:
                        ticker = t.get('ticker', '')
                        ticker_clean = t.get('ticker_clean', ticker.replace('-USD', ''))
                        crossover_tickers.append({
                            'ticker': ticker_clean,  # Use clean ticker without -USD
                            'ticker_clean': ticker_clean,
                            'category': category_map.get(ticker.upper(), category_map.get(ticker_clean.upper(), '')),
                            'close': t.get('close', 0),
                            'bb_upper': t.get('upper_band', t.get('bb_upper', 0)),  # Support both formats
                            'deviation_pct': t.get('deviation_pct', 0),
                            'change_pct': 0,  # Not available in cache
                            'last_date': t.get('last_date', ''),
                            'signal': 'BB Crossover',
                            'stage': 'Super Trend',
                            'priority': 'HIGH'
                        })
            except Exception as e:
                print(f"Error loading cached BB data: {e}")
        return crossover_tickers

    # Get list of price files
    price_files = list(PRICE_DIR.glob("*-USD.csv"))

    for price_file in price_files:
        ticker = price_file.stem.replace("-USD", "")

        try:
            df = pd.read_csv(price_file, index_col=0)
            df.columns = [col.lower() for col in df.columns]

            if 'close' not in df.columns:
                continue

            # Check if data is recent enough (last date >= min_date)
            last_date = df.index[-1]
            if str(last_date) < min_date:
                continue

            # Filter out zero and NaN close prices BEFORE calculating BB
            close = df['close'].replace(0, pd.NA).dropna()

            # Need at least 220 valid data points
            if len(close) < 220:
                continue

            # Skip if last close is NaN or 0
            last_close = close.iloc[-1]
            if pd.isna(last_close) or last_close == 0:
                continue

            # Calculate BB on clean data
            bb_middle = close.rolling(220).mean()
            bb_std = close.rolling(220).std(ddof=1)
            bb_upper = bb_middle + (bb_std * 2.0)

            last_upper = bb_upper.iloc[-1]

            if pd.isna(last_upper) or last_upper == 0:
                continue

            # Check if price is above upper BB and meets min_price threshold
            if last_close > last_upper and last_close >= min_price:
                deviation_pct = (last_close - last_upper) / last_upper * 100

                # Get price change (from valid prices only)
                prev_close = close.iloc[-2] if len(close) >= 2 else last_close
                change_pct = (last_close - prev_close) / prev_close * 100 if prev_close else 0

                # Format prices - use scientific notation for very small values
                if last_close < 0.0001:
                    close_fmt = f"{last_close:.2e}"
                    upper_fmt = f"{last_upper:.2e}"
                else:
                    close_fmt = round(last_close, 6)
                    upper_fmt = round(last_upper, 6)

                crossover_tickers.append({
                    'ticker': ticker,
                    'close': close_fmt,
                    'bb_upper': upper_fmt,
                    'deviation_pct': round(deviation_pct, 2),
                    'change_pct': round(change_pct, 2),
                    'last_date': str(last_date)
                })
        except Exception:
            continue

    # Sort by deviation (how far above the upper band)
    crossover_tickers = sorted(crossover_tickers, key=lambda x: x['deviation_pct'], reverse=True)

    return crossover_tickers[:limit]


def load_filter_data(filter_type: str = "lrs_green_cross_strategy") -> Dict:
    """Load filter data from AutoML_Crypto/Filter"""
    # Try CRYPTONOTTRAINED prefixed version first
    pattern = str(FILTER_DIR / f"CRYPTONOTTRAINED_{filter_type}.json")
    files = glob.glob(pattern)

    if not files:
        # Try Crypto dated version
        pattern = str(FILTER_DIR / f"Crypto_*_{filter_type}_tv.json")
        files = sorted(glob.glob(pattern), reverse=True)

    if not files:
        # Try direct name
        pattern = str(FILTER_DIR / f"{filter_type}.json")
        files = glob.glob(pattern)

    if not files:
        return {}

    try:
        with open(files[0]) as f:
            return json.load(f)
    except Exception:
        return {}


def get_stage_from_signals(momentum: float, bull_ratio: float, in_green: bool = False, in_tstop: bool = False) -> tuple:
    """Determine stage and priority from signals"""
    if momentum > 0.1 and bull_ratio >= 0.5:
        if in_green:
            return "Super Trend", "HIGH"
        return "Early Breakout", "HIGH"
    elif momentum > 0.05:
        if in_tstop:
            return "Early Breakout", "MEDIUM"
        return "Burgeoning", "MEDIUM"
    elif momentum > 0:
        return "Building", "LOW"
    elif momentum < -0.05:
        return "Bear Volatile", "AVOID"
    else:
        return "Consolidation", "LOW"


def get_green_tickers_for_date(green_data: Dict, target_date: str = None) -> set:
    """Extract green tickers from the crypto green filter format"""
    green_tickers = set()

    if not green_data:
        return green_tickers

    # Format: {"date": {"turn_green": [], "momentum": {...}, "trend": []}}
    if target_date and target_date in green_data:
        date_data = green_data[target_date]
        for t in date_data.get('turn_green', []):
            ticker = t.split(':')[-1] if ':' in t else t
            ticker = ticker.replace('-USD', '').upper()
            green_tickers.add(ticker)
    else:
        # Get latest date with data
        dates = sorted(green_data.keys(), reverse=True)
        for date in dates[:5]:  # Check last 5 dates
            date_data = green_data.get(date, {})
            for t in date_data.get('turn_green', []):
                ticker = t.split(':')[-1] if ':' in t else t
                ticker = ticker.replace('-USD', '').upper()
                green_tickers.add(ticker)
            if green_tickers:
                break

    return green_tickers


@router.get("/candidates")
async def get_breakout_candidates(
    stage: Optional[str] = Query(None, description="Filter by stage"),
    priority: Optional[str] = Query(None, description="Filter by priority (HIGH, MEDIUM, LOW)"),
    min_score: Optional[int] = Query(None, description="Minimum score filter"),
    theme: Optional[str] = Query(None, description="Filter by category name"),
    limit: int = Query(100, description="Max results")
) -> Dict[str, Any]:
    """Get breakout candidates with filtering"""
    try:
        df = load_actionable_tickers()

        # Load filter data for green/tstop status
        green_data = load_filter_data("lrs_green_cross_strategy")
        green_tickers = get_green_tickers_for_date(green_data)

        tstop_data = load_filter_data("tstop_filtered")
        tstop_tickers = set()
        if isinstance(tstop_data, dict):
            # Get latest date tickers
            dates = sorted(tstop_data.keys(), reverse=True)
            for date in dates[:5]:
                if tstop_data.get(date):
                    for t in tstop_data[date] if isinstance(tstop_data[date], list) else []:
                        ticker = t.replace('-USD', '').upper()
                        tstop_tickers.add(ticker)
                    if tstop_tickers:
                        break

        candidates = []
        for _, row in df.iterrows():
            ticker = str(row['ticker']).upper()
            momentum = safe_float(row.get('momentum', 0))
            bull_ratio = safe_float(row.get('bull_ratio', 0))
            combined_score = safe_float(row.get('combined_score', 0))

            in_green = ticker in green_tickers
            in_tstop = ticker in tstop_tickers

            stage_name, priority_level = get_stage_from_signals(momentum, bull_ratio, in_green, in_tstop)
            score = int(combined_score * 100)

            # Get strategy recommendation
            if row.get('tier') == 'Tier 1':
                strategy = "Bull Quiet"
            elif row.get('tier') == 'Tier 2':
                strategy = "Transition"
            elif momentum > 0:
                strategy = "Ranging"
            else:
                strategy = "-"

            # Get price info
            price_info = get_ticker_price_info(ticker) if HAS_PRICE_DATA else {}

            candidates.append({
                'ticker': ticker,
                'company': row.get('company', row.get('name', '')),
                'score': score,
                'stage': stage_name,
                'priority': priority_level,
                'strategy': strategy,
                'themes': row.get('category', row.get('theme', '')),
                'momentum': momentum,
                'fiedler': safe_float(row.get('fiedler', 0)),
                'tier': row.get('tier', 'Tier 4'),
                'in_green': in_green,
                'in_tstop': in_tstop,
                'close': price_info.get('close', 0),
            })

        # Apply filters
        if stage:
            candidates = [c for c in candidates if stage.lower() in c['stage'].lower()]
        if priority:
            candidates = [c for c in candidates if c['priority'].upper() == priority.upper()]
        if min_score:
            candidates = [c for c in candidates if c['score'] >= min_score]
        if theme:
            candidates = [c for c in candidates if theme.lower() in str(c['themes']).lower()]

        # Sort by score
        candidates = sorted(candidates, key=lambda x: x['score'], reverse=True)[:limit]

        # Calculate stage distribution
        stage_counts = {}
        for c in candidates:
            stage_counts[c['stage']] = stage_counts.get(c['stage'], 0) + 1

        return {
            "candidates": candidates,
            "count": len(candidates),
            "total_available": len(df),
            "stage_distribution": stage_counts,
            "filters_applied": {
                "stage": stage,
                "min_score": min_score,
                "priority": priority,
                "theme": theme
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stages")
async def get_stage_distribution() -> Dict[str, Any]:
    """Get stage distribution for charts"""
    try:
        df = load_actionable_tickers()

        # Get SuperTrend count from BB crossovers
        bb_crossovers = compute_bb_crossovers(limit=100)
        supertrend_count = len(bb_crossovers)

        # Load filter data
        green_data = load_filter_data("lrs_green_cross_strategy")
        green_tickers = get_green_tickers_for_date(green_data)

        stages = {}
        priorities = {}

        for _, row in df.iterrows():
            ticker = str(row['ticker']).upper()
            momentum = safe_float(row.get('momentum', 0))
            bull_ratio = safe_float(row.get('bull_ratio', 0))
            in_green = ticker in green_tickers

            stage_name, priority_level = get_stage_from_signals(momentum, bull_ratio, in_green)

            stages[stage_name] = stages.get(stage_name, 0) + 1
            priorities[priority_level] = priorities.get(priority_level, 0) + 1

        # Add SuperTrend from BB crossovers
        stages["Super Trend"] = supertrend_count
        if supertrend_count > 0:
            priorities["HIGH"] = priorities.get("HIGH", 0) + supertrend_count

        return {
            "stages": [{"name": k, "count": v} for k, v in sorted(stages.items(), key=lambda x: -x[1])],
            "priorities": [{"name": k, "count": v} for k, v in priorities.items()],
            "total": len(df)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary-cards")
async def get_summary_cards() -> Dict[str, Any]:
    """Get summary card counts for dashboard"""
    try:
        df = load_actionable_tickers()
        consolidated = load_consolidated()

        # Get SuperTrend/Long Term Trend count from BB crossovers
        bb_crossovers = compute_bb_crossovers(limit=100)
        supertrend_count = len(bb_crossovers)

        # Load filter data
        green_data = load_filter_data("lrs_green_cross_strategy")
        green_tickers = get_green_tickers_for_date(green_data)

        early_breakout_count = 0
        high_priority_count = 0

        for _, row in df.iterrows():
            ticker = str(row['ticker']).upper()
            momentum = safe_float(row.get('momentum', 0))
            bull_ratio = safe_float(row.get('bull_ratio', 0))
            in_green = ticker in green_tickers

            stage_name, priority_level = get_stage_from_signals(momentum, bull_ratio, in_green)

            if stage_name == "Early Breakout":
                early_breakout_count += 1
            if priority_level == "HIGH":
                high_priority_count += 1

        # Get date from consolidated analysis
        data_date = consolidated.get('generated_at', datetime.now().strftime('%Y-%m-%d'))

        return {
            "supertrend": supertrend_count,
            "early_breakout": early_breakout_count,
            "high_priority": high_priority_count,
            "long_term_trend": supertrend_count,  # Same as supertrend for crypto (BB crossover)
            "total": 228,  # Total CoinGecko categories
            "date": data_date
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/expected-returns")
async def get_expected_returns() -> Dict[str, Any]:
    """Get historical expected returns by stage - Crypto market data"""
    # Pre-computed from crypto backtest results (higher volatility)
    returns_data = {
        "stages": [
            {"stage": "Super Trend", "return_20d": 12.5, "win_rate": 45.0, "sample_size": 120, "recommendation": "BUY"},
            {"stage": "Early Breakout", "return_20d": 8.5, "win_rate": 42.0, "sample_size": 250, "recommendation": "BUY"},
            {"stage": "Burgeoning", "return_20d": 4.2, "win_rate": 38.0, "sample_size": 380, "recommendation": "HOLD"},
            {"stage": "Building", "return_20d": 1.8, "win_rate": 35.0, "sample_size": 520, "recommendation": "HOLD"},
            {"stage": "Consolidation", "return_20d": 0.5, "win_rate": 32.0, "sample_size": 650, "recommendation": "WATCH"},
            {"stage": "Bear Volatile", "return_20d": -8.5, "win_rate": 25.0, "sample_size": 180, "recommendation": "AVOID"}
        ],
        "source": "Crypto Backtest 2023-01 to 2026-01"
    }
    return returns_data


@router.get("/daily-summary")
async def get_daily_summary(
    date: Optional[str] = Query(None, description="Date (YYYY-MM-DD)")
) -> Dict[str, Any]:
    """Get daily summary - uses actionable tickers for crypto"""
    try:
        df = load_actionable_tickers()
        consolidated = load_consolidated()

        # Get top 10 by combined score
        top_df = df.nlargest(10, 'combined_score')

        top_performers = []
        for idx, row in top_df.iterrows():
            ticker = str(row['ticker']).replace('-USD', '').upper()
            price_info = get_ticker_price_info(ticker) if HAS_PRICE_DATA else {}

            top_performers.append({
                "rank": len(top_performers) + 1,
                "ticker": row['ticker'],
                "name": row.get('company', row.get('name', '')),
                "category": row.get('category', row.get('theme', '')),
                "composite_score": safe_float(row.get('combined_score', 0)),
                "regime_type": row.get('tier', ''),
                "signals": {
                    "momentum": safe_float(row.get('momentum', 0)),
                    "fiedler": safe_float(row.get('fiedler', 0)),
                    "bull_ratio": safe_float(row.get('bull_ratio', 0))
                },
                "in_green": False,
                "in_tstop": False,
                "close": price_info.get('close', 0)
            })

        return {
            "date": consolidated.get('generated_at', datetime.now().strftime('%Y-%m-%d')),
            "generated_at": consolidated.get('generated_at', ''),
            "total_tickers": len(df),
            "top_performers": top_performers,
            "note": "Crypto Sector Rotation - Top 10 by Combined Score"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/top-picks")
async def get_top_picks(limit: int = 10) -> Dict[str, Any]:
    """Get top breakout picks with strategy recommendations"""
    try:
        df = load_actionable_tickers()

        # Filter for positive momentum and sort
        df_positive = df[df['momentum'] > 0]
        if len(df_positive) < limit:
            df_positive = df.nlargest(limit, 'combined_score')
        else:
            df_positive = df_positive.nlargest(limit, 'combined_score')

        picks = []
        for _, row in df_positive.iterrows():
            momentum = safe_float(row.get('momentum', 0))

            # Determine strategy
            if row['tier'] == 'Tier 1':
                strategy = "Aggressive - Full position"
            elif row['tier'] == 'Tier 2':
                strategy = "Accumulate - Build position"
            elif momentum > 0.05:
                strategy = "Tactical - Small position"
            else:
                strategy = "Watch - Wait for confirmation"

            picks.append({
                'ticker': row['ticker'],
                'company': row.get('company', row.get('name', '')),
                'theme': row.get('category', row.get('theme', '')),
                'tier': row['tier'],
                'score': safe_float(row['combined_score']),
                'momentum': momentum,
                'strategy': strategy,
            })

        return {
            "picks": picks,
            "count": len(picks),
            "generated_at": load_consolidated().get('generated_at', ''),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/supertrend-candidates")
async def get_supertrend_candidates(
    date: Optional[str] = Query(None, description="Date (YYYY-MM-DD)"),
    limit: int = Query(50, description="Max results")
) -> Dict[str, Any]:
    """
    Get SuperTrend candidates - tickers where price is above BB(220, 2.0) upper band.
    Computes BB crossovers from actual price data.
    """
    try:
        # Compute BB crossovers from price data
        bb_crossovers = compute_bb_crossovers(limit=limit * 2)  # Get more to filter

        if not bb_crossovers:
            return {
                "candidates": [],
                "count": 0,
                "total_available": 0,
                "date": datetime.now().strftime('%Y-%m-%d'),
                "parameters": {"bb_period": 220, "bb_multiplier": 2.0},
                "note": "No tickers currently above upper Bollinger Band (220, 2.0)"
            }

        # Load actionable tickers for enrichment
        try:
            df = load_actionable_tickers()
            ticker_data = {}
            for _, row in df.iterrows():
                # Index by both formats
                ticker_data[row['ticker']] = row.to_dict()
                ticker_clean = row.get('ticker_clean', row['ticker'].replace('-USD', ''))
                ticker_data[ticker_clean] = row.to_dict()
        except:
            ticker_data = {}

        # Load category mapping
        category_map = get_category_mapping()

        # Load filter data for green/tstop status
        green_data = load_filter_data("lrs_green_cross_strategy")
        green_tickers = get_green_tickers_for_date(green_data)

        tstop_tickers = set()

        candidates = []
        for bb_item in bb_crossovers[:limit]:
            ticker = bb_item['ticker']
            ticker_with_suffix = f"{ticker}-USD"

            # Get enrichment data
            enrich = ticker_data.get(ticker, ticker_data.get(ticker_with_suffix, {}))
            momentum = safe_float(enrich.get('momentum', 0))
            combined_score = safe_float(enrich.get('combined_score', 0))

            in_green = ticker in green_tickers
            in_tstop = ticker in tstop_tickers

            tier = enrich.get('tier', '')
            if tier == 'Tier 1':
                strategy = "Bull Quiet"
            elif tier == 'Tier 2':
                strategy = "Transition"
            elif momentum > 0:
                strategy = "Ranging"
            else:
                strategy = "Breakout"

            # Score based on deviation from BB upper (higher = stronger breakout)
            deviation = bb_item['deviation_pct']
            score = int(min(deviation * 5, 100))  # Scale deviation to 0-100

            category = category_map.get(ticker, '') or enrich.get('category', enrich.get('theme', ''))

            candidates.append({
                'ticker': ticker,
                'score': score,
                'stage': "Super Trend",
                'priority': "HIGH",
                'strategy': strategy,
                'category': category,
                'deviation': round(deviation, 2),
                'close': bb_item['close'],
                'bb_upper': bb_item['bb_upper'],
                'change_pct': bb_item['change_pct'],
                'last_date': bb_item.get('last_date', ''),
                'in_green': in_green,
                'in_tstop': in_tstop,
            })

        # Already sorted by deviation in compute_bb_crossovers

        return {
            "candidates": candidates,
            "count": len(candidates),
            "total_available": len(bb_crossovers),
            "date": datetime.now().strftime('%Y-%m-%d'),
            "parameters": {"bb_period": 220, "bb_multiplier": 2.0},
            "note": "Tickers crossing above upper Bollinger Band (220, 2.0)"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/by-theme/{theme_name}")
async def get_candidates_by_theme(theme_name: str, limit: int = 20) -> Dict[str, Any]:
    """Get candidates for a specific category/theme"""
    try:
        df = load_actionable_tickers()
        consolidated = load_consolidated()

        # Check for category column (crypto) or theme column
        theme_col = 'category' if 'category' in df.columns else 'theme'

        # Filter by theme/category
        df_filtered = df[df[theme_col].str.lower() == theme_name.lower()]
        if df_filtered.empty:
            # Try partial match
            df_filtered = df[df[theme_col].str.lower().str.contains(theme_name.lower(), na=False)]

        if df_filtered.empty:
            raise HTTPException(status_code=404, detail=f"Category '{theme_name}' not found")

        # Sort by weight or score
        sort_col = 'weight_in_theme' if 'weight_in_theme' in df_filtered.columns else 'combined_score'
        df_filtered = df_filtered.sort_values(sort_col, ascending=False).head(limit)

        # Get theme info
        themes_data = consolidated.get('themes', consolidated.get('categories', {}))
        theme_info = themes_data.get(theme_name, {})

        candidates = []
        for _, row in df_filtered.iterrows():
            candidates.append({
                'ticker': row['ticker'],
                'company': row.get('company', row.get('name', '')),
                'weight': safe_float(row.get('weight_in_theme', row.get('combined_score', 0))),
                'action': row.get('action', row.get('tier', '')),
            })

        return {
            'theme': theme_name,
            'tier': theme_info.get('tier', 'Unknown'),
            'combined_score': safe_float(theme_info.get('combined_score', 0)),
            'momentum': safe_float(theme_info.get('momentum', 0)),
            'fiedler': safe_float(theme_info.get('fiedler', 0)),
            'candidates': candidates,
            'count': len(candidates),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
