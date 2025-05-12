import pandas as pd
import os

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

def get_player_data(df, player_id=None):
    """
    Belirli bir oyuncunun verilerini getirir veya oyuncu ID belirtilmemişse
    tüm veri setini döndürür
    """
    if player_id and player_id in df['player_id'].values:
        return df[df['player_id'] == player_id]
    return df.head(10)  # Eğer belirli bir oyuncu bulunamazsa ilk 10 satırı döndür