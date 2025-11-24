import random
from typing import List, Dict, Any


def select_primary_reference(all_scripts: List[Dict[str, Any]], channel_identity: str):
    # filter by channel_identity match inside tone_keywords or summary
    aligned = []
    identity_lower = channel_identity.lower()

    for r in all_scripts:
        tone = r.get("tone_keywords", "").lower()
        summ = r.get("summary", "").lower()
        if identity_lower in tone or identity_lower in summ:
            aligned.append(r)

    # fallback: top 20 by virality score
    pool = aligned if aligned else sorted(
        all_scripts, key=lambda r: r.get("virality_forecast_score", 0), reverse=True
    )[:20]

    # weighted selection by virality score × (1 / ratio)
    def weight(r):
        v = float(r.get("virality_forecast_score", 0))
        ratio = float(r.get("views_to_likes_ratio", 1))
        return max(v / (ratio + 1e-6), 0.01)

    return random.choices(pool, weights=[weight(r) for r in pool], k=1)[0]


def select_supporting_references(all_scripts: List[Dict[str, Any]], count=3):
    if len(all_scripts) <= count:
        return all_scripts

    return random.sample(all_scripts, count)


def select_references(all_scripts: List[Dict[str, Any]], channel_identity: str):
    primary = select_primary_reference(all_scripts, channel_identity)
    supporting = select_supporting_references(all_scripts, 3)
    return primary, supporting
