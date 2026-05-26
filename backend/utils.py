import json


def parse_json_list(text: str | None) -> list[str]:
    """Parse a JSON-encoded list string, with fallback to comma/slash splitting."""
    if not text:
        return []
    try:
        result = json.loads(text)
        return result if isinstance(result, list) else []
    except (json.JSONDecodeError, ValueError):
        # Fallback: try " / " separated (scraper format), then comma
        if " / " in text:
            return [x.strip() for x in text.split(" / ") if x.strip()]
        return [x.strip() for x in text.strip("[]").replace("'", "").split(",") if x.strip()]
