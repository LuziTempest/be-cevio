import glob
import os

from flask import current_app

# Ekstensi PDF bisa dihapus karena kamu tidak jadi mengunggah file CV
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_user_file(file, user_id):
    """
    Menyimpan file ke folder spesifik milik user.
    Memastikan nama file distandarkan dan menimpa/menghapus foto lama.
    """
    if file and allowed_file(file.filename):
        ext = file.filename.rsplit(".", 1)[1].lower()
        filename = f"foto_profil.{ext}"
        user_folder_name = f"user_{user_id}"
        user_folder_path = os.path.join(
            current_app.config["UPLOAD_FOLDER"], user_folder_name
        )

        if not os.path.exists(user_folder_path):
            os.makedirs(user_folder_path)

        existing_files = glob.glob(os.path.join(user_folder_path, "foto_profil.*"))
        for old_file in existing_files:
            try:
                os.remove(old_file)
            except Exception as e:
                print(f"Peringatan: Gagal menghapus file lama {old_file} - {e}")

        file_path = os.path.join(user_folder_path, filename)
        file.save(file_path)

        return f"/static/uploads/{user_folder_name}/{filename}"

    return None
