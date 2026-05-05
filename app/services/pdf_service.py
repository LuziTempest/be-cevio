import pdfplumber

def extract_text_from_pdf(file_stream):
    """
    Fungsi untuk membaca file PDF dan mengembalikan teks mentahnya.
    file_stream: objek file yang dikirim dari form HTTP
    """
    extracted_text = ""
    try:
        # Buka file stream langsung tanpa menyimpannya ke hard disk server
        with pdfplumber.open(file_stream) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    extracted_text += text + "\n"
        
        # Validasi jika PDF kosong atau berupa gambar (hasil scan)
        if not extracted_text.strip():
            return False, "PDF kosong atau berisi gambar (tidak bisa mendeteksi teks)."
            
        return True, extracted_text.strip()
    except Exception as e:
        return False, f"Gagal membaca PDF: {str(e)}"