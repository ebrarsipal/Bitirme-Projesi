@echo off
echo [1/5] Ortam hazırlanıyor...

:: Python varsa pip'i güncelle, yoksa hata verme
python -m ensurepip --upgrade >nul 2>&1

:: Gerekli kütüphaneleri yükle
echo [2/5] Gerekli kütüphaneler yükleniyor...
pip install --upgrade pip >nul 2>&1
pip install pandas openai streamlit sentence-transformers >nul 2>&1

:: Veri hazırlama dizinine git
echo [3/5] Veri hazırlama işlemleri başlatılıyor...
cd veri_hazırlama

:: İlk veri çıkarma dosyasını çalıştır
python extract_sturcted_docs.py

:: İkinci veri çıkarma dosyasını çalıştır
python extract_sekme_and_columns.py

:: Ana dizine geri dön
cd ..

:: Arayüz klasörüne geç
cd erp_chatbot

:: Streamlit uygulamasını başlat
echo [4/5] Uygulama başlatılıyor...
streamlit run agent_app.py

pause
