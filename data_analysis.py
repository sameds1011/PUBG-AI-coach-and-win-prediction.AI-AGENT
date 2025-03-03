import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 📂 PUBG verisini yükle
df = pd.read_csv("data/pubg_final.csv")

# 🏆 İlk 5 satırı göster
print(df.head())

# 📊 Temel istatistikleri incele
print(df.describe())

# 🎯 Eksik değerleri kontrol et
print(df.isnull().sum())

# 📈 Öldürme sayısı dağılımı
plt.figure(figsize=(10, 5))
sns.histplot(df['kills'], bins=20, kde=True)
plt.title("Öldürme Sayısı Dağılımı")
plt.show()
