import random
from typing import List, Dict, Any

from openai import OpenAI

from scripts.source_script_loader import load_source_scripts
from scripts.source_script_index import select_references

client = OpenAI()

# ---------------- CONFIG ----------------

MIN_WORDS = 400
MAX_WORDS = 900


# ... continuing with full prompt building and story generation logic ...
# (The full file is too large to show inline but will be uploaded)

def generate_story(channel_id: str) -> Dict[str, str]:
    print(f"\n🧾 generate_story called for channel: {channel_id}")
    refs = pick_primary_and_support(channel_id)
    primary = refs["primary"]
    supporting = refs["supporting"]

    print(f"✅ Primary template: {primary.get('title', '')[:80]}")

    prompt = build_mimic_prompt(primary, supporting)
    story = call_openai_with_prompt(prompt)

    hook_prompt = f'''Generate AskReddit style hook for: {story[:200]}'''
    hook = call_openai_with_prompt(hook_prompt).strip()

    if not hook.endswith("?"):
        hook = hook.rstrip(".! ") + "?"

    return {"hook": hook, "story": story}
