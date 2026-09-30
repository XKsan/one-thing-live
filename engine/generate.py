import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

from google import genai
from google.genai import types


ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "content" / "today.json"

MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


CATEGORIES = [
    "COSMOS",
    "NATURE",
    "SCIENCE",
    "HUMAN",
    "ART",
    "CULTURE",
    "TIME",
    "LIFE",
]


THEMES = [
    "cosmos",
    "nature",
    "science",
    "human",
    "art",
    "culture",
    "time",
    "life",
]


SCHEMA = {
    "type": "object",
    "properties": {
        "category": {
            "type": "string",
            "enum": CATEGORIES,
        },
        "title_en": {
            "type": "string",
        },
        "title_zh": {
            "type": "string",
        },
        "reveal_en": {
            "type": "string",
        },
        "reveal_zh": {
            "type": "string",
        },
        "meaning_en": {
            "type": "string",
        },
        "meaning_zh": {
            "type": "string",
        },
        "visual": {
            "type": "object",
            "properties": {
                "theme": {
                    "type": "string",
                    "enum": THEMES,
                },
                "color": {
                    "type": "string",
                },
                "motion": {
                    "type": "string",
                },
            },
            "required": [
                "theme",
                "color",
                "motion",
            ],
        },
    },
    "required": [
        "category",
        "title_en",
        "title_zh",
        "reveal_en",
        "reveal_zh",
        "meaning_en",
        "meaning_zh",
        "visual",
    ],
}


PROMPT = """
You are the editorial intelligence behind ONE THING.

ONE THING gives a person exactly ONE fascinating thing worth knowing each day.

This is NOT a news feed.
This is NOT trivia.
This is NOT motivational content.
This is NOT generic educational copy.

The discovery should create a genuine:
"I didn't know that."

Choose one specific, surprising, intellectually interesting fact,
phenomenon, observation, scientific idea, cultural detail,
natural phenomenon, historical detail, artistic insight, or
counterintuitive fact.

Editorial standard:
- Prefer facts with a strong "wait, really?" effect.
- Avoid common facts.
- Avoid internet clichés.
- Avoid motivational language.
- Avoid sensationalism.
- Avoid unverifiable claims.
- Avoid fake precision.
- Avoid repeating the obvious.
- Do not explain everything.
- The experience should feel like discovering one small door
  into a much larger world.

Writing:
- title_en: 2–7 words.
- title_zh: concise natural Chinese title.
- reveal_en: 1–2 short sentences, maximum 45 words.
- reveal_zh: natural Chinese translation/adaptation, maximum 55 Chinese characters where practical.
- meaning_en: 1 short sentence, maximum 28 words.
- meaning_zh: 1 short sentence, concise and natural.

The meaning is NOT a moral lesson.
It should reveal why this fact changes the way we see something.

Visual:
Return one controlled theme and one valid six-digit hexadecimal color.
Motion must be a short visual direction, not a paragraph.

Do not include markdown.
Do not include commentary.
Return JSON only.
"""


def clean_text(value, max_chars):
    value = str(value or "").strip()
    value = re.sub(r"\s+", " ", value)
    return value[:max_chars].strip()


def validate(data):
    if not isinstance(data, dict):
        raise ValueError("Generated result is not an object.")

    required = [
        "category",
        "title_en",
        "title_zh",
        "reveal_en",
        "reveal_zh",
        "meaning_en",
        "meaning_zh",
        "visual",
    ]

    for key in required:
        if key not in data:
            raise ValueError(f"Missing field: {key}")

    if data["category"] not in CATEGORIES:
        raise ValueError(
            f"Invalid category: {data['category']}"
        )

    visual = data["visual"]

    if not isinstance(visual, dict):
        raise ValueError("visual must be an object.")

    if visual.get("theme") not in THEMES:
        raise ValueError(
            f"Invalid visual theme: {visual.get('theme')}"
        )

    color = str(visual.get("color", "")).strip()

    if not re.fullmatch(r"#[0-9a-fA-F]{6}", color):
        raise ValueError(
            f"Invalid visual color: {color}"
        )

    fields = {
        "title_en": 100,
        "title_zh": 100,
        "reveal_en": 360,
        "reveal_zh": 240,
        "meaning_en": 220,
        "meaning_zh": 180,
    }

    for key, limit in fields.items():
        value = data.get(key)

        if not isinstance(value, str):
            raise ValueError(
                f"{key} must be a string."
            )

        if not value.strip():
            raise ValueError(
                f"{key} cannot be empty."
            )

        if len(value) > limit:
            raise ValueError(
                f"{key} is too long: "
                f"{len(value)} > {limit}"
            )

    if not isinstance(
        visual.get("motion"),
        str
    ):
        raise ValueError(
            "visual.motion must be a string."
        )

    return True


def build_final(data):
    category = data["category"]

    theme = data["visual"]["theme"]
    color = data["visual"]["color"]
    motion = clean_text(
        data["visual"]["motion"],
        100,
    )

    now = datetime.now(
        timezone.utc
    )

    date_id = now.strftime(
        "%Y%m%d"
    )

    return {
        "id": f"OT-{date_id}-{category}",
        "category": category,

        "title_en": clean_text(
            data["title_en"],
            100,
        ),

        "title_zh": clean_text(
            data["title_zh"],
            100,
        ),

        "reveal_en": clean_text(
            data["reveal_en"],
            360,
        ),

        "reveal_zh": clean_text(
            data["reveal_zh"],
            240,
        ),

        "meaning_en": clean_text(
            data["meaning_en"],
            220,
        ),

        "meaning_zh": clean_text(
            data["meaning_zh"],
            180,
        ),

        "visual": {
            "theme": theme,
            "color": color,
            "motion": motion,
        },

        "generated_at": now.isoformat(),
    }


def main():
    api_key = os.getenv(
        "GEMINI_API_KEY"
    )

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not set."
        )

    print("=" * 70)
    print("ONE THING DAILY GENERATOR")
    print("=" * 70)
    print(f"Model: {MODEL}")
    print(f"Output: {OUTPUT}")

    client = genai.Client(
        api_key=api_key
    )

    print("\nGenerating ONE THING...")

    response = client.models.generate_content(
        model=MODEL,
        contents=PROMPT,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=SCHEMA,
            temperature=1.0,
        ),
    )

    raw = response.text.strip()

    if not raw:
        raise RuntimeError(
            "Gemini returned empty output."
        )

    print("\nGemini response received.")

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "Gemini returned invalid JSON."
        ) from exc

    validate(data)

    final = build_final(data)

    # Validate the final normalized object too.
    validate(final)

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temp = OUTPUT.with_suffix(
        ".tmp"
    )

    temp.write_text(
        json.dumps(
            final,
            ensure_ascii=False,
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )

    temp.replace(OUTPUT)

    print("\n" + "=" * 70)
    print("GENERATION SUCCESS")
    print("=" * 70)
    print(
        f"ID:       {final['id']}"
    )
    print(
        f"Category: {final['category']}"
    )
    print(
        f"Title EN: {final['title_en']}"
    )
    print(
        f"Title ZH: {final['title_zh']}"
    )
    print(
        f"Theme:    {final['visual']['theme']}"
    )
    print(
        f"Color:    {final['visual']['color']}"
    )
    print(
        f"Written:  {OUTPUT}"
    )
    print("=" * 70)


if __name__ == "__main__":
    main()
