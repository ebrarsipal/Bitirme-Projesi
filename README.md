# Bitirme-Projesi
2025 BTÜ Bitirme Projesi Kapsamında Yapılmıştır.



# 🤖 ERP Agent – LLM Destekli SQL Üretici

Bu proje, kurumsal Excel dosyalarınız ve SQL sorgularınızı kullanarak doğal dilde sorguları otomatik olarak çalıştırılabilir SQL'e dönüştüren bir yapay zekâ sistemidir. Özellikle ERP sistemleriyle çalışan kurumlar için tasarlanmıştır.

## 📦 Özellikler

- ✅ Türkçe doğal dilden SQL üretimi  
- ✅ Streamlit ile kolay arayüz  
- ✅ Excel başlıklarından otomatik açıklama çıkarımı  
- ✅ Embed tabanlı sekme eşleştirme  
- ✅ LLM (OpenRouter/Mistral) kullanımı  
- ✅ API KEY ile güvenli yapılandırma  

## 📁 Klasör Yapısı

```
proje_klasörü/
├── erp_agent.bat                           # Projeyi başlatan otomasyon betiği
├── veri_hazırlama/
│   ├── extract_sturcted_docs.py           # Excel başlıklarını işler
│   ├── extract_sekme_and_columns.py       # SQL view'lardan tablo ve kolon eşleşmeleri çıkarır
├── erp_chatbot/
│   └── agent_app.py                       # Streamlit kullanıcı arayüzü
├── exceller/
│   └── views_and_sqls.xlsx                # SQL view metinlerinin olduğu Excel
├── output/
│   ├── output.json                        # Sekme açıklamaları
│   ├── sekme_columns_with_names_comment.json  # SQL yapısal eşleşme sonuçları
```

## ⚙️ Kurulum

### 1. Python 3.10+ yüklü olduğundan emin olun  
[Python İndir](https://www.python.org/downloads/)

### 2. Gerekli kütüphaneleri yükleyin

```bash
pip install pandas openai streamlit sentence-transformers
```

### 3. OpenRouter API Key Ayarlama

OpenRouter üzerinden bir API anahtarı alın: https://openrouter.ai

Aşağıdaki gibi `client = OpenAI(...)` kısmını **`agent_app.py`** dosyasına ekleyin:

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="sk-...sizin-api-anahtarınız..."
)
```

## 🚀 Projeyi Başlatmak

### `erp_agent.bat` dosyasını çalıştırın (Windows)

Bu dosya sırasıyla:
1. Gerekli kütüphaneleri yükler  
2. `veri_hazırlama/` dizinindeki dosyaları çalıştırır  
3. Streamlit arayüzünü başlatır

```bash
./erp_agent.bat
```

Alternatif olarak manuel olarak:

```bash
cd veri_hazırlama
python extract_sturcted_docs.py
python extract_sekme_and_columns.py
cd ../erp_chatbot
streamlit run agent_app.py
```

## 💬 Örnek Kullanım

Streamlit arayüzünde:

📝 Soru: `Bu ay kaç tane baz araç siparişi aldık?`  
🧠 Sistem:
- Embed ile en uygun sekmeyi bulur (örn: `satış/Tüm Baz Araç Siparişleri`)
- SQL üretir:  
```sql
SELECT COUNT(*) FROM RN01_BazAracOzellikleri WHERE MONTH(Tarih) = MONTH(GETDATE()) AND YEAR(Tarih) = YEAR(GETDATE())
```

## 🧠 Kullanılan Teknolojiler

| Teknoloji            | Açıklama |
|----------------------|----------|
| Python               | Backend dili |
| Streamlit            | UI oluşturmak için |
| SentenceTransformer  | Embed karşılaştırma |
| OpenRouter (Mistral) | LLM tabanlı SQL üretimi |
| Pandas               | Excel işleme |

## 📌 Notlar

- `output.json` ve `sekme_columns_with_names_comment.json` dosyaları sistemin doğru çalışması için gereklidir. Bu dosyalar `veri_hazırlama` klasöründe çalıştırılan scriptlerle otomatik oluşur.
- Girdiğiniz API Key gizli kalmalıdır, `.gitignore` veya `.env` dosyası üzerinden dışa sızması engellenmelidir.

## 📄 Lisans

MIT Lisansı ile lisanslanmıştır.

## 👤 Geliştirici

> Bu proje, veri mühendisliği ve doğal dil işleme alanlarını birleştirerek daha erişilebilir veri analiz araçları üretmeyi amaçlamaktadır.
