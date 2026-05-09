import os
import glob
from flask import current_app

# Ekstensi PDF bisa dihapus karena kamu tidak jadi mengunggah file CV
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_user_file(file, user_id):
    """
    Menyimpan file ke folder spesifik milik user.
    Memastikan nama file distandarkan dan menimpa/menghapus foto lama.
    """
    if file and allowed_file(file.filename):
        # 1. Ekstrak ekstensi file aslinya (jpg / png / jpeg)
        ext = file.filename.rsplit('.', 1)[1].lower()
        
        # 2. Paksa nama file menjadi standar untuk semua user
        filename = f"foto_profil.{ext}"
        
        # 3. Tentukan letak folder user
        user_folder_name = f"user_{user_id}"
        user_folder_path = os.path.join(current_app.config['UPLOAD_FOLDER'], user_folder_name)
        
        # Jika folder belum ada, buatkan
        if not os.path.exists(user_folder_path):
            os.makedirs(user_folder_path)
            
        # 4. FITUR CLEANUP (Mencegah penumpukan file beda ekstensi)
        # Cari semua file yang berawalan "foto_profil." di folder user tersebut, lalu hapus.
        existing_files = glob.glob(os.path.join(user_folder_path, "foto_profil.*"))
        for old_file in existing_files:
            try:
                os.remove(old_file)
            except Exception as e:
                print(f"Peringatan: Gagal menghapus file lama {old_file} - {e}")
        
        # 5. Simpan file yang baru dengan nama yang sudah distandarkan
        file_path = os.path.join(user_folder_path, filename)
        file.save(file_path)
        
        # 6. Kembalikan URL yang aman untuk disimpan ke Database
        # Output selalu seragam: /static/uploads/user_X/foto_profil.jpg (atau .png)
        return f"/static/uploads/{user_folder_name}/{filename}"
        
    return None