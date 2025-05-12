def generate_weapon_suggestions(player_stats):
    """
    Oyuncunun istatistiklerine göre silah önerileri oluşturur
    """
    suggestions = {}

    # Headshot oranına göre keskin nişancı silahları öner
    if player_stats.get('headshot_kills', 0) > 0 and player_stats.get('kills', 0) > 0:
        headshot_ratio = player_stats['headshot_kills'] / player_stats['kills']
        if headshot_ratio > 0.3:
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

    # Hasar oranına göre assault rifle önerileri
    if player_stats.get('avg_damage', 0) > 200:
        suggestions['assault'] = [
            "M416 - Yüksek hasar ve kontrol için ideal",
            "Beryl M762 - Yüksek hasar potansiyeli, kontrol edebilirseniz çok güçlü"
        ]
    else:
        suggestions['assault'] = [
            "SCAR-L - Daha kolay kontrol edilebilir, hasar potansiyelinizi artırabilir",
            "G36C - Düşük geri tepmeli, orta mesafe çatışmalar için ideal"
        ]

    # Hareket tarzına göre yakın mesafe silahları
    if player_stats.get('avg_walk_distance', 0) > 2000:
        suggestions['close_range'] = [
            "UMP45 - Hareket halindeyken bile etkili",
            "Vector - Hızlı TTK, agresif oyun tarzı için ideal"
        ]
    else:
        suggestions['close_range'] = [
            "S12K - Bina içi çatışmalar için güçlü",
            "Tommy Gun - Yüksek şarjör kapasitesi, savunma pozisyonları için iyi"
        ]

    return suggestions

def generate_landing_suggestions(player_stats):
    """
    Oyuncunun istatistiklerine göre iniş bölgesi önerileri oluşturur
    """
    suggestions = {}

    # Agresiflik seviyesine göre iniş bölgeleri öner
    if player_stats.get('kd_ratio', 0) > 2.0:
        suggestions['aggressive'] = [
            "Pochinki - Yüksek oyuncu yoğunluğu, erken çatışmalar için ideal",
            "School/Apartments - Hızlı loot ve çatışma imkanı",
            "Bootcamp (Sanhok) - Yüksek riskli ama yüksek ödüllü bölge"
        ]
    else:
        suggestions['passive'] = [
            "Gatka - Orta seviye loot, daha az oyuncu",
            "Zharki - Uzak lokasyon, güvenli başlangıç",
            "Kampong (Sanhok) - Dengeli loot ve daha az çatışma"
        ]

    # Hareket tarzına göre iniş stratejileri
    if player_stats.get('avg_ride_distance', 0) > 3000:
        suggestions['vehicle_strategy'] = [
            "Araç rotaları yakınına inin (yol kenarları)",
            "Garage bulunan bölgeleri tercih edin",
            "Merkeze uzak ama araç bulabileceğiniz yerleri seçin"
        ]
    else:
        suggestions['on_foot_strategy'] = [
            "Merkeze yakın bölgelere inin",
            "Compound'lar arası mesafenin kısa olduğu bölgeleri seçin",
            "Yüksek loot yoğunluğu olan bölgeleri tercih edin"
        ]

    return suggestions