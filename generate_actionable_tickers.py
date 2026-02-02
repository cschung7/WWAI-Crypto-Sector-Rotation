#!/usr/bin/env python3
"""
Generate Actionable Tickers for USA Sector Rotation
Adapted from KRX system - produces investment-ready analysis

Outputs:
- actionable_tickers_YYYYMMDD.csv
- consolidated_ticker_analysis_YYYYMMDD.json
- tier1_key_players_YYYYMMDD.json
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import logging

from config import (
    PROJECT_ROOT, DATA_DIR, REPORTS_DIR,
    SECTOR_LEADERS_RESULTS, THEME_TICKER_MASTER,
    TIER_THRESHOLDS, TIER_DESCRIPTIONS, THEME_TO_GICS, THEME_TO_ETF
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def load_latest_rankings() -> pd.DataFrame:
    """Load the most recent combined score rankings from Sector-Leaders-Usa"""
    files = sorted(SECTOR_LEADERS_RESULTS.glob("combined_score_ranking_*.csv"), reverse=True)
    if not files:
        raise FileNotFoundError("No combined_score_ranking files found")

    latest = files[0]
    logger.info(f"Loading rankings from: {latest}")
    return pd.read_csv(latest)


def load_theme_tickers() -> pd.DataFrame:
    """Load theme-ticker mapping from master CSV"""
    if not THEME_TICKER_MASTER.exists():
        raise FileNotFoundError(f"Theme ticker master not found: {THEME_TICKER_MASTER}")

    return pd.read_csv(THEME_TICKER_MASTER)


def calculate_tier(combined_score: float) -> str:
    """Determine TIER based on combined score"""
    if combined_score >= TIER_THRESHOLDS["tier1"]:
        return "Tier 1"
    elif combined_score >= TIER_THRESHOLDS["tier2"]:
        return "Tier 2"
    elif combined_score >= TIER_THRESHOLDS["tier3"]:
        return "Tier 3"
    else:
        return "Tier 4"


def get_top_tickers_for_theme(theme: str, theme_tickers_df: pd.DataFrame, n: int = 5) -> List[Dict]:
    """Get top N tickers for a theme by weight"""
    theme_data = theme_tickers_df[theme_tickers_df['theme'] == theme].copy()
    if theme_data.empty:
        return []

    # Sort by weight descending
    theme_data = theme_data.sort_values('weight', ascending=False).head(n)

    return theme_data[['ticker', 'company', 'weight']].to_dict('records')


def generate_actionable_tickers(rankings_df: pd.DataFrame, theme_tickers_df: pd.DataFrame) -> pd.DataFrame:
    """Generate actionable tickers with full analysis"""

    actionable = []

    for _, row in rankings_df.iterrows():
        theme = row['theme']
        tier = row.get('tier', calculate_tier(row['combined_score']))

        # Get top tickers for this theme
        top_tickers = get_top_tickers_for_theme(theme, theme_tickers_df, n=10)

        # Get GICS sector mapping
        gics_sector = THEME_TO_GICS.get(theme, "Other")

        # Get relevant ETFs
        etfs = THEME_TO_ETF.get(theme, [])

        for ticker_info in top_tickers:
            actionable.append({
                'theme': theme,
                'ticker': ticker_info['ticker'],
                'company': ticker_info['company'],
                'weight_in_theme': ticker_info['weight'],
                'tier': tier,
                'combined_score': row['combined_score'],
                'momentum': row['momentum'],
                'trend': row['trend'],
                'fiedler': row['fiedler'],
                'bull_ratio': row['bull_ratio'],
                'stability': row['stability'],
                'recent_return_pct': row['recent_return_pct'],
                'volatility': row['volatility'],
                'gics_sector': gics_sector,
                'etf_exposure': ','.join(etfs[:2]) if etfs else '',
                'action': TIER_DESCRIPTIONS[tier]['action'],
            })

    return pd.DataFrame(actionable)


def generate_consolidated_analysis(rankings_df: pd.DataFrame, theme_tickers_df: pd.DataFrame) -> Dict:
    """Generate comprehensive JSON analysis"""

    analysis = {
        'generated_at': datetime.now().isoformat(),
        'summary': {
            'total_themes': len(rankings_df),
            'tier1_count': len(rankings_df[rankings_df['tier'] == 'Tier 1']),
            'tier2_count': len(rankings_df[rankings_df['tier'] == 'Tier 2']),
            'tier3_count': len(rankings_df[rankings_df['tier'] == 'Tier 3']),
            'tier4_count': len(rankings_df[rankings_df['tier'] == 'Tier 4']),
        },
        'themes': {},
        'gics_summary': {},
        'top_picks': [],
    }

    # Process each theme
    for _, row in rankings_df.iterrows():
        theme = row['theme']
        tier = row.get('tier', calculate_tier(row['combined_score']))
        gics = THEME_TO_GICS.get(theme, "Other")

        top_tickers = get_top_tickers_for_theme(theme, theme_tickers_df, n=5)

        analysis['themes'][theme] = {
            'tier': tier,
            'rank': int(row['rank']) if pd.notna(row.get('rank')) else 0,
            'combined_score': float(row['combined_score']),
            'momentum': float(row['momentum']),
            'trend': float(row['trend']),
            'fiedler': float(row['fiedler']),
            'bull_ratio': float(row['bull_ratio']),
            'stability': float(row['stability']),
            'recent_return_pct': float(row['recent_return_pct']),
            'volatility': float(row['volatility']),
            'gics_sector': gics,
            'etfs': THEME_TO_ETF.get(theme, []),
            'top_tickers': top_tickers,
            'action': TIER_DESCRIPTIONS[tier]['action'],
        }

        # Aggregate GICS summary
        if gics not in analysis['gics_summary']:
            analysis['gics_summary'][gics] = {
                'themes': [],
                'avg_score': 0,
                'best_tier': 'Tier 4',
            }
        analysis['gics_summary'][gics]['themes'].append(theme)

    # Calculate GICS averages
    for gics, data in analysis['gics_summary'].items():
        gics_themes = [analysis['themes'][t] for t in data['themes']]
        if gics_themes:
            data['avg_score'] = np.mean([t['combined_score'] for t in gics_themes])
            best_tier = min([t['tier'] for t in gics_themes], key=lambda x: int(x.split()[-1]))
            data['best_tier'] = best_tier

    # Top picks (Tier 1 and Tier 2 themes with best tickers)
    for theme, data in analysis['themes'].items():
        if data['tier'] in ['Tier 1', 'Tier 2'] and data['top_tickers']:
            for ticker in data['top_tickers'][:3]:
                analysis['top_picks'].append({
                    'ticker': ticker['ticker'],
                    'company': ticker['company'],
                    'theme': theme,
                    'tier': data['tier'],
                    'combined_score': data['combined_score'],
                    'momentum': data['momentum'],
                })

    # Sort top picks by combined score
    analysis['top_picks'] = sorted(
        analysis['top_picks'],
        key=lambda x: x['combined_score'],
        reverse=True
    )[:20]

    return analysis


def generate_tier1_key_players(rankings_df: pd.DataFrame, theme_tickers_df: pd.DataFrame) -> Dict:
    """Generate key players for TIER 1 themes"""

    tier1_themes = rankings_df[rankings_df['tier'] == 'Tier 1']['theme'].tolist()

    key_players = {
        'generated_at': datetime.now().isoformat(),
        'tier1_themes': tier1_themes,
        'key_players': {},
    }

    for theme in tier1_themes:
        top_tickers = get_top_tickers_for_theme(theme, theme_tickers_df, n=10)
        key_players['key_players'][theme] = {
            'tickers': top_tickers,
            'count': len(top_tickers),
            'etfs': THEME_TO_ETF.get(theme, []),
        }

    return key_players


def main():
    """Main execution"""
    logger.info("=" * 60)
    logger.info("USA Sector Rotation - Generate Actionable Tickers")
    logger.info("=" * 60)

    # Ensure output directories exist
    DATA_DIR.mkdir(exist_ok=True)
    REPORTS_DIR.mkdir(exist_ok=True)

    # Load data
    rankings_df = load_latest_rankings()
    theme_tickers_df = load_theme_tickers()

    date_suffix = datetime.now().strftime("%Y%m%d")

    # Generate actionable tickers CSV
    logger.info("Generating actionable tickers...")
    actionable_df = generate_actionable_tickers(rankings_df, theme_tickers_df)
    actionable_path = DATA_DIR / f"actionable_tickers_{date_suffix}.csv"
    actionable_df.to_csv(actionable_path, index=False)
    logger.info(f"Saved: {actionable_path} ({len(actionable_df)} rows)")

    # Generate consolidated analysis JSON
    logger.info("Generating consolidated analysis...")
    consolidated = generate_consolidated_analysis(rankings_df, theme_tickers_df)
    consolidated_path = DATA_DIR / f"consolidated_ticker_analysis_{date_suffix}.json"
    with open(consolidated_path, 'w') as f:
        json.dump(consolidated, f, indent=2)
    logger.info(f"Saved: {consolidated_path}")

    # Generate TIER 1 key players
    logger.info("Generating TIER 1 key players...")
    key_players = generate_tier1_key_players(rankings_df, theme_tickers_df)
    key_players_path = DATA_DIR / f"tier1_key_players_{date_suffix}.json"
    with open(key_players_path, 'w') as f:
        json.dump(key_players, f, indent=2)
    logger.info(f"Saved: {key_players_path}")

    # Print summary
    print("\n" + "=" * 60)
    print("GENERATION COMPLETE")
    print("=" * 60)
    print(f"\nTIER Distribution:")
    print(f"  TIER 1 (AGGRESSIVE): {consolidated['summary']['tier1_count']} themes")
    print(f"  TIER 2 (ACCUMULATE): {consolidated['summary']['tier2_count']} themes")
    print(f"  TIER 3 (RESEARCH):   {consolidated['summary']['tier3_count']} themes")
    print(f"  TIER 4 (MONITOR):    {consolidated['summary']['tier4_count']} themes")

    print(f"\nTop Picks ({len(consolidated['top_picks'])} stocks):")
    for i, pick in enumerate(consolidated['top_picks'][:10], 1):
        print(f"  {i:2}. {pick['ticker']:<6} ({pick['theme']}) - {pick['tier']}")

    print(f"\nOutput Files:")
    print(f"  - {actionable_path}")
    print(f"  - {consolidated_path}")
    print(f"  - {key_players_path}")

    return consolidated


if __name__ == "__main__":
    main()
