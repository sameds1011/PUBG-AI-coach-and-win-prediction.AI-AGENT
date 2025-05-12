import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# .env dosyasından API anahtarını yükle
load_dotenv()

# OpenAI API yapılandırması
def get_llm():
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY bulunamadı. Lütfen .env dosyasını kontrol edin.")

    return ChatOpenAI(
        model="gpt-4o",
        api_key=openai_api_key,
        temperature=0.7
    )