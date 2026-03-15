from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from langgraph.prebuilt import create_react_agent
from langchain.tools import tool
import requests

load_dotenv()
# In llm.py
def generate_style(website_content):
    style_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a CSS expert. Create a modern, high-quality CSS stylesheet to improve the look of an old website snapshot. Return ONLY the CSS code."),
        ("user", "Here is a sample of the HTML content: {content}")
    ])
    
    # We send only a small part of the HTML to save tokens
    chain = style_prompt | llm | str_parser
    return chain.invoke({"content": website_content[:2000]})

str_parser = StrOutputParser()

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.5
)

def archieveAnalyse(website, date):
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", "You are a helphul assistant that explains to me the context of old versions os website for information purpose"),
        ("user", "Explain {website} version from {date}")
    ])

    chain = prompt_template | llm| str_parser

    result = chain.invoke({"website":website, "date": date})
    return result
    #print(result)