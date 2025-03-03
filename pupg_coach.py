import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from crewai import Agent, Task, Crew

# 📌 API Anahtarını Yükle
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("⚠️ API anahtarı bulunamadı! Lütfen .env dosyanızı kontrol edin.")

# 🧠 OpenAI Chat Modelini Tanımla
llm = ChatOpenAI(temperature=0.7, model_name="gpt-4", openai_api_key=OPENAI_API_KEY)

# 🔹 Prompt Template Tanımla
coach_prompt = PromptTemplate(
    input_variables=["kills", "damage", "walk_distance", "weapons"],
    template="""
    Sen bir PUBG koçusun. Oyuncunun istatistikleri aşağıda verilmiştir:
    - Öldürme Sayısı: {kills}
    - Hasar: {damage}
    - Yürüyüş Mesafesi: {walk_distance}
    - Silah Sayısı: {weapons}

    Oyuncunun gelişmesi için stratejik öneriler ver. 
    - Savaş teknikleri, 
    - Loot planı, 
    - Takım oyunuyla ilgili önerilerde bulun.
    """
)

# 🎮 **Koç Fonksiyonu**
def get_coach_advice(kills, damage, walk_distance, weapons):
    prompt = coach_prompt.format(kills=kills, damage=damage, walk_distance=walk_distance, weapons=weapons)
    result = llm.invoke(prompt)
    return result
