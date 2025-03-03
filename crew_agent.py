import os
import openai
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

# 📌 .env dosyasını yükle
load_dotenv()

# 📌 API anahtarını al ve OpenAI istemcisine ekle
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
openai.api_key = OPENAI_API_KEY

# 🚨 Eğer API anahtarı yoksa, hata vermeden varsayılan önerileri kullan!
if not OPENAI_API_KEY or not OPENAI_API_KEY.startswith("sk-"):
    print("⚠️ Uyarı: OpenAI API anahtarı eksik veya hatalı. Öneriler manuel olarak üretilecek.")

# 🧠 OpenAI Chat Modeli Tanımla
try:
    llm = ChatOpenAI(temperature=0.7, model_name="gpt-3.5-turbo", openai_api_key=OPENAI_API_KEY)
except Exception as e:
    print(f"❌ OpenAI API Bağlantı Hatası: {e}")
    llm = None  # Eğer hata alırsak OpenAI olmadan öneriler vereceğiz.

# 🔹 AI Koç Promtu
coach_prompt = PromptTemplate(
    input_variables=["kills", "damage", "walk_distance", "weapons"],
    template="""
    Sen bir PUBG koçusun. Oyuncunun istatistikleri:
    - Öldürme Sayısı: {kills}
    - Hasar: {damage}
    - Yürüyüş Mesafesi: {walk_distance}
    - Silah Sayısı: {weapons}

    Oyuncunun oyun stiline özel olarak en az 3 detaylı öneri ver:
    - Savaş teknikleri
    - Loot stratejileri
    - Hayatta kalma taktikleri
    """
)

# 🎮 Koç Fonksiyonu
def get_coach_advice(kills, damage, walk_distance, weapons):
    """OpenAI API çalışıyorsa AI'dan, çalışmıyorsa manuel öneriler sunar."""
    if llm:
        try:
            prompt = coach_prompt.format(kills=kills, damage=damage, walk_distance=walk_distance, weapons=weapons)
            result = llm.invoke(prompt)
            return result.content
        except Exception as e:
            print(f"❌ OpenAI API Hatası: {e}")
    
    # Eğer OpenAI API çalışmazsa manuel öneriler döndür!
    return generate_manual_advice(kills, damage, walk_distance, weapons)

# 🎯 **Eğer OpenAI API çalışmazsa, önerileri kendimiz üretelim**
def generate_manual_advice(kills, damage, walk_distance, weapons):
    """Eğer OpenAI API çalışmazsa, sabit öneriler döndür."""
    feedback = "**📌 PUBG AI Koç Önerileri:**\n"

    if kills >= 10:
        feedback += "🔥 Harika! Öldürme sayın çok yüksek, agresif oyun tarzına sahipsin.\n"
    elif kills >= 5:
        feedback += "🎯 Savaş yeteneğin iyi, ancak biraz daha agresif oynayabilirsin.\n"
    else:
        feedback += "⚠️ Öldürme sayın düşük, savaşlara girmeyi daha fazla denemelisin.\n"

    if damage >= 3000:
        feedback += "💥 Mükemmel nişancısın! Hasar miktarın çok yüksek.\n"
    elif damage >= 1000:
        feedback += "🔫 Hasar fena değil ama daha isabetli atışlar yapmalısın.\n"
    else:
        feedback += "⚠️ Hasar miktarın düşük, rakiplerle daha çok savaşmalısın.\n"

    if walk_distance >= 5000:
        feedback += "🚶 Haritada çok dolaşıyorsun, hayatta kalma şansın yüksek.\n"
    elif walk_distance <= 1000:
        feedback += "⚠️ Hareketsizsin, keşif yapmalısın.\n"

    if weapons >= 5:
        feedback += "🔫 Loot yapman çok iyi! Silahların yeterli görünüyor.\n"
    else:
        feedback += "⚠️ Daha fazla silah toplamalısın.\n"

    return feedback

