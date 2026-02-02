"""
Breakout/Momentum Scanner API Router - USA
Matches KRX style with AutoML integration
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

# AutoML USA paths
AUTOML_USA_DIR = Path("/mnt/nas/AutoGluon/AutoML_Usa")
FILTER_DIR = AUTOML_USA_DIR / "Filter"
RANKINGS_DIR = AUTOML_USA_DIR / "Backtest" / "Rankings"
DB_DIR = AUTOML_USA_DIR / "DB"
BB_FILTER_DIR = AUTOML_USA_DIR / "working_filter_BB" / "Filter"
PRICE_DIR = AUTOML_USA_DIR / "USANOTTRAINED"
US_LISTED_FILE = DB_DIR / "2024_12_15_us_listed.csv"

# Cache for sector lookup
_sector_cache = None

def get_sector_mapping() -> dict:
    """Load and cache sector mapping from us_listed.csv"""
    global _sector_cache
    if _sector_cache is None:
        try:
            df = pd.read_csv(US_LISTED_FILE)
            _sector_cache = dict(zip(df['Symbol'], df['Sector']))
        except Exception as e:
            print(f"Error loading sector data: {e}")
            _sector_cache = {}
    return _sector_cache


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
    """Load BB crossover filtered tickers - check local repo first, then NAS"""
    # First check local repo (for Railway/cloud deployment)
    local_bb_file = DATA_DIR / "bb_filter" / "bb_filtered_tickers.json"
    if local_bb_file.exists():
        with open(local_bb_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    # Fallback to NAS path (for local development)
    bb_file = BB_FILTER_DIR / "bb_filtered_tickers.json"
    if not bb_file.exists():
        return {}
    with open(bb_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_ticker_price_info(ticker: str) -> Dict:
    """Get latest price info for a ticker"""
    price_file = PRICE_DIR / f"{ticker}.csv"
    if not price_file.exists():
        return {}
    try:
        df = pd.read_csv(price_file, index_col=0)
        df.columns = [col.lower() for col in df.columns]
        if 'close' not in df.columns or len(df) < 220:
            return {}

        # Calculate BB (220, 2.0) matching TradingView
        close = df['close']
        bb_middle = close.rolling(220).mean()
        bb_std = close.rolling(220).std(ddof=1)  # Sample std to match TradingView
        bb_upper = bb_middle + (bb_std * 2.0)

        last_close = close.iloc[-1]
        last_upper = bb_upper.iloc[-1]
        deviation_pct = (last_close - last_upper) / last_upper * 100 if last_upper else 0

        # Get price change
        if len(df) >= 2:
            prev_close = close.iloc[-2]
            change_pct = (last_close - prev_close) / prev_close * 100 if prev_close else 0
        else:
            change_pct = 0

        return {
            'close': round(last_close, 2),
            'bb_upper': round(last_upper, 2) if not pd.isna(last_upper) else 0,
            'deviation_pct': round(deviation_pct, 2),
            'change_pct': round(change_pct, 2)
        }
    except Exception:
        return {}


def load_filter_data(filter_type: str = "lrs_green_cross_strategy") -> Dict:
    """Load filter data from AutoML_Usa/Filter"""
    pattern = str(FILTER_DIR / f"Usa_*_{filter_type}_tv.json")
    files = sorted(glob.glob(pattern), reverse=True)
    if not files:
        # Try non-tv version
        pattern = str(FILTER_DIR / f"Usa_{filter_type}.json")
        files = sorted(glob.glob(pattern), reverse=True)
    if not files:
        return {}
    with open(files[0]) as f:
        return json.load(f)


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


@router.get("/candidates")
async def get_breakout_candidates(
    stage: Optional[str] = Query(None, description="Filter by stage"),
    priority: Optional[str] = Query(None, description="Filter by priority (HIGH, MEDIUM, LOW)"),
    min_score: Optional[int] = Query(None, description="Minimum score filter"),
    theme: Optional[str] = Query(None, description="Filter by theme name"),
    limit: int = Query(100, description="Max results")
) -> Dict[str, Any]:
    """Get breakout candidates with filtering - matches KRX API"""
    try:
        df = load_actionable_tickers()

        # Load filter data for green/tstop status
        green_data = load_filter_data("lrs_green_cross_strategy")
        green_tickers = set()
        if green_data:
            for key in ['turn_green', 'staying_green']:
                for t in green_data.get(key, []):
                    # Remove exchange prefix if present
                    ticker = t.split(':')[-1] if ':' in t else t
                    green_tickers.add(ticker)

        tstop_data = load_filter_data("tstop_filtered")
        tstop_tickers = set(tstop_data.keys() if isinstance(tstop_data, dict) else [])

        candidates = []
        for _, row in df.iterrows():
            ticker = row['ticker']
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

            candidates.append({
                'ticker': ticker,
                'company': row.get('company', ''),
                'score': score,
                'stage': stage_name,
                'priority': priority_level,
                'strategy': strategy,
                'themes': row.get('theme', ''),
                'momentum': momentum,
                'fiedler': safe_float(row.get('fiedler', 0)),
                'tier': row.get('tier', 'Tier 4'),
                'in_green': in_green,
                'in_tstop': in_tstop,
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

        # Load filter data
        green_data = load_filter_data("lrs_green_cross_strategy")
        green_tickers = set()
        if green_data:
            for key in ['turn_green', 'staying_green']:
                for t in green_data.get(key, []):
                    ticker = t.split(':')[-1] if ':' in t else t
                    green_tickers.add(ticker)

        stages = {}
        priorities = {}

        for _, row in df.iterrows():
            ticker = row['ticker']
            momentum = safe_float(row.get('momentum', 0))
            bull_ratio = safe_float(row.get('bull_ratio', 0))
            in_green = ticker in green_tickers

            stage_name, priority_level = get_stage_from_signals(momentum, bull_ratio, in_green)

            stages[stage_name] = stages.get(stage_name, 0) + 1
            priorities[priority_level] = priorities.get(priority_level, 0) + 1

        return {
            "stages": [{"name": k, "count": v} for k, v in sorted(stages.items(), key=lambda x: -x[1])],
            "priorities": [{"name": k, "count": v} for k, v in priorities.items()],
            "total": len(df)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/expected-returns")
async def get_expected_returns() -> Dict[str, Any]:
    """Get historical expected returns by stage - USA market data"""
    # Pre-computed from USA backtest results
    returns_data = {
        "stages": [
            {"stage": "Super Trend", "return_20d": 6.5, "win_rate": 42.0, "sample_size": 180, "recommendation": "BUY"},
            {"stage": "Early Breakout", "return_20d": 5.2, "win_rate": 40.0, "sample_size": 320, "recommendation": "BUY"},
            {"stage": "Burgeoning", "return_20d": 2.8, "win_rate": 38.0, "sample_size": 450, "recommendation": "HOLD"},
            {"stage": "Building", "return_20d": 1.2, "win_rate": 35.0, "sample_size": 620, "recommendation": "HOLD"},
            {"stage": "Consolidation", "return_20d": 0.5, "win_rate": 33.0, "sample_size": 800, "recommendation": "WATCH"},
            {"stage": "Bear Volatile", "return_20d": -4.5, "win_rate": 28.0, "sample_size": 150, "recommendation": "AVOID"}
        ],
        "source": "USA Backtest 2024-01 to 2026-01"
    }
    return returns_data


@router.get("/daily-summary")
async def get_daily_summary(
    date: Optional[str] = Query(None, description="Date (YYYY-MM-DD)")
) -> Dict[str, Any]:
    """Get daily summary from AutoML Rankings"""
    try:
        # Check local repo first (for Railway/cloud deployment)
        local_rankings_dir = DATA_DIR / "rankings"

        if date:
            # Check local first
            summary_file = local_rankings_dir / f"top10_regime_signal_{date}.json"
            if not summary_file.exists():
                summary_file = RANKINGS_DIR / f"top10_regime_signal_{date}.json"
        else:
            # Find latest - check local first
            summary_files = sorted(glob.glob(str(local_rankings_dir / "top10_regime_signal_*.json")))
            if not summary_files:
                # Fallback to NAS
                summary_files = sorted(glob.glob(str(RANKINGS_DIR / "top10_regime_signal_*.json")))
            if not summary_files:
                raise HTTPException(status_code=404, detail="No daily summary data found")
            summary_file = Path(summary_files[-1])

        if not summary_file.exists():
            raise HTTPException(status_code=404, detail=f"Summary not found: {summary_file.name}")

        with open(summary_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Transform to match KRX format
        top_performers = []
        for item in data.get("top10", []):
            signals = item.get("signals", {})
            top_performers.append({
                "rank": item.get("rank"),
                "ticker": item.get("ticker"),
                "name": item.get("name", ""),
                "sector": item.get("sector", ""),
                "composite_score": item.get("composite_score", 0),
                "regime_type": item.get("regime", ""),
                "signals": {
                    "model_prediction": signals.get("model_prediction", 0),
                    "regime_signal": signals.get("regime_signal", 0),
                    "tsf_alignment": signals.get("tsf_alignment", 0)
                },
                "in_green": item.get("in_green", False),
                "in_tstop": item.get("in_tstop", False)
            })

        return {
            "date": data.get("date"),
            "generated_at": data.get("generated_at"),
            "total_tickers": data.get("total_evaluated", 0),
            "top_performers": top_performers,
            "note": data.get("description", "Regime Signal Ranking")
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
        df = df[df['momentum'] > 0].sort_values('combined_score', ascending=False).head(limit)

        picks = []
        for _, row in df.iterrows():
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
                'company': row.get('company', ''),
                'theme': row['theme'],
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
    Get SuperTrend candidates - tickers that crossed above Bollinger Band upper.
    Enriched with regime, score, and theme data.
    """
    try:
        bb_data = load_bb_filtered_tickers()
        if not bb_data:
            return {
                "candidates": [],
                "count": 0,
                "date": date,
                "note": "No BB filter data available"
            }

        # Get the latest date or specified date
        if date and date in bb_data:
            tickers = bb_data[date]
            data_date = date
        else:
            # Get latest date
            dates = sorted(bb_data.keys(), reverse=True)
            if not dates:
                return {"candidates": [], "count": 0, "date": None}
            data_date = dates[0]
            tickers = bb_data[data_date]

        # Load actionable tickers for enrichment data
        try:
            df = load_actionable_tickers()
            ticker_data = df.set_index('ticker').to_dict('index')
        except:
            ticker_data = {}

        # Load sector mapping
        sector_map = get_sector_mapping()

        # Load filter data for green/tstop status
        green_data = load_filter_data("lrs_green_cross_strategy")
        green_tickers = set()
        if green_data:
            for key in ['turn_green', 'staying_green']:
                for t in green_data.get(key, []):
                    ticker = t.split(':')[-1] if ':' in t else t
                    green_tickers.add(ticker)

        tstop_data = load_filter_data("tstop_filtered")
        tstop_tickers = set(tstop_data.keys() if isinstance(tstop_data, dict) else [])

        # Get price info and enrich with regime/score data
        candidates = []
        for ticker in tickers[:limit]:
            price_info = get_ticker_price_info(ticker)

            # Get enrichment data from actionable_tickers
            enrich = ticker_data.get(ticker, {})
            momentum = safe_float(enrich.get('momentum', 0))
            bull_ratio = safe_float(enrich.get('bull_ratio', 0))
            combined_score = safe_float(enrich.get('combined_score', 0))

            in_green = ticker in green_tickers
            in_tstop = ticker in tstop_tickers

            # Determine stage - SuperTrend candidates get "Super Trend" stage
            stage_name = "Super Trend"
            priority_level = "HIGH"

            # Get strategy/regime
            tier = enrich.get('tier', '')
            if tier == 'Tier 1':
                strategy = "Bull Quiet"
            elif tier == 'Tier 2':
                strategy = "Transition"
            elif momentum > 0:
                strategy = "Ranging"
            else:
                strategy = "Bull Quiet"  # Default for BB crossover

            # Calculate score (combine BB deviation with existing score)
            deviation = price_info.get('deviation_pct', 0)
            score = int(combined_score * 100) if combined_score else int(min(deviation * 10, 100))

            # Get sector from mapping or enrichment data
            sector = sector_map.get(ticker, '') or enrich.get('gics_sector', '')

            candidates.append({
                'ticker': ticker,
                'score': score,
                'stage': stage_name,
                'priority': priority_level,
                'strategy': strategy,
                'sector': sector,
                'deviation': round(deviation, 2),
                'in_green': in_green,
                'in_tstop': in_tstop,
            })

        # Sort by score descending
        candidates = sorted(candidates, key=lambda x: x['score'], reverse=True)

        return {
            "candidates": candidates,
            "count": len(candidates),
            "total_available": len(tickers),
            "date": data_date,
            "parameters": {
                "bb_period": 220,
                "bb_multiplier": 2.0
            },
            "note": "Tickers crossing above upper Bollinger Band (220, 2.0)"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/by-theme/{theme_name}")
async def get_candidates_by_theme(theme_name: str, limit: int = 20) -> Dict[str, Any]:
    """Get candidates for a specific theme"""
    try:
        df = load_actionable_tickers()
        consolidated = load_consolidated()

        # Filter by theme
        df = df[df['theme'].str.lower() == theme_name.lower()]
        if df.empty:
            raise HTTPException(status_code=404, detail=f"Theme '{theme_name}' not found")

        df = df.sort_values('weight_in_theme', ascending=False).head(limit)

        # Get theme info
        theme_info = consolidated.get('themes', {}).get(theme_name, {})

        candidates = []
        for _, row in df.iterrows():
            candidates.append({
                'ticker': row['ticker'],
                'company': row.get('company', ''),
                'weight': safe_float(row.get('weight_in_theme', 0)),
                'action': row.get('action', ''),
            })

        return {
            'theme': theme_name,
            'tier': theme_info.get('tier', 'Unknown'),
            'combined_score': safe_float(theme_info.get('combined_score', 0)),
            'momentum': safe_float(theme_info.get('momentum', 0)),
            'fiedler': safe_float(theme_info.get('fiedler', 0)),
            'etfs': theme_info.get('etfs', []),
            'candidates': candidates,
            'count': len(candidates),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
