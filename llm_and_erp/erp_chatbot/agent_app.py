import streamlit as st
from sentence_transformers import SentenceTransformer, util
import requests
import json
import re

# === 📌 MODEL & VERİLER ===
@st.cache_resource
def load_embedding_model():
    return SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

embedding_model = load_embedding_model()

# Sekme embed JSON
sekme_descriptions_path = "<output_json_path>"  # Örn: r"C:\Users\ebrars\Desktop\veri_hazırlama\output.json"
with open(sekme_descriptions_path, "r", encoding="utf-8") as f:
    structured_docs = json.load(f)

sekme_texts = [d["cumle"] for d in structured_docs]
sekme_embeddings = embedding_model.encode(sekme_texts, convert_to_tensor=True)

# Aliaslı kolon JSON
with open("sekme_columns_with_names_comment.json", "r", encoding="utf-8") as f:
    sekme_columns_data = json.load(f)

def clean_user_query(user_query: str) -> str:
    """
    Kullanıcı sorgusunu basit kurallarla temizler.
    """
    # Küçük harfe çevir
    q = user_query.lower()

    # Gereksiz bağlaçları sil
    q = re.sub(r'\b(lütfen|acaba|rica ederim|acil|mümkünse)\b', '', q)

    # Fazla boşlukları sil
    q = re.sub(r'\s+', ' ', q).strip()

    return q

def rewrite_query_with_llm(raw_query, model="mistral"):
    system_prompt = """
Sen bir sorgu düzenleme asistanısın.
Kullanıcının verdiği Türkçe soruyu daha net, kısa ve LLM için anlaşılır şekilde yeniden yaz.
Açıklama ekleme, sadece düzenlenmiş soruyu döndür.

"""
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": raw_query}
        ],
        "stream": False
    }

    response = requests.post("http://localhost:11434/api/chat", json=data)
    result = response.json()["message"]["content"]
    return result.strip()    
# === 🔍 Sekme Bul ===
def find_best_matching_sekme(user_query):
    query_embedding = embedding_model.encode(user_query, convert_to_tensor=True)
    cos_scores = util.cos_sim(query_embedding, sekme_embeddings)[0]
    index = cos_scores.argmax().item()
    return structured_docs[index]["sekme"]

# === ⚙️ Ollama SQL ===
def ollama_sql_filter(prompt, sekme_name, model="mistral"):
    for sekme in sekme_columns_data:
        if sekme["sekme"] == sekme_name:
            alias_table_map = {}
            for col in sekme["columns"]:
                alias_table_map[col["alias"]] = col["table"]
            alias_table_map = {alias: table for alias, table in alias_table_map.items()}
            columns = [f"{col['alias']}.{col['column']}" for col in sekme["columns"]]
            break
    else:
        raise ValueError(f"Sekme bulunamadı: {sekme_name}")

    from_clauses = [f"{table} AS {alias}" for alias, table in alias_table_map.items()]

    system_prompt = f"""
Sen bir SQL sorgu oluşturma asistanısın.
Kullanıcı Türkçe bir istek verecek. Sen SELECT * FROM ... WHERE ... formatında TAM SQL sorgusu üret.Olmayan tabloları asla ama asla kullanma.

Dikkat et:
- Kullanabileceğin tablolar ve aliaslar: {', '.join(from_clauses)}
- Kullanabileceğin kolonlar: {', '.join(columns)}
- Aliasları hem FROM kısmında hem WHERE kısmında doğru kullan.
- SADECE çalıştırılabilir tam SQL döndür, başka açıklama ekleme.
"""

    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "stream": False
    }

    response = requests.post("http://localhost:11434/api/chat", json=data)
    result = response.json()["message"]["content"]
    return result

# === 📊 Streamlit Arayüz ===
st.title("🔍 SQL Agent")

user_query = st.text_input("💬 Sorgunuzu girin:", placeholder="Örn: 1234 şasi no lu araç stokta var mı?")

if st.button("Sorguyu Çalıştır"):
    if not user_query.strip():
        st.warning("Lütfen bir sorgu girin.")
    else:
        with st.spinner("⏳ İşleniyor..."):
            
            clean_query = clean_user_query(user_query)
            llm_refined_query = rewrite_query_with_llm(clean_query)
            best_sekme = find_best_matching_sekme(llm_refined_query)
            sql_result = ollama_sql_filter(llm_refined_query, best_sekme)

        st.success(f"🎯 En alakalı sekme: **{best_sekme}**")
        st.code(sql_result, language="sql")
