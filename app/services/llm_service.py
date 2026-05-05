import os
import json
import google.generativeai as genai

def generate_portfolio_json(raw_text, theme, focus):
    """
    Mengirim teks mentah CV ke LLM dan mengembalikan JSON terstruktur.
    """
    # Konfigurasi API Key dari file .env
    genai.configure(api_key=os.getenv("LLM_API_KEY"))
    
    # Gunakan model Gemini 1.5 Flash (Cepat & hemat biaya)
    model = genai.GenerativeModel('gemini-2.5-flash-lite')

    # Merancang instruksi (Prompt)
    prompt = f"""
    Kamu adalah seorang ahli pembuat website portofolio.
    Tugasmu adalah mengekstrak informasi dari teks CV berikut dan mengubahnya menjadi format JSON yang valid.

    PREFERENSI PENGGUNA:
    - Tema Desain: "{theme}". Sesuaikan gaya bahasa pada 'deskripsi_diri' agar terkesan {theme}. 
      (Misal: jika kreatif, gunakan bahasa yang energik. Jika profesional, gunakan bahasa formal dan tegas).
    - Fokus Utama: "{focus}". Berikan detail ekstra, elaborasi lebih panjang, dan prioritaskan data yang berkaitan dengan {focus}.

    TEKS CV:
    {raw_text}

    SKEMA JSON YANG WAJIB DIKEMBALIKAN (Jangan tambahkan key di luar ini):
    {{
        "profil": {{
            "nama": "...",
            "email": "...",
            "linkedin": "...",
            "github": "...",
            "deskripsi_diri": "..."
        }},
        "pendidikan": [
            {{ "institusi": "...", "jurusan": "...", "tahun": "..." }}
        ],
        "pengalaman_kerja": [
            {{ "posisi": "...", "perusahaan": "...", "durasi": "...", "deskripsi": ["...", "..."] }}
        ],
        "proyek": [
            {{ "nama_proyek": "...", "deskripsi": "...", "teknologi": ["...", "..."] }}
        ],
        "keahlian": ["...", "..."]
    }}
    """

    try:
        # Panggil API Gemini dengan mode JSON paksa (Strict JSON Output)
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                temperature=0.4 # Suhu rendah agar data tidak terlalu berhalusinasi
            )
        )
        
        # Parsing string balasan LLM menjadi objek dictionary Python
        json_data = json.loads(response.text)
        return True, json_data

    except json.JSONDecodeError:
        return False, "LLM gagal mengembalikan format JSON yang valid."
    except Exception as e:
        return False, f"Terjadi kesalahan pada LLM: {str(e)}"