import json
from typing import List, Dict, Any, Tuple


def load_venues(path: str = "venues.json") -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def filter_by_theme(venues: List[Dict[str, Any]], theme: str) -> List[Dict[str, Any]]:
    theme = (theme or "").strip().lower()
    if not theme:
        return venues
    return [v for v in venues if theme in [t.lower() for t in v.get("themes", [])]]


def filter_by_budget_tier(venues: List[Dict[str, Any]], max_price_tier: int) -> List[Dict[str, Any]]:
    try:
        max_price_tier = int(max_price_tier)
    except Exception:
        return venues
    return [v for v in venues if int(v.get("price_tier", 9)) <= max_price_tier]


def filter_by_must_haves(venues: List[Dict[str, Any]], must_haves: List[str]) -> List[Dict[str, Any]]:
    mh = [m.strip().lower() for m in must_haves if m.strip()]
    if not mh:
        return venues

    filtered = []
    for v in venues:
        hay = f"{v.get('name','')} {v.get('category','')} {' '.join(v.get('vibes', []))} {' '.join(v.get('themes', []))}".lower()
        if any(token in hay for token in mh):
            filtered.append(v)
    return filtered


def _theme_boost(venue: Dict[str, Any], theme: str) -> float:
    """Stronger boost if venue explicitly supports the chosen theme."""
    if not theme:
        return 0.0
    theme = theme.lower()
    themes = [t.lower() for t in venue.get("themes", [])]
    return 1.0 if theme in themes else 0.0


def _vibe_score(venue: Dict[str, Any], vibe_weights: Dict[str, float]) -> float:
    score = 0.0
    for vibe in venue.get("vibes", []):
        score += float(vibe_weights.get(vibe, 0.0))
    return score


def score_venue(
    venue: Dict[str, Any],
    vibe_weights: Dict[str, float],
    theme: str,
    weights: Tuple[float, float, float],
) -> float:
    """
    Deterministic scoring: vibes + theme relevance + budget friendliness.
    weights = (w_vibe, w_theme, w_budget)
    """
    w_vibe, w_theme, w_budget = weights

    vibe = _vibe_score(venue, vibe_weights)
    theme_rel = _theme_boost(venue, theme)

    # Budget friendliness: lower price_tier gets a slight advantage inside the user's budget ceiling
    pt = float(venue.get("price_tier", 3))
    budget_friendliness = max(0.0, (5.0 - pt) / 4.0)  # 1->1.0, 4->0.25-ish

    return (vibe * w_vibe) + (theme_rel * w_theme) + (budget_friendliness * w_budget)


def rank_venues(
    venues: List[Dict[str, Any]],
    vibe_weights: Dict[str, float],
    theme: str,
    weights: Tuple[float, float, float] = (0.55, 0.35, 0.10),
) -> List[Dict[str, Any]]:
    scored = []
    for v in venues:
        v2 = dict(v)
        v2["score"] = score_venue(v2, vibe_weights, theme, weights)
        scored.append(v2)
    return sorted(scored, key=lambda x: x["score"], reverse=True)


def pick_top_by_category(
    ranked: List[Dict[str, Any]],
    category_targets: List[str],
    limit_per_category: int = 1,
    max_total: int = 6,
) -> List[Dict[str, Any]]:
    """
    Build an itinerary by category order (ex: brunch, activity, dinner, nightlife, transport).
    Deterministic: take top N per category in order.
    """
    picked = []
    for cat in category_targets:
        cat_matches = [v for v in ranked if v.get("category") == cat]
        picked.extend(cat_matches[:limit_per_category])
        if len(picked) >= max_total:
            break
    return picked[:max_total]


def alternatives(ranked: List[Dict[str, Any]], exclude_names: List[str], k: int = 5) -> List[Dict[str, Any]]:
    excl = set([n.lower() for n in exclude_names])
    alts = [v for v in ranked if v.get("name", "").lower() not in excl]
    return alts[:k]

