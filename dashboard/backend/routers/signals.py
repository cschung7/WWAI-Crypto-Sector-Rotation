"""
Crypto Sector Rotation Dashboard - Signals Router
Signal quality analysis and filtering endpoints
"""

from fastapi import APIRouter, HTTPException
from typing import Optional, List
import pandas as pd
import json
from pathlib import Path
from datetime import datetime

router = APIRouter()

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"


def get_latest_data():
    """Load the latest actionable tickers data"""
    files = sorted(DATA_DIR.glob("actionable_tickers_*.csv"), reverse=True)
    if not files:
        raise HTTPException(status_code=404, detail="No data files found")
    return pd.read_csv(files[0])


def get_latest_consolidated():
    """Load the latest consolidated analysis"""
    files = sorted(DATA_DIR.glob("consolidated_ticker_analysis_*.json"), reverse=True)
    if not files:
        raise HTTPException(status_code=404, detail="No consolidated data found")
    with open(files[0]) as f:
        return json.load(f)


@router.get("/quality")
async def signal_quality():
    """Get overall signal quality metrics"""
    try:
        df = get_latest_data()
        consolidated = get_latest_consolidated()

        total = len(df)
        unique_tickers = df['ticker'].nunique()

        # Tier distribution
        tier_dist = df.groupby('tier').size().to_dict()

        # Quality score: proportion of high-quality signals (TIER 1-2)
        high_quality = len(df[df['tier'].isin(['Tier 1', 'Tier 2'])])
        quality_score = (high_quality / total * 100) if total > 0 else 0

        # Momentum strength
        avg_momentum = df['momentum'].mean() * 100
        positive_momentum = len(df[df['momentum'] > 0])
        momentum_ratio = (positive_momentum / total * 100) if total > 0 else 0

        # Cohesion strength
        avg_fiedler = df['fiedler'].mean()
        strong_cohesion = len(df[df['fiedler'] >= 1.5])
        cohesion_ratio = (strong_cohesion / total * 100) if total > 0 else 0

        return {
            "total_signals": total,
            "unique_tickers": unique_tickers,
            "quality_score": round(quality_score, 1),
            "tier_distribution": tier_dist,
            "momentum": {
                "average_pct": round(avg_momentum, 2),
                "positive_count": positive_momentum,
                "positive_ratio": round(momentum_ratio, 1)
            },
            "cohesion": {
                "average_fiedler": round(avg_fiedler, 2),
                "strong_count": strong_cohesion,
                "strong_ratio": round(cohesion_ratio, 1)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/filter-funnel")
async def filter_funnel():
    """Get signal filtering funnel - from all signals to actionable"""
    try:
        df = get_latest_data()
        consolidated = get_latest_consolidated()

        total_themes = len(consolidated.get('themes', {}))
        total_signals = len(df)

        # Filter stages
        stages = [
            {
                "stage": "All Themes",
                "count": total_themes,
                "description": "Total themes in analysis"
            },
            {
                "stage": "Theme Signals",
                "count": total_signals,
                "description": "Theme-ticker combinations with data"
            },
            {
                "stage": "Momentum Pass",
                "count": len(df[df['momentum'] > 0]),
                "description": "Positive momentum signals"
            },
            {
                "stage": "Cohesion Pass",
                "count": len(df[df['fiedler'] >= 0.5]),
                "description": "Moderate+ cohesion signals"
            },
            {
                "stage": "TIER 1-3",
                "count": len(df[df['tier'].isin(['Tier 1', 'Tier 2', 'Tier 3'])]),
                "description": "Actionable signals (TIER 1-3)"
            },
            {
                "stage": "TIER 1-2",
                "count": len(df[df['tier'].isin(['Tier 1', 'Tier 2'])]),
                "description": "High conviction signals"
            },
            {
                "stage": "TIER 1",
                "count": len(df[df['tier'] == 'Tier 1']),
                "description": "Aggressive buy signals"
            }
        ]

        return {"funnel": stages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/momentum-cohesion")
async def momentum_vs_cohesion():
    """Get momentum vs cohesion scatter plot data"""
    try:
        df = get_latest_data()

        # Get unique theme-level data
        theme_data = df.groupby('theme').agg({
            'momentum': 'first',
            'fiedler': 'first',
            'tier': 'first',
            'combined_score': 'first',
            'bull_ratio': 'first'
        }).reset_index()

        result = []
        for _, row in theme_data.iterrows():
            result.append({
                "theme": row['theme'],
                "momentum": round(row['momentum'] * 100, 2),
                "fiedler": round(row['fiedler'], 2),
                "tier": row['tier'],
                "score": round(row['combined_score'], 4),
                "bull_ratio": round(row['bull_ratio'] * 100, 1)
            })

        return {"data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tier-breakdown")
async def tier_breakdown():
    """Get detailed TIER breakdown with theme info"""
    try:
        df = get_latest_data()
        consolidated = get_latest_consolidated()

        breakdown = {}
        for tier in ['Tier 1', 'Tier 2', 'Tier 3', 'Tier 4']:
            tier_df = df[df['tier'] == tier]
            themes = tier_df['theme'].unique().tolist()

            breakdown[tier] = {
                "stock_count": len(tier_df),
                "unique_tickers": tier_df['ticker'].nunique(),
                "themes": themes,
                "theme_count": len(themes),
                "avg_momentum": round(tier_df['momentum'].mean() * 100, 2) if len(tier_df) > 0 else 0,
                "avg_cohesion": round(tier_df['fiedler'].mean(), 2) if len(tier_df) > 0 else 0
            }

        return breakdown
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/top-signals")
async def top_signals(limit: int = 20):
    """Get top signals ranked by combined score"""
    try:
        df = get_latest_data()

        # Get unique ticker-theme combinations, sorted by score
        top = df.nlargest(limit, 'combined_score')[
            ['ticker', 'company', 'theme', 'tier', 'combined_score', 'momentum', 'fiedler', 'action']
        ]

        return top.to_dict('records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/by-tier/{tier}")
async def signals_by_tier(tier: str, limit: int = 50):
    """Get signals filtered by TIER"""
    try:
        df = get_latest_data()

        # Normalize tier format
        tier_normalized = f"Tier {tier}" if tier.isdigit() else tier

        filtered = df[df['tier'] == tier_normalized]
        if filtered.empty:
            return {"tier": tier_normalized, "signals": []}

        result = filtered.nlargest(limit, 'combined_score')[
            ['ticker', 'company', 'theme', 'combined_score', 'momentum', 'fiedler', 'action', 'etf_exposure']
        ].to_dict('records')

        return {
            "tier": tier_normalized,
            "count": len(filtered),
            "signals": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/theme-signals/{theme}")
async def theme_signals(theme: str):
    """Get all signals for a specific theme"""
    try:
        df = get_latest_data()
        consolidated = get_latest_consolidated()

        filtered = df[df['theme'] == theme]
        if filtered.empty:
            raise HTTPException(status_code=404, detail=f"Theme '{theme}' not found")

        # Get theme-level stats from consolidated
        theme_info = consolidated.get('themes', {}).get(theme, {})

        signals = filtered[
            ['ticker', 'company', 'weight_in_theme', 'combined_score', 'momentum', 'action']
        ].to_dict('records')

        return {
            "theme": theme,
            "tier": filtered['tier'].iloc[0],
            "fiedler": round(filtered['fiedler'].iloc[0], 2),
            "momentum": round(filtered['momentum'].iloc[0] * 100, 2),
            "bull_ratio": round(filtered['bull_ratio'].iloc[0] * 100, 1),
            "stock_count": len(signals),
            "etf_exposure": filtered['etf_exposure'].iloc[0] if 'etf_exposure' in filtered.columns else None,
            "signals": signals
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
