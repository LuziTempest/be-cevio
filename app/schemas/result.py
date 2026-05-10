from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ==========================================
# SUB-MODELS (Struktur Portofolio)
# ==========================================
class ProfilDTO(BaseModel):
    nama: str
    email: str
    linkedin: Optional[str] = ""
    github: Optional[str] = ""
    deskripsi_diri: str


class PendidikanDTO(BaseModel):
    institusi: str
    jurusan: str
    tahun: str


class PengalamanKerjaDTO(BaseModel):
    posisi: str
    perusahaan: str
    durasi: str
    deskripsi: List[str]


class ProyekDTO(BaseModel):
    nama_proyek: str
    deskripsi: str
    teknologi: List[str]


class PortfolioDataDTO(BaseModel):
    profil: ProfilDTO
    pendidikan: List[PendidikanDTO]
    pengalaman_kerja: List[PengalamanKerjaDTO]
    proyek: List[ProyekDTO]
    keahlian: List[str]


# ==========================================
# REQUEST DTOs
# ==========================================
class PortfolioSaveRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    data: PortfolioDataDTO
    tema_terpilih: str
    fokus_terpilih: str
    foto: Optional[str] = None


class PortfolioPhotoUpdateRequest(BaseModel):
    foto: str  # URL foto yang sudah diupload via /assets/photo


# ==========================================
# RESPONSE DTOs
# ==========================================
class ResultDTO(BaseModel):
    id: int
    title: str
    theme: str
    focus: str
    foto: Optional[str]
    content: PortfolioDataDTO = Field(..., alias="data")
    created_at: Optional[datetime]

    class Config:
        from_attributes = True
        populate_by_name = True


class PortfolioGenerateResponse(BaseModel):
    user: str
    tema_terpilih: str
    fokus_terpilih: str
    data: PortfolioDataDTO


# ==========================================
# LEGACY SCHEMAS (Keep for compatibility)
# ==========================================
def result_schema(result_obj):
    if not result_obj:
        return None

    return {
        "id": result_obj.id,
        "title": getattr(result_obj, 'title', None),
        "theme": result_obj.theme,
        "focus": result_obj.focus,
        "foto": result_obj.foto,
        "data": result_obj.content,
        "created_at": result_obj.created_at.isoformat()
        if result_obj.created_at
        else None,
    }


def results_list_schema(results_list):
    return [result_schema(r) for r in results_list]
