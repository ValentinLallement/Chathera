import re

def glb_url_to_readyplayerme_headshot(glb_url: str) -> str:
    match = re.search(r'/([0-9a-f]{24})\.glb$', glb_url)
    if not match:
        raise ValueError("L'URL GLB n'a pas le format ReadyPlayerMe attendu (ex: .../{id}.glb).")
    user_id = match.group(1)
    if len(user_id) != 24 or not all(c in '0123456789abcdef' for c in user_id):
        raise ValueError("L'ID extrait n'est pas un ObjectID valide (24 caractères hexadécimaux).")
    return f"https://models.readyplayer.me/{user_id}.png"