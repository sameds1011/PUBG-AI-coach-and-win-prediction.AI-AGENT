import streamlit as st
import numpy as np
import joblib
import os
from crew_agent import get_coach_advice

# 📌 Modeli yükleme
model_path = os.path.join(os.path.dirname(__file__), "../pubg_model.pkl")

if not os.path.exists(model_path):
    st.error("❌ Model dosyası bulunamadı! Önce modeli eğitip kaydedin.")
    st.stop()

model = joblib.load(model_path)

# 🎮 Streamlit Arayüzü Başlık
st.title("🏆 PUBG AI Koçu ve Kazanma Tahmini")
st.write("📊 Aşağıdaki verileri girerek kazanma ihtimalinizi öğrenin!")

# 📊 Kullanıcıdan Giriş Değerleri Alma
kills = st.number_input("Öldürme Sayısı", 0, 20, 3)
damage = st.number_input("Hasar (Damage Dealt)", 0, 5000, 500)
walk_distance = st.number_input("Yürüyüş Mesafesi", 0, 10000, 2000)
weapons = st.number_input("Silah Sayısı", 0, 10, 4)

# 🎯 Tahmin Butonu
if st.button("Tahmin Et ve AI Koç Önerisi Al"):
    input_features = np.array([[kills, damage, walk_distance, weapons]])
    
    # 🔮 Tahmini Hesapla
    prediction = model.predict(input_features)[0]
    
    # 🏆 Kazanma olasılığını hesapla
    probability = model.predict_proba(input_features)[0][1]  # Kazanma olasılığı
    win_probability = round(probability * 100, 2)

    # 🏆 Sonucu Göster
    st.subheader(f"🔮 Tahmin: {'Kazanan' if prediction == 1 else 'Kaybeden'}")
    st.write(f"📊 **Kazanma Olasılığı: %{win_probability}**")

    # 💡 AI Koçtan Geri Bildirim
    feedback = get_coach_advice(kills, damage, walk_distance, weapons)
    st.write("🤖 **AI Koç Önerileri:**")
    st.write(feedback)
