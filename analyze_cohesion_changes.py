#!/usr/bin/env python3
"""
Analyze Theme Cohesion Changes for USA Sector Rotation
Tracks weekly Fiedler eigenvalue changes to identify emerging/declining themes
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import logging

from config import PROJECT_ROOT, DATA_DIR, REPORTS_DIR, SECTOR_LEADERS_RESULTS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_rankings_by_date() -> Dict[str, pd.DataFrame]:
    """Load all available ranking files by date"""
    files = sorted(SECTOR_LEADERS_RESULTS.glob("combined_score_ranking_*.csv"))
    rankings = {}

    for f in files:
        date_str = f.stem.split('_')[-1]  # Extract YYYYMMDD
        try:
            df = pd.read_csv(f)
            rankings[date_str] = df
        except Exception as e:
            logger.warning(f"Could not load {f}: {e}")

    return rankings


def calculate_cohesion_changes(rankings: Dict[str, pd.DataFrame], lookback_days: int = 7) -> pd.DataFrame:
    """Calculate Fiedler changes between periods"""

    dates = sorted(rankings.keys(), reverse=True)
    if len(dates) < 2:
        logger.warning("Not enough data points for comparison")
        return pd.DataFrame()

    latest_date = dates[0]
    latest_df = rankings[latest_date]

    # Find comparison date (approximately lookback_days ago)
    target_date = datetime.strptime(latest_date, "%Y%m%d") - timedelta(days=lookback_days)

    compare_date = None
    for d in dates[1:]:
        d_datetime = datetime.strptime(d, "%Y%m%d")
        if d_datetime <= target_date:
            compare_date = d
            break

    if not compare_date:
        compare_date = dates[1] if len(dates) > 1 else None

    if not compare_date:
        logger.warning("No comparison date found")
        return pd.DataFrame()

    compare_df = rankings[compare_date]

    # Merge and calculate changes
    merged = latest_df.merge(
        compare_df[['theme', 'fiedler', 'momentum', 'combined_score']],
        on='theme',
        suffixes=('', '_prev')
    )

    merged['fiedler_change'] = merged['fiedler'] - merged['fiedler_prev']
    merged['fiedler_pct_change'] = (merged['fiedler_change'] / merged['fiedler_prev'].replace(0, 1)) * 100
    merged['momentum_change'] = merged['momentum'] - merged['momentum_prev']
    merged['score_change'] = merged['combined_score'] - merged['combined_score_prev']

    # Add status classification
    def classify_cohesion(row):
        if row['fiedler'] >= 3.0:
            return "VERY STRONG"
        elif row['fiedler'] >= 1.5:
            return "STRONG"
        elif row['fiedler'] >= 0.5:
            return "MODERATE"
        else:
            return "WEAK"

    def classify_change(pct_change):
        if pct_change >= 20:
            return "ENHANCED ↑↑"
        elif pct_change >= 5:
            return "IMPROVING ↑"
        elif pct_change <= -20:
            return "DECLINING ↓↓"
        elif pct_change <= -5:
            return "WEAKENING ↓"
        else:
            return "STABLE →"

    merged['cohesion_status'] = merged.apply(classify_cohesion, axis=1)
    merged['change_status'] = merged['fiedler_pct_change'].apply(classify_change)

    return merged, latest_date, compare_date


def generate_cohesion_report(changes_df: pd.DataFrame, latest_date: str, compare_date: str) -> str:
    """Generate markdown report for cohesion changes"""

    report = f"""# USA Theme Cohesion Analysis Report
**Latest Data**: {latest_date}
**Compared To**: {compare_date}

---

## Executive Summary

"""

    # Count statuses
    enhanced = len(changes_df[changes_df['change_status'].str.contains('ENHANCED')])
    declining = len(changes_df[changes_df['change_status'].str.contains('DECLINING')])
    stable = len(changes_df[changes_df['change_status'].str.contains('STABLE')])

    report += f"""### Cohesion Trend Overview
- **Enhanced (↑↑)**: {enhanced} themes
- **Declining (↓↓)**: {declining} themes
- **Stable (→)**: {stable} themes

"""

    # Top enhanced themes
    report += "## 🚀 Top 5 Enhanced Cohesion\n\n"
    report += "| Theme | Fiedler | Change | Status | Tier |\n"
    report += "|-------|---------|--------|--------|------|\n"

    enhanced_themes = changes_df.nlargest(5, 'fiedler_pct_change')
    for _, row in enhanced_themes.iterrows():
        report += f"| {row['theme']} | {row['fiedler']:.2f} | {row['fiedler_pct_change']:+.1f}% | {row['cohesion_status']} | {row['tier']} |\n"

    # Top declining themes
    report += "\n## 📉 Top 5 Declining Cohesion\n\n"
    report += "| Theme | Fiedler | Change | Status | Tier |\n"
    report += "|-------|---------|--------|--------|------|\n"

    declining_themes = changes_df.nsmallest(5, 'fiedler_pct_change')
    for _, row in declining_themes.iterrows():
        report += f"| {row['theme']} | {row['fiedler']:.2f} | {row['fiedler_pct_change']:+.1f}% | {row['cohesion_status']} | {row['tier']} |\n"

    # All themes sorted by current cohesion
    report += "\n## 📊 All Themes by Cohesion Strength\n\n"
    report += "| # | Theme | Fiedler | Change | Status | Momentum | Tier |\n"
    report += "|---|-------|---------|--------|--------|----------|------|\n"

    sorted_df = changes_df.sort_values('fiedler', ascending=False)
    for i, (_, row) in enumerate(sorted_df.iterrows(), 1):
        mom_emoji = "↑" if row['momentum'] > 0 else "↓"
        report += f"| {i} | {row['theme']} | {row['fiedler']:.2f} | {row['fiedler_pct_change']:+.1f}% | {row['cohesion_status']} | {mom_emoji}{row['momentum']*100:.2f}% | {row['tier']} |\n"

    # Investment implications
    report += """

---

## Investment Implications

### Enhanced Cohesion Themes
Themes with increasing Fiedler values indicate:
- Stocks within the theme moving more synchronously
- Stronger theme-level momentum potential
- Consider increasing exposure if combined with positive momentum

### Declining Cohesion Themes
Themes with decreasing Fiedler values indicate:
- Stock dispersion within the theme
- Potential for individual stock picking over theme ETFs
- May signal theme exhaustion or rotation

### Action Items
1. **ENHANCED + TIER 1/2**: Strong conviction, increase position
2. **DECLINING + TIER 4**: Consider exit or rotation
3. **STABLE + TIER 3**: Monitor for breakout signals

"""

    report += f"\n---\n\n**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"

    return report


def main():
    """Main execution"""
    logger.info("=" * 60)
    logger.info("USA Sector Rotation - Cohesion Change Analysis")
    logger.info("=" * 60)

    REPORTS_DIR.mkdir(exist_ok=True)

    # Load all rankings
    rankings = load_rankings_by_date()
    logger.info(f"Found {len(rankings)} ranking files")

    if len(rankings) < 2:
        logger.error("Need at least 2 data points for comparison")
        return

    # Calculate changes
    result = calculate_cohesion_changes(rankings)
    if isinstance(result, tuple):
        changes_df, latest_date, compare_date = result
    else:
        logger.error("Could not calculate changes")
        return

    # Generate report
    report = generate_cohesion_report(changes_df, latest_date, compare_date)

    # Save report
    report_path = REPORTS_DIR / f"cohesion_changes_{datetime.now().strftime('%Y%m%d')}.md"
    with open(report_path, 'w') as f:
        f.write(report)
    logger.info(f"Saved: {report_path}")

    # Save data
    data_path = DATA_DIR / f"cohesion_changes_{datetime.now().strftime('%Y%m%d')}.csv"
    changes_df.to_csv(data_path, index=False)
    logger.info(f"Saved: {data_path}")

    # Print summary
    print("\n" + "=" * 60)
    print("COHESION ANALYSIS COMPLETE")
    print("=" * 60)

    print(f"\nTop Enhanced:")
    for _, row in changes_df.nlargest(3, 'fiedler_pct_change').iterrows():
        print(f"  {row['theme']}: {row['fiedler']:.2f} ({row['fiedler_pct_change']:+.1f}%)")

    print(f"\nTop Declining:")
    for _, row in changes_df.nsmallest(3, 'fiedler_pct_change').iterrows():
        print(f"  {row['theme']}: {row['fiedler']:.2f} ({row['fiedler_pct_change']:+.1f}%)")


if __name__ == "__main__":
    main()
