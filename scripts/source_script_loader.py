import gspread
from oauth2client.service_account import ServiceAccountCredentials
from typing import List, Dict, Any
import unicodedata


def normalize(v: Any) -> str:
    if v is None:
        return ""
    if not isinstance(v, str):
        v = str(v)
    v = unicodedata.normalize("NFKC", v)
    v = v.replace("\u200b", "").replace("\u200c", "").replace("\u200d", "")
    return v.strip()


def get_client():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets.readonly",
        "https://www.googleapis.com/auth/drive.readonly",
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        "config/service_account.json", scope
    )
    return gspread.authorize(creds)


def load_source_scripts() -> List[Dict[str, Any]]:
    gc = get_client()
    sheet = gc.open("story-generator")
    ws = sheet.worksheet("source_scripts")
    rows = ws.get_all_records()

    cleaned = []
    for r in rows:
        out = {k.strip(): normalize(v) for k, v in r.items()}

        # parse numbers
        try:
            out["virality_forecast_score"] = float(out.get("virality_forecast_score", 0) or 0)
        except:
            out["virality_forecast_score"] = 0.0

        try:
            out["views_to_likes_ratio"] = float(out.get("views_to_likes_ratio", 0) or 0)
        except:
            out["views_to_likes_ratio"] = 0.0

        cleaned.append(out)

    return cleaned
