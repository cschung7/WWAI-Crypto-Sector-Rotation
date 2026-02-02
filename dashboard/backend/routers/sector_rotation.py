"""
Sector Rotation Overview API Router
"""

from fastapi import APIRouter, HTTPException
from pathlib import Path
import pandas as pd
import json
from datetime import datetime
from typing import List, Dict, Any
import math

router = APIRouter()

# Data directory
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
SECTOR_LEADERS_RESULTS = Path("/mnt/nas/WWAI/Sector-Rotation/Sector-Leaders-Crypto/results")


def safe_float(value) -> float:
    """Convert to float, return 0 if NaN/None"""
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return 0.0
    return float(value)


def load_latest_consolidated() -> Dict:
    """Load the latest consolidated analysis JSON"""
    files = sorted(DATA_DIR.glob("consolidated_ticker_analysis_*.json"), reverse=True)
    if not files:
        raise HTTPException(status_code=404, detail="No consolidated analysis found")

    with open(files[0]) as f:
        return json.load(f)


def load_latest_rankings() -> pd.DataFrame:
    """Load the latest rankings CSV"""
    files = sorted(SECTOR_LEADERS_RESULTS.glob("combined_score_ranking_*.csv"), reverse=True)
    if not files:
        raise HTTPException(status_code=404, detail="No rankings data found")

    return pd.read_csv(files[0])


@router.get("/summary")
async def get_summary() -> Dict[str, Any]:
    """Get market summary with key metrics"""
    try:
        data = load_latest_consolidated()
        rankings = load_latest_rankings()

        # Calculate overall market sentiment
        avg_momentum = rankings['momentum'].mean()
        avg_bull_ratio = rankings['bull_ratio'].mean()

        if avg_momentum > 0.05 and avg_bull_ratio > 0.3:
            sentiment = "Bullish"
        elif avg_momentum < -0.02 or avg_bull_ratio < 0.1:
            sentiment = "Bearish"
        else:
            sentiment = "Neutral"

        # Support both 'statistics' and 'summary' keys
        stats = data.get('statistics', data.get('summary', {}))
        metadata = data.get('metadata', {})
        total_categories = metadata.get('total_categories', stats.get('total_themes', 0))

        return {
            "date": metadata.get("generated", datetime.now().isoformat()),
            "regime": sentiment,
            "sentiment": sentiment,
            "total_themes": total_categories,
            "total_tickers": metadata.get('total_tickers', 0),
            "tier1_count": stats.get('tier1_count', 0),
            "tier2_count": stats.get('tier2_count', 0),
            "tier3_count": stats.get('tier3_count', 0),
            "tier4_count": stats.get('tier4_count', 0),
            "avg_momentum": safe_float(stats.get('avg_momentum', avg_momentum)),
            "avg_bull_ratio": safe_float(avg_bull_ratio),
            "avg_fiedler": safe_float(stats.get('avg_fiedler', 0)),
            "signal_quality": min(100, int((stats.get('tier1_count', 0) + stats.get('tier2_count', 0)) / max(1, total_categories) * 100)),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/top-picks")
async def get_top_picks(limit: int = 10) -> List[Dict]:
    """Get top stock picks across all themes"""
    try:
        data = load_latest_consolidated()
        picks = data.get('top_picks', [])[:limit]

        return [{
            'ticker': p.get('ticker_clean', p.get('ticker', '')),
            'company': p.get('company', p.get('ticker_clean', '')),
            'theme': p.get('theme', ''),
            'tier': p.get('tier', 'Tier 1'),
            'score': safe_float(p.get('combined_score', 0)),
            'momentum': safe_float(p.get('momentum', 0)),
            'fiedler': safe_float(p.get('fiedler', 0)),
        } for p in picks]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/theme-health")
async def get_theme_health() -> List[Dict]:
    """Get theme health status for all themes"""
    try:
        data = load_latest_consolidated()

        # Support both dict format (themes) and array format (categories)
        themes_data = data.get('themes', {})
        categories_data = data.get('categories', [])

        health = []

        # Handle dict format
        if themes_data:
            for theme, info in themes_data.items():
                fiedler = safe_float(info.get('fiedler', 0))

                if fiedler >= 3.0:
                    level = "Very Strong"
                elif fiedler >= 1.5:
                    level = "Strong"
                elif fiedler >= 0.5:
                    level = "Moderate"
                else:
                    level = "Weak"

                health.append({
                    'theme': theme,
                    'tier': info.get('tier', 'Tier 4'),
                    'fiedler': fiedler,
                    'level': level,
                    'momentum': safe_float(info.get('momentum', 0)),
                    'bull_ratio': safe_float(info.get('bull_ratio', 0)),
                    'gics_sector': info.get('gics_sector', info.get('sector', 'Other')),
                })

        # Handle array format (crypto categories)
        elif categories_data:
            for info in categories_data:
                fiedler = safe_float(info.get('fiedler', 0))

                if fiedler >= 3.0:
                    level = "Very Strong"
                elif fiedler >= 1.5:
                    level = "Strong"
                elif fiedler >= 0.5:
                    level = "Moderate"
                else:
                    level = "Weak"

                health.append({
                    'theme': info.get('theme', ''),
                    'tier': info.get('tier', 'Tier 4'),
                    'fiedler': fiedler,
                    'level': level,
                    'momentum': safe_float(info.get('momentum', 0)),
                    'bull_ratio': safe_float(info.get('bull_ratio', 0)),
                    'gics_sector': info.get('sector', 'Other'),
                })

        # Sort by tier then by fiedler
        tier_order = {'Tier 1': 0, 'Tier 2': 1, 'Tier 3': 2, 'Tier 4': 3}
        health.sort(key=lambda x: (tier_order.get(x['tier'], 4), -x['fiedler']))

        return health
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/themes")
async def get_all_themes() -> Dict[str, Any]:
    """Get detailed information for all themes"""
    try:
        data = load_latest_consolidated()
        return {
            "themes": data.get('themes', {}),
            "gics_summary": data.get('gics_summary', {}),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/theme/{theme_name}")
async def get_theme_detail(theme_name: str) -> Dict:
    """Get detailed information for a specific theme"""
    try:
        data = load_latest_consolidated()
        themes = data.get('themes', {})

        # Try exact match first
        if theme_name in themes:
            return themes[theme_name]

        # Try case-insensitive match
        for theme, info in themes.items():
            if theme.lower() == theme_name.lower():
                return info

        raise HTTPException(status_code=404, detail=f"Theme '{theme_name}' not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/gics-sectors")
async def get_gics_sectors() -> Dict[str, Any]:
    """Get GICS sector summary"""
    try:
        data = load_latest_consolidated()
        return data.get('gics_summary', {})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
