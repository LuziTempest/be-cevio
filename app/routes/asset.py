from flask import Blueprint, request

from app.middlewares.require_auth import token_required
from app.schemas.response import error_response, success_response
from app.services.file_service import save_user_file

asset_bp = Blueprint("asset", __name__)


@asset_bp.route("/photo", methods=["POST"])
@token_required
def upload_photo(current_user):
    """
    Endpoint generic: Hanya mengunggah file foto ke storage.
    Tidak melakukan perubahan apa pun ke database portofolio.
    """
    if "foto" not in request.files:
        return error_response(message="Tidak ada foto yang diunggah", status_code=400)

    foto_file = request.files["foto"]

    if foto_file.filename == "":
        return error_response(message="Nama file kosong", status_code=400)

    foto_url = save_user_file(foto_file, current_user["id"])

    if foto_url:
        return success_response(
            data={"foto_url": foto_url},
            message="Foto berhasil diunggah ke storage",
            status_code=200,
        )
    else:
        return error_response(
            message="Format file tidak valid. Gunakan JPG, JPEG, atau PNG.",
            status_code=400,
        )
