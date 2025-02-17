import os
import time
import logging
import pandas as pd
import streamlit as st
from prompts import prompt_keywords, prompt_query
from duckduckgo_search import DDGS
from googlesearch import search
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
from langchain_ollama import OllamaLLM

os.environ['GOOGLE_METADATA_DISABLED'] = 'true'

load_dotenv()

logging.basicConfig(level=logging.INFO)

def log_message(message):
    logging.info(message)
    st.write(message)

def get_model(llm_engine, llm_model_name=None):
    if llm_engine == "Gemini":
        return ChatGoogleGenerativeAI(
            model="gemini-pro",
            google_api_key=os.getenv('GEMINI_API_KEY'),
            temperature=0.1
        )
    elif llm_engine == "Local Ollama":
        return OllamaLLM(model=llm_model_name)

def get_content(result, llm_engine):
    if llm_engine == "Gemini":
        return result.content.split(',')
    else:
        return result.split(',')

def generate_keywords(topic, llm_engine, llm_model_name):
    prompt = PromptTemplate.from_template(prompt_keywords)
    llm = get_model(llm_engine, llm_model_name)
    chain = prompt | llm
    result = chain.invoke({"topic": topic})
    return [keyword.strip() for keyword in get_content(result, llm_engine)]

def generate_queries(topic, keywords, llm_engine, llm_model_name):
    prompt = PromptTemplate.from_template(prompt_query)
    llm = get_model(llm_engine, llm_model_name)
    chain = prompt | llm
    result = chain.invoke({"topic": topic, "keywords": keywords})
    return [q.strip() for q in get_content(result, llm_engine)]

def search_duckduckgo(query, max_results=10):
    with DDGS(verify=False) as ddgs:
        return [
            {
                'Title': result.get('title'),
                'URL': result.get('href'),
                'Description': result.get('body')
            }
            for result in ddgs.text(query, max_results=max_results)
        ]

def search_google(query, max_results=10):
    return [
        {
            'Title': result.title,
            'URL': result.url,
            'Description': result.description
        }
        for result in search(query, num_results=max_results, advanced=True)
    ]

def search_prior_art(queries, search_engine, k):
    full_result = []
    for query in queries:
        log_message(f"Processing Query: \n{query}")
        if search_engine in ('duckduckgo', 'both'):
            full_query = f"site:patents.google.com {query}"
            results = search_duckduckgo(full_query, k)
            full_result.extend(results)
            log_message(f"{len(results)} results found for DDGS")
        if search_engine in ('google', 'both'):
            full_query = f"https://patents.google.com?q={query}"
            results = search_google(full_query, k)
            full_result.extend(results)
            log_message(f"{len(results)} results found for GoogleSearch")
        time.sleep(2)

    log_message(f"{len(full_result)} results found in total")
    return pd.DataFrame(full_result).query("URL.str.startswith('https://patents.google.com/patent/')", engine='python')

st.title("Patent Search and Analysis Tool")
st.write("Use this app to search for prior art related to your idea using DuckDuckGo and Google Patents.")

topic = st.text_area("Enter a description of your idea or topic:", "A new method for efficient solar energy conversion using nanotechnology.")

st.sidebar.header("Settings")
top_k_results = st.sidebar.number_input("Number of Results per Query", min_value=1, max_value=20, value=10, step=1)
search_engine = st.sidebar.radio("Select Search Engine", options=['google', 'duckduckgo', 'both'], index=0)
llm_engine = st.sidebar.radio("Select LLM Type", options=['Gemini', 'Local Ollama'], index=0)

if llm_engine == 'Gemini':
    llm_model_name = ""
    api_key_input = st.sidebar.text_input("Google Gemini API Key", type="password")
    if api_key_input and api_key_input != os.getenv('GEMINI_API_KEY'):
        os.environ['GEMINI_API_KEY'] = api_key_input
elif llm_engine == 'Local Ollama':
    llm_model_name = st.sidebar.text_input("Ollama Model Name", value="llama3.2:latest")
    api_key_input = ""

if st.button("Search for Patents"):
    if not topic.strip():
        st.error("Please enter a valid topic description.")
    else:
        try:
            st.info("Generating keywords...")
            keywords = generate_keywords(topic, llm_engine, llm_model_name)
            st.success("Keywords generated successfully!")
            st.write(keywords)

            st.info("Generating search queries...")
            queries = generate_queries(topic, keywords, llm_engine, llm_model_name)
            st.success("Queries generated successfully!")
            st.write(queries)

            st.info(f"Searching for prior art... top: {top_k_results}")
            prior_arts = search_prior_art(queries, search_engine, top_k_results)
            st.success("Search completed!")

            if not prior_arts.empty:
                st.subheader("Search Results")
                for _, row in prior_arts.iterrows():
                    st.write(f"### [{row['Title']}]({row['URL']})\n{row['Description']}")
            else:
                st.warning("No results found for the given queries.")

        except Exception as e:
            st.error(f"An error occurred: {e}")
