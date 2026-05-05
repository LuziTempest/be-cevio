import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load API Key dari .env
load_dotenv()
api_key = os.getenv("LLM_API_KEY")

if not api_key:
    print("Error: LLM_API_KEY tidak ditemukan di file .env")
    exit()

genai.configure(api_key=api_key)

print("Berhasil terhubung. Berikut adalah daftar model yang bisa kamu gunakan:")
print("-" * 50)

# Looping untuk mencari model yang mendukung fitur generate text
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    print(f"Gagal mengambil daftar model: {e}")