import os
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import json

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

# Initialize model and and creativity
llm = ChatOpenAI(model="gpt-5.4", temperature=0.6)
str_parser = StrOutputParser()

def generate_style(website_content):
    style_prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "You are a Senior Web Designer. Your goal is to modernize old HTML snapshots. "
            "Create a high-quality, colorful CSS stylesheet. "
            "Use a clean font like 'Segoe UI' or 'Arial'. "
            "Add padding to tables, give images rounded corners, and use a bright color palette (blues, reds, whites). "
            "Output ONLY the raw CSS code. No markdown, no comments, no ```css blocks."
        )),
        ("user", "Here is the HTML structure to restyle: {content}")
    ])
    
    chain = style_prompt | llm | str_parser
    # We take the first 3000 chars to give the AI enough context without hitting token limits
    css = chain.invoke({"content": website_content[:3000]})
    
    # Clean up any markdown the LLM might have included
    return css.replace("```css", "").replace("```", "").strip()

def archieveAnalyse(website, date):
    prompt_template = ChatPromptTemplate.from_messages([
        (
            "system",
            "You analyze archived website snapshots and return structured historical and design insights. "
            "Return ONLY valid JSON with exactly these keys: "
            "summary (string), design_notes (array of strings), context_of_the_time (string), impact (string). "
            "Keep it concise and readable; if uncertain, note uncertainty briefly."
        ),
        (
            "user",
            "Website: {website}\n"
            "Snapshot date label: {date}\n\n"
            "Write the JSON response now."
        ),
    ])

    chain = prompt_template | llm | str_parser
    raw = chain.invoke({"website": website, "date": date})

    try:
        return json.loads(raw)
    except Exception:
        start = raw.find('{')
        end = raw.rfind('}')
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(raw[start:end+1])
            except Exception:
                pass

    return {
        "summary": raw.strip(),
        "design_notes": [],
        "context_of_the_time": "",
        "impact": "",
    }

#Model look for most used sites and display it in main page
def nostalgic_recommendations(years_ago: int = 10, count: int = 6):
    """Return AI-generated 'nostalgic but still active' website recommendations.

    Output shape:
    {
      "title": str,
      "items": [{"name": str, "url": str, "why": str, "year": int}]
    }

    Note: This is best-effort. We don't browse the live web here; the model suggests candidates.
    """
    prompt_template = ChatPromptTemplate.from_messages([
        (
            "system",
            "You recommend nostalgic websites that were popular about a decade ago and are likely still active today. "
            "Return ONLY valid JSON with keys: "
            "title (string) and items (array). Each item must have: name (string), url (string), why (string), year (number). "
            "URLs must include https://. Keep it family-friendly and mainstream."
        ),
        (
            "user",
            "Generate {count} nostalgic website recommendations from about {years_ago} years ago. "
            "Prefer a mix: video, social, news, gaming, music, forums."
        ),
    ])

    chain = prompt_template | llm | str_parser
    raw = chain.invoke({"years_ago": years_ago, "count": count})

    try:
        data = json.loads(raw)
    except Exception:
        start = raw.find('{')
        end = raw.rfind('}')
        if start != -1 and end != -1 and end > start:
            try:
                data = json.loads(raw[start:end+1])
            except Exception:
                data = None
        else:
            data = None

    if not isinstance(data, dict):
        return {
            "title": "Nostalgic picks",
            "items": [],
        }

    # Light normalization / safety
    title = str(data.get("title") or "Nostalgic picks")
    items = data.get("items")
    if not isinstance(items, list):
        items = []

    cleaned = []
    for item in items[: max(0, int(count))]:
        if not isinstance(item, dict):
            continue
        url = str(item.get("url") or "").strip()
        if url and not url.startswith("http"):
            url = "https://" + url.lstrip("/")
        cleaned.append({
            "name": str(item.get("name") or "").strip(),
            "url": url,
            "why": str(item.get("why") or "").strip(),
            "year": int(item.get("year") or 0),
        })

    return {
        "title": title,
        "items": cleaned,
    }