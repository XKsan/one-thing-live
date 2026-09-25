import os
import json
from pathlib import Path
from dotenv import load_dotenv
from google import genai

# ==============================
# ONE THING DAILY ENGINE V1.1
# Mobile One Screen Edition
# ==============================

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise Exception("Missing GEMINI_API_KEY")


client = genai.Client(
    api_key=API_KEY
)


BASE_DIR = Path(__file__).resolve().parent.parent

CONTENT_FILE = BASE_DIR / "content" / "today.json"


PROMPT = """
You are the content engine of ONE THING.

Create ONE extraordinary discovery for a mobile app.

The user only spends 60 seconds.

The output must be:
- simple
- mysterious
- beautiful
- emotionally powerful
- suitable for a premium minimalist mobile experience


STRICT FORMAT:

Return ONLY valid JSON.

{
"id":"",
"category":"",
"title_en":"",
"title_zh":"",
"reveal_en":"",
"reveal_zh":"",
"meaning_en":"",
"meaning_zh":"",
"source":"",
"visual":{
"theme":"",
"color":"",
"motion":""
}
}


CONTENT RULES:

Title:
- English title maximum 6 words
- Chinese title maximum 12 Chinese characters

Reveal:
- English maximum 25 words
- Chinese maximum 40 characters

Meaning:
- English maximum 35 words
- Chinese maximum 70 characters

Source:
- Keep very short.

Visual:
- Describe only visual atmosphere.

Do NOT:
- write articles
- write explanations
- create paragraphs
- use academic language
- add unnecessary details

ONE THING is a single moment of discovery, not a long article.

STRICT MOBILE DISPLAY RULES:

- Everything must fit on one phone screen.
- Title: maximum 5 words.
- English discovery: maximum 2 short sentences.
- Chinese discovery: maximum 2 short sentences.
- Meaning must be concise.
- Never create paragraphs.
- Never add explanations.

Categories:
COSMOS
NATURE
SCIENCE
HUMAN
ART
CULTURE
TIME
LIFE

Choose one.
"""


response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=PROMPT
)


text = response.text.strip()


# remove markdown fences if Gemini adds them

if text.startswith("```"):
    text = text.replace("```json", "")
    text = text.replace("```", "")

text = text.strip()


try:
    data = json.loads(text)

except Exception:

    print("JSON ERROR")
    print(text)
    raise


# ==============================
# Quality Control
# ==============================

score = 100


checks = [

    len(data.get("title",{}).get("en","")) <= 30,

    len(data.get("title",{}).get("zh","")) <= 15,


    len(data.get("reveal",{}).get("en","")) <= 90,

    len(data.get("reveal",{}).get("zh","")) <= 60,


    len(data.get("meaning",{}).get("en","")) <= 120,

    len(data.get("meaning",{}).get("zh","")) <= 80,

]


score -= checks.count(False) * 15


if score < 60:

    print("CONTENT QUALITY TOO LOW")
    print(json.dumps(data,indent=2,ensure_ascii=False))
    raise Exception("Quality check failed")


# ==============================
# Save
# ==============================


with open(
    CONTENT_FILE,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        data,
        f,
        ensure_ascii=False,
        indent=2
    )


print()
print("==============================")
print("ONE THING UPDATED")
print("==============================")
print()

print(
    json.dumps(
        data,
        ensure_ascii=False,
        indent=2
    )
)

print()
print("QUALITY SCORE:",score)