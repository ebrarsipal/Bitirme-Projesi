import os
import pandas as pd
import json
import re
from openai import OpenAI

# 1️⃣ Kök klasör yolu
root_dir = r"<EXCEL_PATH>"

# 2️⃣ JSON formatında sonuçları saklayacağımız liste
result = []



client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key="<YOUR_aPI_KEY>",
)

def generate_comment(columns: list) -> str:
    """
    Excel başlıklarına göre OpenRouter'dan kısa bir kullanım amacı alır.
    """
    prompt = (
        f"Aşağıdaki başlıklara sahip bir Excel dosyası var:\n"
        f"{columns}\n\n"
        f"Bu dosya genelde hangi amaçla kullanılır? Kısa bir açıklama ver."
    )

    response = client.chat.completions.create(
        model="openai/gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "Sen bir sekme anlama asistanısın. "
                    "Yapısal veri başlıklarına bakarak dosyanın hangi amaçla kullanılabileceğini "
                    "kısa ve açık bir cümleyle açıklarsın."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content.strip()

# 3️⃣ Klasörleri gez
for folder_name in os.listdir(root_dir):
    folder_path = os.path.join(root_dir, folder_name)
    if os.path.isdir(folder_path):
        for file_name in os.listdir(folder_path):
            if file_name.endswith(".xlsx") or file_name.endswith(".xls"):
                file_path = os.path.join(folder_path, file_name)
                
                try:
                    # Excel'den başlıkları oku
                    df = pd.read_excel(file_path, nrows=1)
                    columns = df.columns.tolist()

                    # Alanları düzgün formatla
                    if len(columns) == 1:
                        shown_fields = columns[0]
                    else:
                        shown_fields = ", ".join(columns[:-1]) + f" ve {columns[-1]}"

                    # Dosya adı temizle & sekme formatla
                    sekme_adi = os.path.splitext(file_name)[0]
                    sekme_adi_clean = re.sub(r"\s*\(.*?\)", "", sekme_adi).strip()
                    sekme = f"{folder_name}/{sekme_adi_clean}"

                    # 📌 Fonksiyonu çağır — dosya hakkında yorum al
                    yorum = generate_comment(columns)

                    # 📌 cumle: başlık açıklaması + LLM yorumu
                    cumle = f"{sekme_adi_clean} sekmesi, her kayıt için {shown_fields} bilgilerini içerir. {yorum}"

                    # Sonuç listesine ekle
                    entry = {
                        "sekme": sekme,
                        "cumle": cumle,
                        "shown_fields": shown_fields
                    }

                    result.append(entry)

                except Exception as e:
                    print(f"Hata: {file_name} okunamadı. Sebep: {e}")


# 6️⃣ Sonucu JSON dosyasına kaydet (isteğe bağlı)
with open("output.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=4)

# 7️⃣ Ekrana yazdır
print(json.dumps(result, ensure_ascii=False, indent=4))
