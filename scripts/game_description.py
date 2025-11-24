import random

def build_game_description(game_entry):
    \"\"\"
    game_entry is a dict from load_game_library()
    {
        "game_id": ...,
        "game_name": ...,
        "ios_link": ...,
        "facts": [...],
        "ratio": int
    }
    \"\"\"

    game_name = game_entry["game_name"]
    ios_link = game_entry["ios_link"]
    facts = game_entry["facts"]

    chosen_fact = random.choice(facts)

    # Build natural-sounding line for your metadata description
    description = (
        f"Try out {game_name}! {chosen_fact} "
        f"Play now: {ios_link}"
    )

    return description
