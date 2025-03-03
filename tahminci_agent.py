import os
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# 📌 Veri dosyasının yolu
csv_path = "pubg_final.csv"

# 🔍 Dosyanın var olup olmadığını kontrol et
if not os.path.exists(csv_path):
    print(f"❌ HATA: '{csv_path}' dosyası bulunamadı! Lütfen dosyanın doğru yerde olduğundan emin olun.")
    exit()

# ✅ CSV dosyasını oku
df = pd.read_csv(csv_path)

# 🔹 Kullanılacak özellikler
features = ['kills', 'damageDealt', 'walkDistance', 'weaponsAcquired']

# 🔍 Gerekli sütunlar dosyada var mı kontrol et
missing_columns = [col for col in features + ['winPlacePerc'] if col not in df.columns]
if missing_columns:
    print(f"❌ HATA: Eksik sütunlar var: {missing_columns}")
    exit()

# 📌 Büyük veri setlerini küçültmek için örnekleme (Hızlandırma amacıyla)
df_sample = df.sample(n=10000, random_state=42)

X = df_sample[features]
y = df_sample['winPlacePerc'].apply(lambda x: 1 if x > 0.5 else 0)  # Kazananları etiketle

# 📊 Veriyi eğitim ve test setlerine ayır
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 🌲 Random Forest Modeli Eğitme
model = RandomForestClassifier(n_estimators=50, random_state=42, n_jobs=-1)  # Daha hızlı eğitim için azaltıldı
model.fit(X_train, y_train)

# 📌 Modeli Kaydet
joblib.dump(model, "pubg_model.pkl")
print("✅ Model başarıyla kaydedildi: pubg_model.pkl")

# 📌 Doğruluk Testipython 

y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"🎯 Model Doğruluğu: {accuracy:.2f}")
