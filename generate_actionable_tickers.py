"""
Crypto Sector Rotation - Generate Actionable Tickers
Creates actionable_tickers.csv from category rankings and ticker mappings
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
import json

# Paths
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
CRYPTO_PRICE_DIR = Path("/mnt/nas/AutoGluon/AutoML_Crypto/CRYPTONOTTRAINED")

def get_tier(combined_score: float, fiedler: float) -> str:
    """Determine tier based on combined score and fiedler"""
    if combined_score >= 0.20 or fiedler >= 7.5:
        return "Tier 1"
    elif combined_score >= 0.10 or fiedler >= 3.0:
        return "Tier 2"
    elif combined_score >= 0.05 or fiedler >= 1.0:
        return "Tier 3"
    else:
        return "Tier 4"

def get_action(tier: str) -> str:
    """Get action based on tier"""
    actions = {
        "Tier 1": "AGGRESSIVE BUY",
        "Tier 2": "ACCUMULATE",
        "Tier 3": "RESEARCH",
        "Tier 4": "MONITOR"
    }
    return actions.get(tier, "MONITOR")

def get_sector(category: str) -> str:
    """Map category to sector"""
    category_lower = category.lower()

    if any(x in category_lower for x in ['ai_', 'ai ', 'generative', 'defai']):
        return "AI"
    elif any(x in category_lower for x in ['defi', 'amm', 'yield', 'derivatives', 'lending', 'dex']):
        return "DeFi"
    elif any(x in category_lower for x in ['gaming', 'metaverse', 'play_to_earn', 'move_to_earn']):
        return "Gaming"
    elif any(x in category_lower for x in ['meme', 'doge', 'shib', 'pepe']):
        return "Memes"
    elif any(x in category_lower for x in ['privacy', 'zero_knowledge']):
        return "Privacy"
    elif any(x in category_lower for x in ['infrastructure', 'oracle', 'storage', 'depin', 'layer_1']):
        return "Infrastructure"
    elif any(x in category_lower for x in ['stablecoin', 'usd_', 'fiat_']):
        return "Stablecoins"
    elif any(x in category_lower for x in ['ecosystem', 'solana', 'ethereum', 'bnb', 'bitcoin']):
        return "Ecosystem"
    elif any(x in category_lower for x in ['portfolio', 'launchpad', 'ventures']):
        return "VC_Portfolio"
    elif any(x in category_lower for x in ['tokenized', 'rwa', 'real_world']):
        return "RWA"
    else:
        return "Other"

def main():
    print("=" * 60)
    print("Crypto Sector Rotation - Actionable Tickers Generator")
    print("=" * 60)

    # Find latest ranking file
    ranking_files = sorted(DATA_DIR.glob("combined_score_ranking_*.csv"), reverse=True)
    if not ranking_files:
        print("ERROR: No ranking files found!")
        return

    ranking_file = ranking_files[0]
    print(f"\nUsing ranking file: {ranking_file.name}")

    # Load category rankings
    rankings_df = pd.read_csv(ranking_file)
    print(f"Loaded {len(rankings_df)} categories")

    # Load ticker mappings
    ticker_file = PROJECT_ROOT / "theme_ticker_master.csv"
    tickers_df = pd.read_csv(ticker_file)
    print(f"Loaded {len(tickers_df)} ticker mappings")

    # Get available tickers from CRYPTONOTTRAINED (have price data)
    available_tickers = set()
    if CRYPTO_PRICE_DIR.exists():
        for f in CRYPTO_PRICE_DIR.glob("*-USD.csv"):
            ticker = f.stem.replace("-USD", "")
            available_tickers.add(ticker)
        print(f"Found {len(available_tickers)} tickers with price data in CRYPTONOTTRAINED")

        # Filter to only tickers with price data
        # ticker_clean column has clean ticker symbols (e.g., "BTC" not "BTC-USD")
        filter_col = 'ticker_clean' if 'ticker_clean' in tickers_df.columns else 'ticker'
        before_filter = len(tickers_df)
        if filter_col == 'ticker':
            # Remove -USD suffix for matching
            tickers_df['_filter_ticker'] = tickers_df['ticker'].str.replace('-USD', '', regex=False)
            tickers_df = tickers_df[tickers_df['_filter_ticker'].isin(available_tickers)]
            tickers_df = tickers_df.drop(columns=['_filter_ticker'])
        else:
            tickers_df = tickers_df[tickers_df[filter_col].isin(available_tickers)]
        print(f"Filtered: {before_filter} -> {len(tickers_df)} tickers (removed {before_filter - len(tickers_df)} without price data)")

    # Rename columns for consistency
    rankings_df = rankings_df.rename(columns={'sector': 'category'})
    tickers_df = tickers_df.rename(columns={'category': 'theme'})
    if 'ticker_clean' in tickers_df.columns:
        tickers_df = tickers_df.rename(columns={'ticker_clean': 'ticker_symbol'})

    # Merge rankings with tickers
    merged_df = tickers_df.merge(
        rankings_df,
        left_on='theme',
        right_on='category',
        how='left'
    )

    # Fill NaN values
    merged_df['combined_score'] = merged_df['combined_score'].fillna(0)
    merged_df['momentum'] = merged_df['momentum'].fillna(0)
    merged_df['trend'] = merged_df['trend'].fillna(0)
    merged_df['fiedler'] = merged_df['fiedler'].fillna(0)
    merged_df['bull_ratio'] = merged_df['bull_ratio'].fillna(0)
    merged_df['stability'] = merged_df['stability'].fillna(0)
    merged_df['recent_return_pct'] = merged_df['recent_return_pct'].fillna(0)
    merged_df['volatility'] = merged_df['volatility'].fillna(0)

    # Calculate tier and action
    merged_df['tier'] = merged_df.apply(
        lambda x: get_tier(x['combined_score'], x['fiedler']), axis=1
    )
    merged_df['action'] = merged_df['tier'].apply(get_action)
    merged_df['sector'] = merged_df['theme'].apply(get_sector)

    # Create output dataframe
    output_df = pd.DataFrame({
        'theme': merged_df['theme'],
        'ticker': merged_df['ticker'],
        'ticker_clean': merged_df['ticker_symbol'],
        'confidence': merged_df['confidence'],
        'tier': merged_df['tier'],
        'combined_score': merged_df['combined_score'].round(6),
        'momentum': merged_df['momentum'].round(6),
        'trend': merged_df['trend'].round(4),
        'fiedler': merged_df['fiedler'].round(6),
        'bull_ratio': merged_df['bull_ratio'].round(2),
        'stability': merged_df['stability'].round(4),
        'recent_return_pct': merged_df['recent_return_pct'].round(2),
        'volatility': merged_df['volatility'].round(2),
        'sector': merged_df['sector'],
        'action': merged_df['action']
    })

    # Sort by combined_score descending
    output_df = output_df.sort_values('combined_score', ascending=False)

    # Save to CSV
    date_suffix = datetime.now().strftime("%Y%m%d")
    output_file = DATA_DIR / f"actionable_tickers_{date_suffix}.csv"
    output_df.to_csv(output_file, index=False)
    print(f"\nSaved {len(output_df)} actionable tickers to {output_file.name}")

    # Print tier summary
    print("\n" + "=" * 60)
    print("TIER SUMMARY")
    print("=" * 60)
    tier_counts = output_df['tier'].value_counts().sort_index()
    for tier, count in tier_counts.items():
        action = get_action(tier)
        print(f"  {tier}: {count:,} tickers ({action})")

    # Print top picks
    print("\n" + "=" * 60)
    print("TOP 20 PICKS (Tier 1)")
    print("=" * 60)
    tier1 = output_df[output_df['tier'] == 'Tier 1'].head(20)
    for _, row in tier1.iterrows():
        print(f"  {row['ticker_clean']:10s} | {row['theme']:30s} | Score: {row['combined_score']:.4f}")

    # Create consolidated analysis JSON
    print("\n" + "=" * 60)
    print("GENERATING CONSOLIDATED ANALYSIS")
    print("=" * 60)

    # Category-level statistics
    category_stats = output_df.groupby('theme').agg({
        'ticker': 'count',
        'combined_score': 'first',
        'momentum': 'first',
        'trend': 'first',
        'fiedler': 'first',
        'bull_ratio': 'first',
        'tier': 'first',
        'action': 'first',
        'sector': 'first'
    }).reset_index()
    category_stats = category_stats.rename(columns={'ticker': 'ticker_count'})

    # Build consolidated JSON
    consolidated = {
        "metadata": {
            "generated": datetime.now().isoformat(),
            "source": ranking_file.name,
            "total_tickers": len(output_df),
            "total_categories": len(category_stats),
            "market": "Cryptocurrency",
            "classification": "CoinGecko Categories"
        },
        "statistics": {
            "tier1_count": len(output_df[output_df['tier'] == 'Tier 1']),
            "tier2_count": len(output_df[output_df['tier'] == 'Tier 2']),
            "tier3_count": len(output_df[output_df['tier'] == 'Tier 3']),
            "tier4_count": len(output_df[output_df['tier'] == 'Tier 4']),
            "avg_momentum": float(output_df['momentum'].mean()),
            "avg_fiedler": float(output_df['fiedler'].mean()),
            "avg_combined_score": float(output_df['combined_score'].mean())
        },
        "categories": category_stats.to_dict(orient='records'),
        "top_picks": output_df[output_df['tier'] == 'Tier 1'][['ticker_clean', 'theme', 'combined_score', 'momentum', 'fiedler']].head(50).to_dict(orient='records'),
        "sector_summary": output_df.groupby('sector').agg({
            'ticker': 'count',
            'combined_score': 'mean'
        }).reset_index().rename(columns={'ticker': 'count', 'combined_score': 'avg_score'}).to_dict(orient='records')
    }

    # Save consolidated JSON
    json_file = DATA_DIR / f"consolidated_ticker_analysis_{date_suffix}.json"
    with open(json_file, 'w') as f:
        json.dump(consolidated, f, indent=2)
    print(f"Saved consolidated analysis to {json_file.name}")

    # Create tier files
    for tier_num in range(1, 5):
        tier_name = f"Tier {tier_num}"
        tier_df = output_df[output_df['tier'] == tier_name]
        tier_file = DATA_DIR / f"tier{tier_num}_{['buy_now', 'accumulate', 'research', 'monitor'][tier_num-1]}_{date_suffix}.csv"
        tier_df.to_csv(tier_file, index=False)
        print(f"Saved {len(tier_df)} tickers to {tier_file.name}")

    print("\n" + "=" * 60)
    print("GENERATION COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()
