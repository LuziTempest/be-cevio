from flask import Blueprint, request
from pydantic import ValidationError

from app.middlewares.require_auth import token_required
from app.schemas.response import error_response, success_response
from app.schemas.result import (
    PortfolioGenerateResponse,
    PortfolioPhotoUpdateRequest,
    PortfolioSaveRequest,
    ResultDTO,
)
from app.services.file_service import save_user_file
from app.services.llm_service import generate_portfolio_json
from app.services.pdf_service import extract_text_from_pdf
from app.services.portfolio_service import (
    get_all_user_results,
    get_portfolio_by_title,
    get_result_details,
    save_portfolio_result,
    update_portfolio_photo,
)

portfolio_bp = Blueprint("portfolio", __name__)


@portfolio_bp.route("/photo", methods=["POST"])
@token_required
def upload_portfolio_photo(current_user):
    """
    Mengunggah file foto (Overwrite file fisik)
    Dan memperbarui database HANYA jika field foto masih kosong.
    """
    try:
        if "foto" not in request.files:
            return error_response(message="Tidak ada foto yang diunggah", status_code=400)

        foto_file = request.files["foto"]

        if foto_file.filename == "":
            return error_response(message="Nama file kosong", status_code=400)

        # 1. Simpan file ke storage (Otomatis menimpa foto_profil.jpg sebelumnya)
        foto_url = save_user_file(foto_file, current_user["id"])
        if not foto_url:
            return error_response(
                message="Format file tidak valid. Gunakan JPG, JPEG, atau PNG.",
                status_code=400,
            )

        # 2. Update database (Hanya jika field foto kosong)
        success, message = update_portfolio_photo(
            user_id=current_user["id"], foto_url=foto_url
        )

        if success:
            return success_response(
                data={"foto_url": foto_url}, message=message, status_code=200
            )
        else:
            return error_response(message=message, status_code=400)

    except Exception as e:
        return error_response(message=f"Terjadi kesalahan: {str(e)}", status_code=500)


@portfolio_bp.route("/generate", methods=["POST"])
@token_required
def generate_portfolio(current_user):
    """Endpoint untuk generate portofolio dari PDF menggunakan AI"""
    try:
        if "file" not in request.files:
            return error_response(message="Tidak ada file yang diunggah", status_code=400)

        file = request.files["file"]
        theme = request.form.get("theme", "profesional")
        focus = request.form.get("focus", "pengalaman")

        if file.filename == "" or not file.filename.lower().endswith(".pdf"):
            return error_response(message="File harus berupa PDF", status_code=400)

        # 1. Ekstrak teks dari PDF
        pdf_success, raw_text = extract_text_from_pdf(file)
        if not pdf_success:
            return error_response(message=raw_text, status_code=422)

        # 2. Generate JSON menggunakan LLM
        llm_success, portfolio_data = generate_portfolio_json(raw_text, theme, focus)
        if not llm_success:
            return error_response(message=portfolio_data, status_code=500)

        # 3. Validasi & Standarisasi menggunakan DTO
        response_dto = PortfolioGenerateResponse(
            user=current_user["name"],
            tema_terpilih=theme,
            fokus_terpilih=focus,
            data=portfolio_data,
        )

        return success_response(
            data=response_dto.dict(), message="Portofolio berhasil di-generate!"
        )

    except Exception as e:
        return error_response(
            message=f"Gagal generate portofolio: {str(e)}", status_code=500
        )


@portfolio_bp.route("", methods=["POST"])
@token_required
def save_portfolio(current_user):
    """Menyimpan hasil generate portofolio ke database"""
    try:
        raw_data = request.get_json()
        save_req = PortfolioSaveRequest(**raw_data)

        success, message, result_id = save_portfolio_result(
            user_id=current_user["id"],
            json_data=save_req.data.dict(),
            theme=save_req.tema_terpilih,
            focus=save_req.fokus_terpilih,
            title=save_req.title,
        )

        if success:
            return success_response(
                data={"id": result_id}, message=message, status_code=201
            )
        else:
            return error_response(message=message, status_code=400)

    except ValidationError as e:
        return error_response(
            message="Data portofolio tidak valid", status_code=400, errors=e.errors()
        )
    except Exception as e:
        return error_response(message=f"Terjadi kesalahan: {str(e)}", status_code=500)


@portfolio_bp.route("", methods=["GET"])
@token_required
def get_my_portfolios(current_user):
    """Mendapatkan daftar semua portofolio milik user"""
    try:
        results = get_all_user_results(current_user["id"])
        data = [ResultDTO.from_orm(r).dict(by_alias=True) for r in results]

        return success_response(data=data, message="Daftar portofolio berhasil diambil")
    except Exception as e:
        return error_response(message=f"Terjadi kesalahan saat mengambil data", status_code=500)


@portfolio_bp.route("/<int:result_id>", methods=["GET"])
@token_required
def get_portfolio_detail(current_user, result_id):
    """Mendapatkan detail portofolio berdasarkan ID (Private)"""
    try:
        result = get_result_details(result_id, current_user["id"])

        if not result:
            return error_response(message="Portofolio tidak ditemukan", status_code=404)

        return success_response(
            data=ResultDTO.from_orm(result).dict(by_alias=True),
            message="Detail portofolio berhasil diambil",
        )
    except Exception as e:
        return error_response(message=f"Terjadi kesalahan: {str(e)}", status_code=500)


@portfolio_bp.route("/<string:title>", methods=["GET"])
def get_public_portfolio(title):
    """Endpoint publik untuk mengambil portofolio berdasarkan judul (Slug)"""
    try:
        result = get_portfolio_by_title(title)

        if not result:
            return error_response(message="Portofolio tidak ditemukan", status_code=404)

        return success_response(
            data=ResultDTO.from_orm(result).dict(by_alias=True),
            message="Detail portofolio publik berhasil diambil",
        )
    except Exception as e:
        return error_response(message=f"Terjadi kesalahan: {str(e)}", status_code=500)
