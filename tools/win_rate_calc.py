def calculate_win_rate(player_data):
    """
    Oyuncunun kazanma oranını hesaplar
    """
    total_matches = len(player_data)
    if total_matches == 0:
        return 0

    wins = len(player_data[player_data['win_place'] == 1])
    win_rate = (wins / total_matches) * 100

    return {
        'total_matches': total_matches,
        'wins': wins,
        'win_rate': win_rate
    }

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
            'longest_kill': 0
        }

    # Kazanma oranı
    wins = len(player_data[player_data['win_place'] == 1])
    win_rate = (wins / total_matches) * 100

    # K/D oranı
    kills = player_data['kills'].sum()
    deaths = total_matches - wins  # Basitleştirilmiş hesaplama
    kd_ratio = kills / deaths if deaths > 0 else kills

    # Diğer istatistikler
    avg_damage = player_data['damage_dealt'].mean()

    # Hareket istatistikleri - eğer bu sütunlar yoksa varsayılan değerler kullan
    avg_walk_distance = player_data['walk_distance'].mean() if 'walk_distance' in player_data.columns else 0
    avg_ride_distance = player_data['ride_distance'].mean() if 'ride_distance' in player_data.columns else 0
    avg_swim_distance = player_data['swim_distance'].mean() if 'swim_distance' in player_data.columns else 0

    # Silah istatistikleri - eğer bu sütunlar yoksa varsayılan değerler kullan
    headshot_kills = player_data['headshot_kills'].sum() if 'headshot_kills' in player_data.columns else 0
    longest_kill = player_data['longest_kill'].max() if 'longest_kill' in player_data.columns else 0

    return {
        'total_matches': total_matches,
        'wins': wins,
        'win_rate': win_rate,
        'kills': kills,
        'deaths': deaths,
        'kd_ratio': kd_ratio,
        'avg_damage': avg_damage,
        'avg_walk_distance': avg_walk_distance,
        'avg_ride_distance': avg_ride_distance,
        'avg_swim_distance': avg_swim_distance,
        'headshot_kills': headshot_kills,
        'longest_kill': longest_kill
    }