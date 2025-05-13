import os
import streamlit as st
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv

from crewai import Agent, Task, Crew
try:
    from crewai.process import Process
except ImportError:
    from crewai import Process

from langchain_openai import ChatOpenAI

# API anahtarını doğrudan ayarla
os.environ["OPENAI_API_KEY"] = "your_key"

# Veri yükleme fonksiyonu
def load_pubg_data(file_path='pubg_final.csv'):
    """
    PUBG veri setini yükler
    """
    try:
        df = pd.read_csv(file_path)
        return df
    except FileNotFoundError:
        # Alternatif konumları dene
        alt_paths = ['./data/pubg_final.csv', '../pubg_final.csv']
        for path in alt_paths:
            try:
                df = pd.read_csv(path)
                return df
            except FileNotFoundError:
                continue
        print(f"Veri dosyası bulunamadı: {file_path}")
        return None
    except Exception as e:
        print(f"Veri yükleme hatası: {e}")
        return None

# Oyuncu verilerini getirme fonksiyonu
def get_player_data(df, player_id=None, id_column=None):
    """
    Belirli bir oyuncunun verilerini getirir
    """
    if player_id and id_column and player_id in df[id_column].values:
        return df[df[id_column] == player_id]
    return df.head(10)  # Eğer belirli bir oyuncu bulunamazsa ilk 10 satırı döndür

# Oyuncu istatistiklerini hesaplama fonksiyonu
def calculate_player_stats(player_data):
    """
    Oyuncunun detaylı istatistiklerini hesaplar
    """
    # Temel istatistikler
    total_matches = len(player_data)
    if total_matches == 0:
        return {
            'total_matches': 0,
            'wins': 0,
            'win_rate': 0,
            'kills': 0,
            'deaths': 0,
            'kd_ratio': 0,
            'avg_damage': 0,
            'avg_walk_distance': 0,
            'avg_ride_distance': 0,
            'avg_swim_distance': 0,
            'headshot_kills': 0,
            'longest_kill': 0,
            'weapons_acquired': 0
        }

    # Kazanma oranı - winPlacePerc sütunu varsa kullan
    if 'winPlacePerc' in player_data.columns:
        avg_win_place = player_data['winPlacePerc'].mean() * 100
    else:
        avg_win_place = 0

    # Kills
    if 'kills' in player_data.columns:
        kills = player_data['kills'].sum()
    else:
        kills = 0

    # Damage
    if 'damageDealt' in player_data.columns:
        avg_damage = player_data['damageDealt'].mean()
    else:
        avg_damage = 0

    # Hareket istatistikleri
    avg_walk_distance = player_data['walkDistance'].mean() if 'walkDistance' in player_data.columns else 0
    avg_ride_distance = player_data['rideDistance'].mean() if 'rideDistance' in player_data.columns else 0
    avg_swim_distance = player_data['swimDistance'].mean() if 'swimDistance' in player_data.columns else 0

    # Silah istatistikleri
    headshot_kills = player_data['headshotKills'].sum() if 'headshotKills' in player_data.columns else 0
    longest_kill = player_data['longestKill'].max() if 'longestKill' in player_data.columns else 0
    weapons_acquired = player_data['weaponsAcquired'].mean() if 'weaponsAcquired' in player_data.columns else 0

    # K/D oranı
    deaths = total_matches - (avg_win_place / 100 * total_matches)  # Basitleştirilmiş hesaplama
    kd_ratio = kills / deaths if deaths > 0 else kills

    return {
        'total_matches': total_matches,
        'win_rate': avg_win_place,
        'kills': kills,
        'kills_per_match': kills / total_matches if total_matches > 0 else 0,
        'deaths': deaths,
        'kd_ratio': kd_ratio,
        'avg_damage': avg_damage,
        'avg_walk_distance': avg_walk_distance,
        'avg_ride_distance': avg_ride_distance,
        'avg_swim_distance': avg_swim_distance,
        'headshot_kills': headshot_kills,
        'headshot_ratio': headshot_kills / kills if kills > 0 else 0,
        'longest_kill': longest_kill,
        'weapons_acquired': weapons_acquired
    }

# Oyun tarzını belirleme fonksiyonu
def determine_playstyle(player_stats):
    """
    Oyuncunun istatistiklerine göre oyun tarzını belirler
    """
    # Agresiflik puanı hesapla
    aggression_score = 0

    # Kills ve damage yüksekse agresiflik artar
    if player_stats['kills_per_match'] > 3:
        aggression_score += 2
    elif player_stats['kills_per_match'] > 1:
        aggression_score += 1

    if player_stats['avg_damage'] > 300:
        aggression_score += 2
    elif player_stats['avg_damage'] > 150:
        aggression_score += 1

    # Headshot oranı yüksekse agresiflik ve beceri artar
    headshot_ratio = player_stats.get('headshot_ratio', 0)
    if isinstance(headshot_ratio, (int, float)) and headshot_ratio > 0.3:
        aggression_score += 1

    # Hareket mesafesi fazlaysa aktif oyuncu
    if player_stats['avg_walk_distance'] > 2500:
        aggression_score += 1

    # Playstyle belirleme
    if aggression_score >= 4:
        return "Çok Agresif"
    elif aggression_score >= 2:
        return "Agresif"
    elif aggression_score >= 1:
        return "Dengeli"
    else:
        return "Pasif"

# Silah önerileri oluşturma fonksiyonu
def generate_weapon_suggestions(player_stats, playstyle):
    """
    Oyuncunun istatistiklerine ve oyun tarzına göre silah önerileri oluşturur
    """
    suggestions = {}

    # Headshot oranına göre keskin nişancı silahları öner
    headshot_ratio = player_stats.get('headshot_ratio', 0)
    if isinstance(headshot_ratio, (int, float)) and headshot_ratio > 0.3:
        suggestions['sniper'] = [
            "Kar98k - Yüksek headshot oranınız bu silahla çok etkili olacaktır",
            "M24 - Keskin nişancılık yeteneklerinizi en üst düzeye çıkarabilirsiniz",
            "AWM - Kutu silahı olarak bulursanız mutlaka alın"
        ]
    else:
        suggestions['sniper'] = [
            "SKS - Yarı otomatik keskin nişancı tüfeği, daha az hassas nişan gerektirir",
            "Mini14 - Hızlı atış yapabilir, headshot oranınızı artırmak için iyi bir seçenek"
        ]

    # Oyun tarzına göre assault rifle önerileri
    if playstyle in ["Çok Agresif", "Agresif"]:
        suggestions['assault'] = [
            "M416 - Yüksek hasar ve kontrol için ideal",
            "Beryl M762 - Yüksek hasar potansiyeli, kontrol edebilirseniz çok güçlü",
            "AKM - Yüksek hasar, agresif oyun tarzı için uygun"
        ]
    else:
        suggestions['assault'] = [
            "SCAR-L - Daha kolay kontrol edilebilir, hasar potansiyelinizi artırabilir",
            "G36C - Düşük geri tepmeli, orta mesafe çatışmalar için ideal",
            "QBZ - Dengeli performans, pasif oyun tarzı için uygun"
        ]

    # Oyun tarzına göre yakın mesafe silahları
    if playstyle in ["Çok Agresif"]:
        suggestions['close_range'] = [
            "Vector - Hızlı TTK, agresif oyun tarzı için ideal",
            "Tommy Gun - Yüksek şarjör kapasitesi, bina baskınları için iyi"
        ]
    elif playstyle in ["Agresif"]:
        suggestions['close_range'] = [
            "UMP45 - Hareket halindeyken bile etkili",
            "Uzi - Yakın mesafede çok hızlı, agresif oyuncular için"
        ]
    else:
        suggestions['close_range'] = [
            "S12K - Bina içi çatışmalar için güçlü",
            "S686 - Yüksek hasar, savunma pozisyonları için iyi"
        ]

    return suggestions

# İniş bölgesi önerileri oluşturma fonksiyonu
def generate_landing_suggestions(playstyle):
    """
    Oyuncunun oyun tarzına göre iniş bölgesi önerileri oluşturur
    """
    suggestions = {}

    # Oyun tarzına göre iniş bölgeleri öner
    if playstyle in ["Çok Agresif"]:
        suggestions['hot_drop'] = [
            "Pochinki - Yüksek oyuncu yoğunluğu, erken çatışmalar için ideal",
            "School/Apartments - Hızlı loot ve çatışma imkanı",
            "Bootcamp (Sanhok) - Yüksek riskli ama yüksek ödüllü bölge",
            "Hacienda (Miramar) - Yüksek kaliteli loot ve erken çatışma"
        ]
    elif playstyle in ["Agresif"]:
        suggestions['medium_drop'] = [
            "Rozhok - Orta seviye çatışma, iyi loot",
            "Yasnaya Polyana - Geniş alan, çok sayıda bina ve orta seviye çatışma",
            "Paradise Resort (Sanhok) - Orta-yüksek risk, iyi loot",
            "Los Leones (Miramar) - Büyük şehir, çeşitli çatışma fırsatları"
        ]
    else:
        suggestions['safe_drop'] = [
            "Gatka - Orta seviye loot, daha az oyuncu",
            "Zharki - Uzak lokasyon, güvenli başlangıç",
            "Kampong (Sanhok) - Dengeli loot ve daha az çatışma",
            "Monte Nuevo (Miramar) - Sakin bölge, güvenli başlangıç"
        ]

    # Taktik önerileri
    if playstyle in ["Çok Agresif", "Agresif"]:
        suggestions['tactics'] = [
            "Erken çatışmalara gir ve bölgeyi temizle",
            "Silah sesleri duyduğunda o yöne doğru ilerle",
            "Airdrop'ları kovala",
            "Araçları agresif kullan ve baskın yap"
        ]
    else:
        suggestions['tactics'] = [
            "Güvenli bölgelerde loot topla",
            "Çemberin kenarında hareket et",
            "İyi pozisyon al ve savunmada kal",
            "Çatışmalardan kaçın ve son çemberlere kadar hayatta kal"
        ]

    return suggestions

# LLM oluşturma fonksiyonu
def get_llm():
    """
    OpenAI LLM'i oluşturur
    """
    return ChatOpenAI(
        model="gpt-4o",
        temperature=0.7
    )

# Ajanları oluşturma fonksiyonu
def create_agents():
    """
    Ajanları oluşturur
    """
    llm = get_llm()

    # Analist ajanı
    analyst_agent = Agent(
        name="PUBG Veri Analisti",
        role="Veri Analisti",
        goal="PUBG oyun verilerini analiz etmek ve oyuncunun kazanma oranını hesaplamak",
        backstory="PUBG oyun verilerinde uzmanlaşmış, oyun mekaniklerini ve istatistiklerini derinlemesine anlayan bir veri bilimci.",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

    # Koç ajanı
    coach_agent = Agent(
        name="PUBG Oyun Koçu",
        role="Strateji Koçu",
        goal="Oyuncunun verilerine dayanarak kişiselleştirilmiş stratejiler ve taktikler önermek",
        backstory="Profesyonel PUBG oyuncusu ve koçu, binlerce saatlik oyun deneyimine sahip ve oyuncuların performansını artırmada uzman.",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

    return {
        'analyst': analyst_agent,
        'coach': coach_agent
    }

# Görevleri oluşturma fonksiyonu
def create_tasks(agents, player_stats, playstyle):
    """
    Görevleri oluşturur
    """
    # Oyuncu istatistiklerini basit bir string olarak formatla
    stats_summary = f"Toplam maç: {player_stats['total_matches']}, Kazanma oranı: {player_stats['win_rate']:.2f}%, K/D: {player_stats['kd_ratio']:.2f}, Öldürme: {player_stats['kills']}, Hasar: {player_stats['avg_damage']:.2f}"

    # Analiz görevi
    analyze_task = Task(
        description=f"Oyuncunun PUBG verilerini analiz et. {stats_summary}. Oyun tarzı: {playstyle}",
        expected_output="Oyuncunun kazanma oranı, K/D oranı ve diğer önemli istatistikler hakkında detaylı analiz",
        agent=agents['analyst']
    )

    # Koçluk önerileri görevi
    coaching_task = Task(
        description=f"Oyuncunun istatistiklerine göre oyun stratejileri öner. {stats_summary}. Oyun tarzı: {playstyle}",
        expected_output="Kişiselleştirilmiş oyun stratejileri, silah önerileri ve iniş bölgesi tavsiyeleri",
        agent=agents['coach'],
        dependencies=[analyze_task]
    )

    return [analyze_task, coaching_task]

# Sonuçları gösterme fonksiyonu - CrewOutput için düzeltildi
def display_results(player_stats, playstyle, weapon_suggestions, landing_suggestions, results):
    """
    Analiz sonuçlarını gösterir
    """
    # Sonuçları göster
    col1, col2 = st.columns(2)

    with col1:
        st.header("🎯 Kazanma Olasılığı")
        st.metric("Kazanma Oranı", f"{player_stats['win_rate']:.2f}%")

        st.header("📊 Oyuncu İstatistikleri")

        # İstatistikleri göster
        metrics_col1, metrics_col2 = st.columns(2)

        with metrics_col1:
            st.metric("K/D Oranı", f"{player_stats['kd_ratio']:.2f}")
            st.metric("Toplam Öldürme", f"{player_stats['kills']}")
            st.metric("Maç Başı Öldürme", f"{player_stats['kills_per_match']:.2f}")

        with metrics_col2:
            st.metric("Ortalama Hasar", f"{player_stats['avg_damage']:.2f}")
            headshot_ratio = player_stats.get('headshot_ratio', 0)
            if isinstance(headshot_ratio, (int, float)):
                st.metric("Headshot Oranı", f"{headshot_ratio*100:.2f}%")
            else:
                st.metric("Headshot Oranı", "0.00%")
            st.metric("En Uzun Kill", f"{player_stats['longest_kill']:.2f}m")

        # Grafik ekle
        st.subheader("Hareket Analizi")
        fig = px.bar(
            x=["Yürüme", "Araç", "Yüzme"],
            y=[player_stats['avg_walk_distance'], player_stats['avg_ride_distance'], player_stats['avg_swim_distance']],
            title="Ortalama Hareket Mesafeleri",
            labels={"x": "Hareket Tipi", "y": "Mesafe (m)"}
        )
        st.plotly_chart(fig)

    with col2:
        st.header("🤖 Gelişmiş Koç Önerileri")

        st.subheader("Oyun Tarzı Analizi")
        st.write(f"Oyuncunun istatistikleri, **{playstyle}** bir oyun tarzına sahip olduğunu gösteriyor. {player_stats['kills_per_match']:.1f} maç başı kill ve {player_stats['avg_damage']:.0f} hasar ile bu açıkça belli oluyor.")

        if playstyle in ["Çok Agresif", "Agresif"]:
            st.write("Agresif oyun tarzı, oyuncunun çatışmalarda kendine güvendiğini ve rakipleri hızlıca alt edebilme yeteneğine sahip olduğunu gösteriyor. Ancak, bu tarz bazen riskli olabilir; bu yüzden dikkatli planlanmalı.")
        else:
            st.write("Dengeli/Pasif oyun tarzı, stratejik düşünme ve pozisyon alma konusunda iyi olduğunuzu gösteriyor. Bu tarz, uzun vadede hayatta kalma şansınızı artırır ancak kill sayınızı sınırlayabilir.")

        # Sekmeleri oluştur
        tabs = st.tabs(["Çatışma Stratejileri", "Silah Önerileri", "İniş Bölgeleri"])

        with tabs[0]:
            st.subheader("Çatışma/Savaş Stratejileri")
            st.write("1. **Öncelikli Hedef Belirleme:** Çatışma sırasında hızlı karar vererek, en büyük tehdit oluşturan rakipleri öncelikle etkisiz hale getirmeye odaklan.")
            st.write("2. **Konum Avantajı:** Yüksek yerlere çıkmak veya doğal örtülerden yararlanarak görüş açısını artır. Böylece rakiplerin konumlarını daha kolay tespit edebilirsin.")
            st.write("3. **Sürpriz Saldırılar:** Rakiplerin pozisyonlarını tahmin ederek onları hazırlıksız yakalayabilirsin. Ancak, bu tür hamleleri yaparken dikkatli ol, çünkü tuzağa düşme riski de vardır.")

            # AI koç önerilerini ekle
            st.write("### AI Koç Analizi")

            # CrewOutput nesnesini kontrol et
            if results:
                # CrewOutput'un farklı yapılarını kontrol et
                if hasattr(results, 'raw_output'):
                    # raw_output varsa
                    if isinstance(results.raw_output, list) and results.raw_output:
                        st.write(results.raw_output[0])
                    else:
                        st.write(str(results.raw_output))
                elif hasattr(results, 'tasks') and results.tasks:
                    # tasks varsa
                    st.write(results.tasks[0].output if results.tasks[0].output else "Analiz sonucu bulunamadı.")
                elif hasattr(results, 'result'):
                    # result varsa
                    st.write(results.result)
                else:
                    # Diğer durumlar için
                    st.write(str(results))

        with tabs[1]:
            st.subheader("Loot, Silah ve Eklenti Önerileri")

            st.write("1. **Silahlar:**")
            if 'sniper' in weapon_suggestions:
                st.write("   **Keskin Nişancı Silahları:**")
                for sugg in weapon_suggestions['sniper']:
                    st.write(f"   - {sugg}")

            if 'assault' in weapon_suggestions:
                st.write("   **Assault Rifles:**")
                for sugg in weapon_suggestions['assault']:
                    st.write(f"   - {sugg}")

            if 'close_range' in weapon_suggestions:
                st.write("   **Yakın Mesafe Silahları:**")
                for sugg in weapon_suggestions['close_range']:
                    st.write(f"   - {sugg}")

            st.write("2. **Eklentiler:** Dikey tutuş (foregrip) ve kompansatör kullanarak geri tepkiyi azaltabilirsin. Ayrıca, kırmızı nokta veya holosight gibi hızlı nişan alma imkanı veren nişangahlar tercih edilebilir.")

            st.write("3. **Zırh ve Sağlık:** Çatışmalar esnasında daha uzun süre hayatta kalmak için seviye 3 kask ve yelek bulmaya öncelik ver. Ayrıca, yeterli miktarda sağlık kiti ve boost almayı unutma.")

            # AI koç önerilerini ekle
            st.write("### AI Koç Silah Önerileri")

            # CrewOutput nesnesini kontrol et
            if results:
                # CrewOutput'un farklı yapılarını kontrol et
                if hasattr(results, 'raw_output'):
                    # raw_output varsa ve liste ise
                    if isinstance(results.raw_output, list) and len(results.raw_output) > 1:
                        st.write(results.raw_output[1])
                    elif isinstance(results.raw_output, str):
                        st.write(results.raw_output)
                elif hasattr(results, 'tasks') and len(results.tasks) > 1:
                    # tasks varsa
                    st.write(results.tasks[1].output if results.tasks[1].output else "Koçluk önerileri bulunamadı.")
                elif hasattr(results, 'result'):
                    # result varsa
                    st.write(results.result)
                else:
                    # Diğer durumlar için
                    st.write("Koçluk önerileri oluşturulamadı.")

        with tabs[2]:
            st.subheader("İniş Bölgesi Önerileri")

            if 'hot_drop' in landing_suggestions:
                st.write("**Sıcak Bölgeler (Yüksek Risk, Yüksek Ödül):**")
                for sugg in landing_suggestions['hot_drop']:
                    st.write(f"- {sugg}")

            if 'medium_drop' in landing_suggestions:
                st.write("**Orta Yoğunluklu Bölgeler:**")
                for sugg in landing_suggestions['medium_drop']:
                    st.write(f"- {sugg}")

            if 'safe_drop' in landing_suggestions:
                st.write("**Güvenli Bölgeler:**")
                for sugg in landing_suggestions['safe_drop']:
                    st.write(f"- {sugg}")

            st.write("**Taktik Önerileri:**")
            for tactic in landing_suggestions['tactics']:
                st.write(f"- {tactic}")

# Ana fonksiyon
def main():
    """
    Streamlit uygulamasını çalıştırır
    """
    st.set_page_config(
        page_title="PUBG AI Koçu",
        page_icon="🎮",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.title("🏆 PUBG AI Koçu - Gelişmiş ve Gerçekçi Öneriler")
    st.subheader("Bu uygulama, PUBG performansına dayalı kazanma olasılığı ve OpenAI GPT tabanlı gelişmiş koç önerileri sunar.")

    # Veri setini yükle
    df = load_pubg_data()
    if df is None:
        st.error("Veri seti yüklenemedi. Lütfen 'pubg_final.csv' dosyasının doğru konumda olduğunu kontrol edin.")
        return

    # Sidebar - Oyuncu seçimi veya manuel giriş
    st.sidebar.header("Oyuncu Verileri")

    input_method = st.sidebar.radio(
        "Veri Giriş Yöntemi",
        ["Veri Setinden Seç", "Manuel Giriş"]
    )

    player_stats = {}
    playstyle = ""

    if input_method == "Veri Setinden Seç":
        # Veri setindeki sütunları göster
        if st.sidebar.checkbox("Veri Seti Detaylarını Göster"):
            st.sidebar.write("Veri seti örneği:")
            st.sidebar.dataframe(df.head(3))
            st.sidebar.write("Veri seti sütunları:")
            st.sidebar.write(df.columns.tolist())

        # Oyuncu ID sütunu olarak kullanılabilecek bir sütun seç
        player_id_column = None
        possible_id_columns = ['Id', 'player_id', 'id', 'player_name', 'name', 'player']

        for col in possible_id_columns:
            if col in df.columns:
                player_id_column = col
                break

        if player_id_column is None:
            # Eğer uygun bir sütun bulunamazsa, indeksi kullan
            df['player_index'] = range(len(df))
            player_id_column = 'player_index'
            st.sidebar.warning("Veri setinde oyuncu ID sütunu bulunamadı. İndeks numaralarını kullanıyoruz.")

        # Benzersiz oyuncu ID'lerini al
        player_ids = df[player_id_column].unique().tolist()

        # Eğer çok fazla benzersiz ID varsa, sadece ilk 100'ünü göster
        if len(player_ids) > 100:
            player_ids = player_ids[:100]
            st.sidebar.warning(f"Çok fazla benzersiz ID var. Sadece ilk 100 ID gösteriliyor.")

        selected_player = st.sidebar.selectbox(
            f"Oyuncu seçin ({player_id_column})",
            options=player_ids,
            index=0
        )

        # Analiz butonunu ekle
        if st.sidebar.button("Analiz Et ve Koç Önerilerini Al"):
            with st.spinner("AI Koçunuz analiz yapıyor..."):
                # Seçilen oyuncunun verilerini al
                player_data = get_player_data(df, selected_player, player_id_column)

                # Oyuncu istatistiklerini hesapla
                player_stats = calculate_player_stats(player_data)

                # Oyun tarzını belirle
                playstyle = determine_playstyle(player_stats)

                # Silah ve iniş önerilerini oluştur
                weapon_suggestions = generate_weapon_suggestions(player_stats, playstyle)
                landing_suggestions = generate_landing_suggestions(playstyle)

                try:
                    # Ajanları oluştur
                    agents = create_agents()

                    # Görevleri oluştur
                    tasks = create_tasks(agents, player_stats, playstyle)

                    # Crew'u oluştur ve çalıştır
                    crew = Crew(
                        agents=list(agents.values()),
                        tasks=tasks,
                        verbose=True,
                        process=Process.sequential
                    )

                    # Sonuçları al
                    results = crew.kickoff()
                except Exception as e:
                    st.error(f"CrewAI çalıştırılırken bir hata oluştu: {e}")
                    # Hata durumunda varsayılan sonuçlar
                    results = f"Oyuncu Analizi: {playstyle} oyun tarzına sahip bir oyuncu. K/D oranı {player_stats['kd_ratio']:.2f} ve kazanma oranı {player_stats['win_rate']:.2f}%. Koçluk Önerileri: {playstyle} oyun tarzınıza göre silah seçimlerinizi ve iniş bölgelerinizi optimize edin."

                # Sonuçları göster
                display_results(player_stats, playstyle, weapon_suggestions, landing_suggestions, results)

    else:  # Manuel Giriş
        st.sidebar.subheader("Oyun İstatistiklerinizi Girin")

        kills = st.sidebar.slider("Öldürme (Kills)", 0, 100, 40)
        damage = st.sidebar.slider("Hasar (Damage Dealt)", 0, 10000, 5000)
        walk_distance = st.sidebar.slider("Yürüme Mesafesi (metre)", 0, 10000, 3000)
        weapons_acquired = st.sidebar.slider("Silah Sayısı", 0, 20, 7)

        # Manuel girilen verilere göre istatistikleri oluştur
        player_stats = {
            'total_matches': 10,  # Varsayılan değer
            'win_rate': 50,  # Varsayılan değer
            'kills': kills,
            'kills_per_match': kills / 10,  # 10 maç varsayılan
            'deaths': 5,  # Varsayılan değer
            'kd_ratio': kills / 5,  # Varsayılan değer
            'avg_damage': damage,
            'avg_walk_distance': walk_distance,
            'avg_ride_distance': 1000,  # Varsayılan değer
            'avg_swim_distance': 100,  # Varsayılan değer
            'headshot_kills': kills * 0.2,  # Varsayılan değer
            'headshot_ratio': 0.2,  # Varsayılan değer
            'longest_kill': 200,  # Varsayılan değer
            'weapons_acquired': weapons_acquired
        }

        # Oyun tarzını belirle
        playstyle = determine_playstyle(player_stats)

        if st.sidebar.button("Analiz Et ve Koç Önerilerini Al"):
            with st.spinner("AI Koçunuz analiz yapıyor..."):
                # Silah ve iniş önerilerini oluştur
                weapon_suggestions = generate_weapon_suggestions(player_stats, playstyle)
                landing_suggestions = generate_landing_suggestions(playstyle)

                try:
                    # Ajanları oluştur
                    agents = create_agents()

                    # Görevleri oluştur
                    tasks = create_tasks(agents, player_stats, playstyle)

                    # Crew'u oluştur ve çalıştır
                    crew = Crew(
                        agents=list(agents.values()),
                        tasks=tasks,
                        verbose=True,
                        process=Process.sequential
                    )

                    # Sonuçları al
                    results = crew.kickoff()
                except Exception as e:
                    st.error(f"CrewAI çalıştırılırken bir hata oluştu: {e}")
                    # Hata durumunda varsayılan sonuçlar
                    results = f"Oyuncu Analizi: {playstyle} oyun tarzına sahip bir oyuncu. K/D oranı {player_stats['kd_ratio']:.2f} ve kazanma oranı {player_stats['win_rate']:.2f}%. Koçluk Önerileri: {playstyle} oyun tarzınıza göre silah seçimlerinizi ve iniş bölgelerinizi optimize edin."

                # Sonuçları göster
                display_results(player_stats, playstyle, weapon_suggestions, landing_suggestions, results)

if __name__ == "__main__":
    main()