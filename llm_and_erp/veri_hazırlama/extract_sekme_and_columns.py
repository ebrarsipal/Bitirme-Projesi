import os
import pandas as pd
import re
from openai import OpenAI
import json

# === 1️⃣ ===
# Excel klasörü
root_dir = "<EXCEL_PATH>"

# Tüm Excel başlıkları burada toplanacak
excel_column_map = {}
client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key="<YOUR_API_KEY>",
)

# === 2️⃣ ===
# Tüm Excel dosyalarını tara ve başlıklarını kaydet
for folder_name in os.listdir(root_dir):
    folder_path = os.path.join(root_dir, folder_name)
    if os.path.isdir(folder_path):
        for file_name in os.listdir(folder_path):
            if file_name.endswith(".xlsx") or file_name.endswith(".xls"):
                file_path = os.path.join(folder_path, file_name)
                try:
                    df = pd.read_excel(file_path, nrows=1)
                    excel_column_map[file_name.lower()] = df.columns.tolist()
                except Exception as e:
                    print(f"Hata: {file_name} başlık okunamadı. Sebep: {e}")
                    
def generate_comment(columns: list) -> str:
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
# === 3️⃣ ===
# SQL parse eden fonksiyon
def extract_columns_and_table_mapping(sql_text, excel_column_map, excel_filename=None):
    alias_table_map = {}

    # FROM/JOIN alias eşlemesi
    from_joins = re.findall(
        r"(FROM|JOIN)\s+([\w\.]+)\s+(AS\s+)?(\w+)",
        sql_text,
        flags=re.IGNORECASE
    )
    for _, table_name, _, alias in from_joins:
        alias_table_map[alias] = table_name

    # SELECT bloğu
    select_match = re.search(r"SELECT(.*?)FROM", sql_text, re.DOTALL | re.IGNORECASE)
    if not select_match:
        return []

    select_block = select_match.group(1)
    lines = select_block.split("\n")
    columns = []

    for line in lines:
        line = line.strip().rstrip(",")
        if not line:
            continue
        if re.match(r"CASE|IIF|\(", line, re.IGNORECASE):
            continue

        # AS varsa split et
        shown_name = None
        if re.search(r"\s+AS\s+", line, re.IGNORECASE):
            parts = re.split(r"\s+AS\s+", line, flags=re.IGNORECASE)
            line = parts[0].strip()
            shown_name = parts[1].strip()
        else:
            shown_name = None  # henüz boş

        # Alias + kolon ayır
        if "." in line:
            alias, column = [p.strip() for p in line.split(".", 1)]
        else:
            alias = None
            column = line.strip()

        # Parantez sil
        column = re.sub(r"[()]", "", column)
        

        table_name = alias_table_map.get(alias) if alias else None

        # --- Excel başlıklarından name bul ---
        matched_name = shown_name
        if not matched_name and excel_filename:
            excel_headers = excel_column_map.get(excel_filename.lower(), [])
            for head in excel_headers:
                if head.lower().replace(" ", "") == column.lower():
                    matched_name = head
                    break

        # matched_name hala yoksa column kullan
        matched_name = matched_name or column

        if column and table_name:
            columns.append({
                "table": table_name,
                "alias": alias,
                "column": column,
                "name": matched_name
                
            })

    return columns

# === 4️⃣ ===
# Excel ve SQL eşleştir
excel_path = r"<VIEWS_AND_SQL_EXCEL_PATH>"
df = pd.read_excel(excel_path)

result = []
for idx, row in df.iterrows():
    sekme = row[0]
    sql_text = row[1]

    # Bu satırın Excel dosyasını tahmin et → ör: views_and_sqls.xlsx
    # Senin gerçek senaryonda daha iyi logic gerekebilir.
    excel_filename = os.path.basename(excel_path)

    columns = extract_columns_and_table_mapping(sql_text, excel_column_map, excel_filename)
    tables = sorted(list({col["table"] for col in columns}))
    shown_headers = [col["name"] for col in columns]
    comment = generate_comment(shown_headers)

    tables = sorted(list({col["table"] for col in columns}))

    result.append({
        "sekme": sekme,
        "tables": tables,
        "columns": columns,
        "yorum": comment
    })

# === 5️⃣ ===
# JSON kaydet
with open("sekme_columns_with_names_comment.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=4)

print(json.dumps(result, ensure_ascii=False, indent=4))
