import os
import openai
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from pathlib import Path

###############################################
# 1. .env dosyasını yüklerken  When loading the .env file
###############################################
# crew_agent.py'in bulunduğu konumun bir üst klasöründe .env olduğunu varsayıyoruz. We assume that .env is in the parent folder of the location where crew_agent.py is located.
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

# Şimdi API KEY'i okuması gereken kısım 
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()

print("🔎 DEBUG: Yüklenen API KEY =", OPENAI_API_KEY)  # GÖZLE GÖR, ANAHTAR GİZLEMEK İSTERSEN SİL

# Eğer API anahtarı yok veya yanlışsa 
if not OPENAI_API_KEY.startswith("sk-"):
    raise ValueError("❌ Geçerli bir OpenAI API anahtarı bulunamadı veya yanlış! .env dosyasını kontrol edin.")

openai.api_key = OPENAI_API_KEY

###############################################
# 2. KAZANMA OLASILIGI HESABI WINNING PROBABILITY CALCULATION
###############################################
def calculate_win_probability(kills, damage, walk_distance, weapons):
    kill_factor = min(40, kills * 4)           
    damage_factor = min(25, damage / 40)       
    move_factor = min(20, walk_distance / 150) 
    weapon_factor = min(15, weapons * 3)       
    total_score = kill_factor + damage_factor + move_factor + weapon_factor
    return round(max(0, min(100, total_score)), 1)

###############################################
# 3. GPT'DEN KOÇ ÖNERİSİ ALMA  = GETTING A COACH RECOMMENDATION FROM GPT
###############################################
def get_coach_advice(kills, damage, walk_distance, weapons):
    """
    OpenAI GPT tabanlı PUBG koç önerisi.
    Manuel fallback yok. API key hatalıysa hata verir.
    """
    # Kazanma olasılığı probability of winning
    win_prob = calculate_win_probability(kills, damage, walk_distance, weapons)

    # GPT modeli kur Install GPT model
    llm = ChatOpenAI(
        temperature=0.8,
       model_name="gpt-4o",  # GPT-4 erişimin varsa "gpt-4" de yazabilirsin
        openai_api_key=OPENAI_API_KEY
    )

    # Prompt sablonu Prompt template
    prompt_template = PromptTemplate(
        input_variables=["kills", "damage", "walk_distance", "weapons", "win_prob"],
        template="""
        Sen profesyonel bir PUBG koçusun. Oyuncunun istatistikleri:
        - Kills: {kills}
        - Damage: {damage}
        - Walk Distance: {walk_distance}
        - Weapons: {weapons}
        - Win Probability (basit hesap): %{win_prob}

        Lütfen oyuncuya şu konularda somut ve gerçekçi tavsiyeler ver:
        1) Oyun Tarzı Analizi (agresif, pasif, lootçu vs.)
        2) Çatışma/Savaş Stratejileri
        3) Loot, Silah ve Eklenti Önerileri
        4) Pozisyon ve Rotasyon Taktikleri
        5) Gelişim Planı ve Zayıf Noktalar

        Önerilerin çok teknik veya çok yüzeysel olmasın; orta seviye detaylı, uygulanabilir olsun.
        """
    )

    prompt_text = prompt_template.format(
        kills=kills,
        damage=damage,
        walk_distance=walk_distance,
        weapons=weapons,
        win_prob=win_prob
    )

    # GPT'ye isteği gönder Send request to GPT 
    try:
        result = llm.invoke(prompt_text)
        return result.content  # GPT cevabı
    except Exception as e:
        # Burada manuel fallback YOK
        raise RuntimeError(f"OpenAI GPT hatası: {e}")
