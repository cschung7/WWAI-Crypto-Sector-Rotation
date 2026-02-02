#!/usr/bin/env python3
"""
Generate Investment Implications Report for USA Sector Rotation
Creates actionable investment recommendations based on analysis
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import logging

from config import (
    PROJECT_ROOT, DATA_DIR, REPORTS_DIR, ANALYSIS_DIR,
    TIER_DESCRIPTIONS, THEME_TO_GICS, THEME_TO_ETF
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_latest_consolidated() -> Dict:
    """Load latest consolidated analysis"""
    files = sorted(DATA_DIR.glob("consolidated_ticker_analysis_*.json"), reverse=True)
    if not files:
        raise FileNotFoundError("No consolidated analysis found")

    with open(files[0]) as f:
        return json.load(f)


def load_latest_actionable() -> pd.DataFrame:
    """Load latest actionable tickers"""
    files = sorted(DATA_DIR.glob("actionable_tickers_*.csv"), reverse=True)
    if not files:
        raise FileNotFoundError("No actionable tickers found")

    return pd.read_csv(files[0])


def generate_qa_document(data: Dict, actionable_df: pd.DataFrame) -> str:
    """Generate Q&A context document for AI chat"""

    date_str = datetime.now().strftime("%Y-%m-%d")

    # Get tier distributions
    tier1_themes = [t for t, info in data['themes'].items() if info['tier'] == 'Tier 1']
    tier2_themes = [t for t, info in data['themes'].items() if info['tier'] == 'Tier 2']
    tier3_themes = [t for t, info in data['themes'].items() if info['tier'] == 'Tier 3']

    # Get top picks
    top_picks = data.get('top_picks', [])[:10]

    # Build document
    doc = f"""# USA Sector Rotation - Investment Q&A Context
**Date**: {date_str}
**Data Source**: Sector-Leaders-Usa Analysis

---

## Current Market Status

### TIER Distribution
- **TIER 1 (AGGRESSIVE BUY)**: {len(tier1_themes)} themes
- **TIER 2 (ACCUMULATE)**: {len(tier2_themes)} themes
- **TIER 3 (RESEARCH)**: {len(tier3_themes)} themes
- **TIER 4 (MONITOR)**: {data['summary']['tier4_count']} themes

### Signal Quality
- Total themes analyzed: {data['summary']['total_themes']}
- Strong signals (T1+T2): {len(tier1_themes) + len(tier2_themes)}

---

## TIER 1 Themes (AGGRESSIVE BUY)

"""

    for theme in tier1_themes:
        info = data['themes'][theme]
        doc += f"""### {theme}
- **Combined Score**: {info['combined_score']:.4f}
- **Momentum**: {info['momentum']*100:.2f}%
- **Fiedler (Cohesion)**: {info['fiedler']:.2f}
- **Bull Ratio**: {info['bull_ratio']*100:.0f}%
- **ETFs**: {', '.join(info.get('etfs', [])[:3])}
- **Top Tickers**: {', '.join([t['ticker'] for t in info.get('top_tickers', [])[:5]])}
- **GICS Sector**: {info.get('gics_sector', 'N/A')}

"""

    doc += """---

## TIER 2 Themes (ACCUMULATE)

"""

    for theme in tier2_themes:
        info = data['themes'][theme]
        doc += f"""### {theme}
- **Combined Score**: {info['combined_score']:.4f}
- **Momentum**: {info['momentum']*100:.2f}%
- **Fiedler (Cohesion)**: {info['fiedler']:.2f}
- **Top Tickers**: {', '.join([t['ticker'] for t in info.get('top_tickers', [])[:5]])}

"""

    doc += """---

## Top Stock Picks

| Rank | Ticker | Theme | Tier | Score | Momentum |
|------|--------|-------|------|-------|----------|
"""

    for i, pick in enumerate(top_picks, 1):
        doc += f"| {i} | {pick['ticker']} | {pick['theme']} | {pick['tier']} | {pick['combined_score']:.4f} | {pick['momentum']*100:.2f}% |\n"

    doc += """

---

## Investment Actions by TIER

### TIER 1: AGGRESSIVE BUY
- Full position sizing (100% target allocation)
- High conviction, strong momentum
- Consider direct stock positions or ETF exposure

### TIER 2: ACCUMULATE
- Build positions gradually (50-75% target)
- Good momentum, building strength
- Dollar-cost averaging recommended

### TIER 3: RESEARCH
- Small starter positions (25-50% target)
- Monitor for momentum improvement
- Research catalysts and fundamentals

### TIER 4: MONITOR
- No new positions
- Wait for signal improvement
- Review weekly for tier changes

---

## GICS Sector Summary

"""

    for gics, gics_info in data.get('gics_summary', {}).items():
        doc += f"""### {gics}
- Themes: {', '.join(gics_info['themes'])}
- Best Tier: {gics_info['best_tier']}
- Avg Score: {gics_info['avg_score']:.4f}

"""

    doc += f"""---

## Key Metrics Explanation

- **Combined Score**: Weighted combination of momentum, trend, cohesion, and bull ratio
- **Fiedler (Cohesion)**: Measures how synchronized stocks within a theme move together
- **Bull Ratio**: Percentage of stocks in bullish regime (HMM-based)
- **Momentum**: Recent price performance relative to trend
- **Volatility**: Standard deviation of returns

---

**Last Updated**: {date_str}
**Note**: This analysis is for informational purposes. Always conduct your own research.
"""

    return doc


def generate_investment_memo(data: Dict) -> str:
    """Generate executive investment memo"""

    date_str = datetime.now().strftime("%Y-%m-%d")

    tier1_themes = [t for t, info in data['themes'].items() if info['tier'] == 'Tier 1']
    tier2_themes = [t for t, info in data['themes'].items() if info['tier'] == 'Tier 2']
    top_picks = data.get('top_picks', [])[:5]

    memo = f"""# USA Sector Rotation - Investment Memo
**Date**: {date_str}

---

## Executive Summary

### Current Positioning
- **Bullish Themes**: {len(tier1_themes) + len(tier2_themes)} ({len(tier1_themes)} TIER 1, {len(tier2_themes)} TIER 2)
- **Signal Quality**: {int((len(tier1_themes) + len(tier2_themes)) / max(1, data['summary']['total_themes']) * 100)}%
- **Primary Sectors**: {', '.join(set([data['themes'][t].get('gics_sector', 'N/A') for t in tier1_themes + tier2_themes]))}

---

## Action Items

### Immediate Actions (TIER 1)
"""

    for theme in tier1_themes:
        info = data['themes'][theme]
        etfs = info.get('etfs', [])
        top_tickers = [t['ticker'] for t in info.get('top_tickers', [])[:3]]
        memo += f"""
**{theme}**
- Action: AGGRESSIVE BUY
- ETF Option: {etfs[0] if etfs else 'N/A'}
- Individual Stocks: {', '.join(top_tickers)}
- Score: {info['combined_score']:.4f}
"""

    memo += """
### Building Positions (TIER 2)
"""

    for theme in tier2_themes:
        info = data['themes'][theme]
        etfs = info.get('etfs', [])
        top_tickers = [t['ticker'] for t in info.get('top_tickers', [])[:3]]
        memo += f"""
**{theme}**
- Action: ACCUMULATE
- ETF Option: {etfs[0] if etfs else 'N/A'}
- Individual Stocks: {', '.join(top_tickers)}
- Score: {info['combined_score']:.4f}
"""

    memo += """
---

## Top Individual Stock Picks

"""

    for i, pick in enumerate(top_picks, 1):
        memo += f"{i}. **{pick['ticker']}** - {pick['theme']} ({pick['tier']})\n"

    memo += f"""
---

## Risk Considerations

1. **Concentration Risk**: Monitor exposure to individual themes
2. **Volatility**: TIER 1 themes may have higher volatility
3. **Correlation**: Consider GICS sector diversification
4. **Timing**: Use momentum confirmation before entry

---

## Next Review

- **Daily**: Monitor TIER 1 positions
- **Weekly**: Review TIER classifications
- **Monthly**: Rebalance based on tier changes

---

**Disclaimer**: This memo is for informational purposes only. Not financial advice.
"""

    return memo


def main():
    """Main execution"""
    logger.info("=" * 60)
    logger.info("USA Sector Rotation - Generate Investment Reports")
    logger.info("=" * 60)

    # Ensure directories exist
    REPORTS_DIR.mkdir(exist_ok=True)
    ANALYSIS_DIR.mkdir(exist_ok=True)

    # Load data
    data = load_latest_consolidated()
    actionable_df = load_latest_actionable()

    date_suffix = datetime.now().strftime("%Y%m%d")

    # Generate Q&A document
    logger.info("Generating Q&A context document...")
    qa_doc = generate_qa_document(data, actionable_df)
    qa_path = ANALYSIS_DIR / f"QA_investment_questions_{date_suffix}.md"
    with open(qa_path, 'w') as f:
        f.write(qa_doc)
    logger.info(f"Saved: {qa_path}")

    # Generate investment memo
    logger.info("Generating investment memo...")
    memo = generate_investment_memo(data)
    memo_path = REPORTS_DIR / f"investment_memo_{date_suffix}.md"
    with open(memo_path, 'w') as f:
        f.write(memo)
    logger.info(f"Saved: {memo_path}")

    # Print summary
    tier1_themes = [t for t, info in data['themes'].items() if info['tier'] == 'Tier 1']
    tier2_themes = [t for t, info in data['themes'].items() if info['tier'] == 'Tier 2']

    print("\n" + "=" * 60)
    print("INVESTMENT REPORT GENERATED")
    print("=" * 60)
    print(f"\nTIER 1 Themes ({len(tier1_themes)}):")
    for t in tier1_themes:
        print(f"  - {t}")

    print(f"\nTIER 2 Themes ({len(tier2_themes)}):")
    for t in tier2_themes:
        print(f"  - {t}")

    print(f"\nTop Picks:")
    for i, pick in enumerate(data.get('top_picks', [])[:5], 1):
        print(f"  {i}. {pick['ticker']} ({pick['theme']})")

    print(f"\nOutput Files:")
    print(f"  - {qa_path}")
    print(f"  - {memo_path}")


if __name__ == "__main__":
    main()
