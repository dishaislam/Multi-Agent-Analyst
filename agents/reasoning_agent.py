import os
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_mistralai import ChatMistralAI

load_dotenv()

def run_reasoning(summary_text):
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        print(" Missing MISTRAL_API_KEY in .env file")
        return "API key missing"

    try:
        model = ChatMistralAI(model="mistral-small", api_key=api_key)

        prompt = PromptTemplate.from_template("""
        You are an intelligent business analyst AI.
        Analyze the following yearly sales summary and explain WHY performance changed.
        Focus on causes, not just numbers.
        Include observations about revenue, profit, customers, and regional differences.

        Summary:
        {summary_text}
        """)

        chain = prompt | model | StrOutputParser()

        print("Running Mistral reasoning...")
        result = chain.invoke({"summary_text": summary_text})
        print("Reasoning completed.")
        return result

    except Exception as e:
        print(f"Mistral reasoning failed: {e}")
        return "Reasoning failed due to API or library issue."
