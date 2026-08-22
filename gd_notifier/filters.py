"""Logic for deciding whether a live stream is a level-request stream."""


def is_level_request_stream(stream, keywords, require_gd_category, gd_category_name):
    if require_gd_category:
        game_name = (stream.get("game_name") or "").strip().lower()
        if game_name != gd_category_name.strip().lower():
            return False

    title = (stream.get("title") or "").lower()
    return any(keyword.lower() in title for keyword in keywords)
