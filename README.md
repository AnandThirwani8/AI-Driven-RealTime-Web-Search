# AI-Driven-RealTime-Web-Search
Demonstration of a multi-agent AI system designed to answer factual questions by querying the internet. The system ensures accurate, up-to-date answers by querying the internet and providing source URLs for transparency and trust.

## Prerequisites
To run this repository, ensure you have the following:
- Conda 
- Google Gemini API key

## Setup
```bash
git clone https://github.com/AnandThirwani8/AI-Driven-RealTime-Web-Search.git
cd AI-Driven-RealTime-Web-Search

conda create --name WebSearchChat python=3.10
conda activate WebSearchChat
pip install -r requirements.txt

streamlit run WebSearchApp.py
```
