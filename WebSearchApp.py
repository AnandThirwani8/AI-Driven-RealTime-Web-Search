#---------------------------------------------- Imports ----------------------------------------------
# Import necessary libraries and modules.
import os
import re
import requests
import streamlit as st
from markdownify import markdownify
from requests.exceptions import RequestException

import google.generativeai as genai
from smolagents import CodeAgent, ManagedAgent, LiteLLMModel, tool, DuckDuckGoSearchTool

#---------------------------------------------- Side Bar (Key) ----------------------------------------------
st.set_page_config(page_title="Chat with Web Search", page_icon="🌐")

# Create a sidebar for entering the Gemini API key.
with st.sidebar:
    st.markdown("# Enter your Gemini API Key here:")
    gemini_api_key = st.sidebar.text_input("Gemini API Key", type="password")
    "[🔑 Get your Gemini API key](https://ai.google.dev/gemini-api/docs)"
    "[👨‍💻 View the source code](https://github.com/AnandThirwani8/AI-Driven-RealTime-Web-Search/)"
    "[🤝 Let's Connect](https://www.linkedin.com/in/anandthirwani/)"

    st.markdown("---")
    st.markdown("# About")
    st.markdown(
        "🚀 Demonstration of a multi-agent AI system 🤖 designed to answer factual questions by querying the internet. "
        "❓ Ask anything factual, and watch the agents collaborate to find the best answer!"
    )
    st.markdown(
        "This tool is a work in progress. "
        "You can contribute to the project on [GitHub](https://github.com/AnandThirwani8/AI-Driven-RealTime-Web-Search/) "  
        "with your feedback and suggestions💡"
    )


#---------------------------------------------- Define LLM ----------------------------------------------
# Set up the language model using Gemini API.
# if not gemini_api_key:
model_name = "gemini-1.5-flash"
model = LiteLLMModel(model_id=f"gemini/{model_name}", api_key = gemini_api_key)
genai.configure(api_key = gemini_api_key)
llm = genai.GenerativeModel(model_name=f"{model_name}")

#---------------------------------------------- Define Agents ----------------------------------------------
@tool
def visit_webpage(url: str) -> str:
    """Visits a webpage at the given URL and returns its content as a markdown string.

    Args:
        url: The URL of the webpage to visit.

    Returns:
        URL of the webpage and The content of the webpage converted to Markdown, or an error message if the request fails.
    """
    try:
        # Send a GET request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes

        # Convert the HTML content to Markdown
        markdown_content = markdownify(response.text).strip()

        # Remove multiple line breaks
        markdown_content = re.sub(r"\n{3,}", "\n\n", markdown_content)

        return url, markdown_content

    except RequestException as e:
        return f"Error fetching the webpage: {str(e)}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"

# Define agents for web search and content extraction.
web_agent = CodeAgent(tools=[DuckDuckGoSearchTool(), visit_webpage], model=model)
managed_web_agent = ManagedAgent(agent=web_agent, name="search", 
                                 description="""Runs web searches for you.Give it your query as an argument.""")

manager_agent = CodeAgent(tools=[], model=model, 
                          managed_agents=[managed_web_agent],
                          additional_authorized_imports=["re", "json", "requests"])

# Define function to perform question-and-answer web searches.
def QnA_Web_Search(query):
    out = manager_agent.run(f"""{query}'. You must provide source URLs with your final answer""")

    prompt = 'Reformat the following text into bullet points. Add URLs in a separate REFERENCES section. Do not add any additional information.'
    input_data = [{"text": prompt},
                  {"text": str(out)}]
    result = llm.generate_content(input_data).text
    return result

#---------------------------------------------- Chat UI ----------------------------------------------
# Set up the web application interface.
st.title("🌐 Chat with Web Search")
st.caption("🚀 Powered by Google Gemini and HuggingFace SmolAgents")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How may I help you ?"}]

# Display chat messages
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Handle user input
if query := st.chat_input():
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": query})
    st.chat_message("user").write(query)

    # Generate response 
    with st.spinner("Thinking..."):

        if not gemini_api_key:
            st.warning('Please enter your API key!', icon='⚠')
            st.stop()
        else:
            response = QnA_Web_Search(query)

        msg = response

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": msg})
    st.chat_message("assistant").write(msg)

