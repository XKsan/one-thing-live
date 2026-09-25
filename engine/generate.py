from google import genai
from dotenv import load_dotenv

import json
import os


load_dotenv()


client = genai.Client(
    api_key=os.environ["GEMINI_API_KEY"]
)


prompt = """

Create ONE THING.

A single daily discovery.

It must feel:

- mysterious
- beautiful
- surprising
- meaningful


Return ONLY JSON.


Format:


{
"id":"",
"category":"",

"title":{
"en":"",
"zh":""
},

"reveal":{
"en":"",
"zh":""
},

"meaning":{
"en":"",
"zh":""
},

"source":"",

"visual":{
"theme":"",
"color":""
}

}

"""


response = client.models.generate_content(

    model="gemini-2.5-flash",

    contents=prompt

)



text=response.text


text=text.replace(
"```json",
""
).replace(
"```",
""
).strip()



data=json.loads(text)



if not data.get("title"):
    raise Exception(
        "Invalid content"
    )



with open(
"content/today.json",
"w",
encoding="utf-8"
) as f:

    json.dump(
        data,
        f,
        ensure_ascii=False,
        indent=2
    )


print(
"ONE THING UPDATED"
)
