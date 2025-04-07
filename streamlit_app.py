import streamlit as st
from crew_agent import get_coach_advice, calculate_win_probability

def main():
    st.set_page_config(page_title="PUBG AI Koçu", layout="centered")
    st.title("🏆 PUBG AI Koçu - Gelişmiş ve Gerçekçi Öneriler")

    st.write("""
    Bu uygulama, PUBG performansına dayalı **kazanma olasılığı** ve
    **OpenAI GPT** tabanlı gelişmiş koç önerileri sunar.
    """)

    # Kullanıcıdan veri al
    kills = st.number_input("Öldürme (Kills)", min_value=0, max_value=50, value=3, step=1)
    damage = st.number_input("Hasar (Damage Dealt)", min_value=0, max_value=9999, value=500, step=100)
    walk_distance = st.number_input("Yürüme Mesafesi (metre)", min_value=0, max_value=50000, value=2000, step=500)
    weapons = st.number_input("Silah Sayısı", min_value=0, max_value=20, value=4, step=1)

    if st.button("Analiz Et ve Koç Önerilerini Al"):
        # 1) Kazanma yüzdesi
        prob = calculate_win_probability(kills, damage, walk_distance, weapons)
        st.subheader("🎯 Kazanma Olasılığı")
        st.write(f"**%{prob}**")

        # 2) GPT Koç Önerileri
        try:
            with st.spinner("AI Koçu düşünüyor..."):
                advice = get_coach_advice(kills, damage, walk_distance, weapons)
            st.subheader("🤖 Gelişmiş Koç Önerileri")
            st.write(advice)
        except Exception as e:
            st.error(f"Koç önerisi alınırken hata oluştu: {e}")

if __name__ == "__main__":
    main()
