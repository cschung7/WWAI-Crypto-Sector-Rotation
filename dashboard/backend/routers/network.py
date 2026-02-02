"""
Network Graph API Router - Crypto Sector Rotation
Interactive network visualization for cryptocurrency categories
"""

from fastapi import APIRouter, HTTPException, Query
from pathlib import Path
import pandas as pd
import json
from typing import List, Dict, Any, Optional
import math

router = APIRouter()

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
THEME_TICKER_MASTER = PROJECT_ROOT / "theme_ticker_master.csv"


def safe_float(value) -> float:
    """Convert to float, return 0 if NaN/None"""
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return 0.0
    return float(value)


def load_theme_tickers() -> pd.DataFrame:
    """Load theme-ticker mapping"""
    if not THEME_TICKER_MASTER.exists():
        raise HTTPException(status_code=404, detail="Theme ticker master not found")
    df = pd.read_csv(THEME_TICKER_MASTER)
    # Normalize column names - support both 'theme' and 'category'
    if 'category' in df.columns and 'theme' not in df.columns:
        df['theme'] = df['category']
    if 'weight' not in df.columns:
        df['weight'] = 1.0  # Default weight for crypto
    if 'company' not in df.columns:
        df['company'] = df.get('ticker_clean', df['ticker'])
    return df


def load_consolidated() -> Dict:
    """Load consolidated analysis"""
    files = sorted(DATA_DIR.glob("consolidated_ticker_analysis_*.json"), reverse=True)
    if not files:
        raise HTTPException(status_code=404, detail="No consolidated analysis found")

    with open(files[0]) as f:
        return json.load(f)


def get_themes_dict(consolidated: Dict) -> Dict:
    """Convert categories array to themes dict if needed"""
    # If already has themes dict, return it
    if 'themes' in consolidated and isinstance(consolidated['themes'], dict):
        return consolidated['themes']

    # Convert categories array to dict
    themes = {}
    categories = consolidated.get('categories', [])
    if isinstance(categories, list):
        for cat in categories:
            theme_name = cat.get('theme', '')
            if theme_name:
                themes[theme_name] = cat
    return themes


def load_actionable_tickers() -> pd.DataFrame:
    """Load actionable tickers with scores"""
    files = sorted(DATA_DIR.glob("actionable_tickers_*.csv"), reverse=True)
    if not files:
        return pd.DataFrame()
    return pd.read_csv(files[0])


def fuzzy_match(query: str, text: str) -> bool:
    """Check if query matches text (partial matching)"""
    query = query.lower().strip()
    text = text.lower()

    if query in text:
        return True

    # Multi-word matching
    words = query.split()
    if len(words) > 1:
        return all(word in text for word in words)

    return False


def get_cohesion_color(fiedler: float) -> str:
    """Get color based on Fiedler value"""
    if fiedler > 3.0:
        return "#10b981"  # Green - very strong
    elif fiedler >= 1.0:
        return "#3b82f6"  # Blue - strong
    elif fiedler >= 0.5:
        return "#f59e0b"  # Yellow - moderate
    else:
        return "#ef4444"  # Red - weak


def get_cohesion_level(fiedler: float) -> str:
    """Get cohesion level string"""
    if fiedler > 3.0:
        return "very_strong"
    elif fiedler >= 1.0:
        return "strong"
    elif fiedler >= 0.5:
        return "moderate"
    else:
        return "weak"


@router.get("/search")
async def search_all(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(15, description="Max results per category")
) -> Dict[str, Any]:
    """Search stocks and themes with partial matching"""
    try:
        df = load_theme_tickers()
        consolidated = load_consolidated()
        actionable = load_actionable_tickers()

        # Search stocks
        stock_matches = []
        seen_tickers = set()

        for _, row in df.iterrows():
            ticker = row['ticker']
            company = row.get('company', '')

            if ticker in seen_tickers:
                continue

            if fuzzy_match(q, ticker) or fuzzy_match(q, company):
                # Get buy_pct from actionable tickers
                buy_pct = 50.0  # Default
                if not actionable.empty:
                    ticker_data = actionable[actionable['ticker'] == ticker]
                    if not ticker_data.empty:
                        # Calculate buy_pct from combined_score (scaled 0-100)
                        score = safe_float(ticker_data.iloc[0].get('combined_score', 0))
                        buy_pct = min(100, max(0, score * 500))  # Scale score to percentage

                stock_matches.append({
                    'name': f"{company} ({ticker})" if company else ticker,
                    'ticker': ticker,
                    'market': 'NYSE/NASDAQ',
                    'buy_pct': round(buy_pct, 1),
                    'type': 'stock',
                })
                seen_tickers.add(ticker)

                if len(stock_matches) >= limit:
                    break

        # Search themes
        theme_matches = []
        themes = get_themes_dict(consolidated)

        for theme, info in themes.items():
            if fuzzy_match(q, theme):
                theme_matches.append({
                    'theme': theme,
                    'tier': info.get('tier', 'Unknown'),
                    'fiedler': safe_float(info.get('fiedler', 0)),
                    'type': 'theme',
                })

                if len(theme_matches) >= limit:
                    break

        # Sort themes by fiedler
        theme_matches.sort(key=lambda x: x['fiedler'], reverse=True)

        return {
            "success": True,
            "query": q,
            "stocks": stock_matches,
            "themes": theme_matches,
            "stock_count": len(stock_matches),
            "theme_count": len(theme_matches),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/graph-data")
async def get_graph_data(
    stock: Optional[str] = Query(None, description="Stock ticker"),
    theme: Optional[str] = Query(None, description="Theme name"),
    depth: int = Query(1, description="Graph depth")
) -> Dict[str, Any]:
    """Get network graph data for visualization"""
    try:
        df = load_theme_tickers()
        consolidated = load_consolidated()
        actionable = load_actionable_tickers()

        nodes = []
        edges = []
        node_ids = set()

        def add_theme_node(theme_name):
            node_id = f"theme_{theme_name}"
            if node_id in node_ids:
                return
            node_ids.add(node_id)

            theme_info = get_themes_dict(consolidated).get(theme_name, {})
            fiedler = safe_float(theme_info.get('fiedler', 0))

            nodes.append({
                'id': node_id,
                'label': theme_name,
                'type': 'theme',
                'tier': theme_info.get('tier', 'Tier 4'),
                'fiedler': round(fiedler, 3),
                'size': 25,
                'color': get_cohesion_color(fiedler),
            })

        def add_stock_node(ticker, company='', is_center=False):
            node_id = f"stock_{ticker}"
            if node_id in node_ids:
                return
            node_ids.add(node_id)

            # Get signal data
            buy_pct = 50.0
            signal = 'neutral'
            if not actionable.empty:
                ticker_data = actionable[actionable['ticker'] == ticker]
                if not ticker_data.empty:
                    row = ticker_data.iloc[0]
                    score = safe_float(row.get('combined_score', 0))
                    buy_pct = min(100, max(0, score * 500))
                    if buy_pct >= 70:
                        signal = 'strong_buy'
                    elif buy_pct >= 50:
                        signal = 'buy'
                    elif buy_pct >= 30:
                        signal = 'neutral'
                    else:
                        signal = 'avoid'

            # Color by signal
            if signal == 'strong_buy':
                color = '#059669'
            elif signal == 'buy':
                color = '#10b981'
            elif signal == 'neutral':
                color = '#f59e0b'
            else:
                color = '#ef4444'

            nodes.append({
                'id': node_id,
                'label': ticker,
                'type': 'stock',
                'ticker': ticker,
                'company': company,
                'signal': signal,
                'score': round(buy_pct, 1),
                'size': 45 if is_center else 30,
                'color': color,
                'isCenter': is_center,
            })

        def add_edge(from_id, to_id):
            edge_id = f"edge_{from_id}_{to_id}"
            if edge_id not in node_ids:
                node_ids.add(edge_id)
                edges.append({
                    'id': edge_id,
                    'from': from_id,
                    'to': to_id,
                })

        if stock:
            # Stock-centered graph
            stock_upper = stock.upper()
            stock_data = df[df['ticker'].str.upper() == stock_upper]

            if stock_data.empty:
                raise HTTPException(status_code=404, detail=f"Stock not found: {stock}")

            # Add center stock
            company = stock_data.iloc[0].get('company', '')
            add_stock_node(stock_upper, company, is_center=True)

            # Add connected themes
            stock_themes = stock_data['theme'].unique()
            for theme_name in stock_themes:
                add_theme_node(theme_name)
                add_edge(f"stock_{stock_upper}", f"theme_{theme_name}")

        elif theme:
            # Theme-centered graph
            add_theme_node(theme)

            # Get stocks in theme
            theme_stocks = df[df['theme'] == theme].sort_values('weight', ascending=False).head(15)

            for _, row in theme_stocks.iterrows():
                ticker = row['ticker']
                company = row.get('company', '')
                add_stock_node(ticker, company)
                add_edge(f"theme_{theme}", f"stock_{ticker}")

                # Depth 2: Add other themes for each stock
                if depth >= 2:
                    other_themes = df[df['ticker'] == ticker]['theme'].unique()
                    for other_theme in other_themes[:5]:
                        if other_theme != theme:
                            add_theme_node(other_theme)
                            add_edge(f"stock_{ticker}", f"theme_{other_theme}")

        else:
            # Default: Show all themes with connections
            themes = get_themes_dict(consolidated)

            # Add all theme nodes
            for theme_name, theme_info in themes.items():
                add_theme_node(theme_name)

            # Create edges between themes that share stocks
            theme_stocks = {}
            for theme_name in themes.keys():
                theme_df = df[df['theme'] == theme_name]
                theme_stocks[theme_name] = set(theme_df['ticker'].unique())

            # Find theme pairs with shared stocks
            theme_list = list(themes.keys())
            for i, theme1 in enumerate(theme_list):
                for theme2 in theme_list[i+1:]:
                    shared = theme_stocks.get(theme1, set()) & theme_stocks.get(theme2, set())
                    if len(shared) >= 2:
                        edges.append({
                            'id': f"edge_{theme1}_{theme2}",
                            'from': f"theme_{theme1}",
                            'to': f"theme_{theme2}",
                            'value': len(shared),
                            'title': f'{len(shared)} shared stocks'
                        })

        return {
            "success": True,
            "nodes": nodes,
            "edges": edges,
            "stats": {
                "node_count": len(nodes),
                "edge_count": len(edges),
                "stock_count": len([n for n in nodes if n['type'] == 'stock']),
                "theme_count": len([n for n in nodes if n['type'] == 'theme']),
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stock-themes")
async def get_stock_themes(name: str) -> Dict[str, Any]:
    """Get all themes for a specific stock"""
    try:
        df = load_theme_tickers()
        consolidated = load_consolidated()
        actionable = load_actionable_tickers()

        # Find stock by ticker or company name
        stock_data = df[df['ticker'].str.upper() == name.upper()]
        if stock_data.empty:
            stock_data = df[df['company'].str.contains(name, case=False, na=False)]

        if stock_data.empty:
            raise HTTPException(status_code=404, detail=f"Stock not found: {name}")

        ticker = stock_data.iloc[0]['ticker']
        company = stock_data.iloc[0].get('company', '')

        themes = []
        for _, row in stock_data.iterrows():
            theme_name = row['theme']
            theme_info = get_themes_dict(consolidated).get(theme_name, {})
            fiedler = safe_float(theme_info.get('fiedler', 0))

            themes.append({
                'theme': theme_name,
                'fiedler': round(fiedler, 3),
                'cohesion_level': get_cohesion_level(fiedler),
                'tier': theme_info.get('tier', 'Unknown'),
                'weight_in_theme': safe_float(row.get('weight', 0)),
            })

        # Sort by fiedler
        themes.sort(key=lambda x: x['fiedler'], reverse=True)

        return {
            'success': True,
            'stock_name': f"{company} ({ticker})" if company else ticker,
            'ticker': ticker,
            'market': 'NYSE/NASDAQ',
            'themes': themes,
            'theme_count': len(themes),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/theme-stocks")
async def get_theme_stocks(
    theme: str = Query(None, description="Theme name"),
    name: str = Query(None, description="Theme name (alias)"),
    limit: int = 20
) -> Dict[str, Any]:
    """Get all stocks for a specific theme"""
    try:
        theme_name = theme or name
        if not theme_name:
            raise HTTPException(status_code=400, detail="Theme name required")

        df = load_theme_tickers()
        consolidated = load_consolidated()
        actionable = load_actionable_tickers()

        # Find theme (case-insensitive)
        theme_data = df[df['theme'].str.lower() == theme_name.lower()]
        if theme_data.empty:
            raise HTTPException(status_code=404, detail=f"Theme not found: {theme_name}")

        theme_info = get_themes_dict(consolidated).get(theme_name, {})
        fiedler = safe_float(theme_info.get('fiedler', 0))

        stocks = []
        for _, row in theme_data.sort_values('weight', ascending=False).head(limit).iterrows():
            ticker = row['ticker']
            company = row.get('company', '')

            # Get signal data
            buy_pct = 50.0
            sell_pct = 25.0
            neutral_pct = 25.0
            signal = 'neutral'

            if not actionable.empty:
                ticker_data = actionable[actionable['ticker'] == ticker]
                if not ticker_data.empty:
                    score = safe_float(ticker_data.iloc[0].get('combined_score', 0))
                    buy_pct = min(100, max(0, score * 500))
                    sell_pct = max(0, 100 - buy_pct - 20)
                    neutral_pct = 100 - buy_pct - sell_pct

                    if buy_pct >= 70:
                        signal = 'strong_buy'
                    elif buy_pct >= 50:
                        signal = 'buy'
                    elif buy_pct >= 30:
                        signal = 'neutral'
                    else:
                        signal = 'avoid'

            stocks.append({
                'name': f"{company} ({ticker})" if company else ticker,
                'ticker': ticker,
                'market': 'NYSE/NASDAQ',
                'weight': safe_float(row.get('weight', 0)),
                'signal': signal,
                'buy_pct': round(buy_pct, 1),
                'signal_probability': {
                    'buy': round(buy_pct, 1),
                    'neutral': round(neutral_pct, 1),
                    'sell': round(sell_pct, 1),
                },
                'total_score': round(buy_pct / 100, 3),
            })

        return {
            'success': True,
            'theme': theme_name,
            'fiedler': round(fiedler, 3),
            'cohesion_level': get_cohesion_level(fiedler),
            'tier': theme_info.get('tier', 'Unknown'),
            'stock_count': len(theme_data),
            'stocks': stocks,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
