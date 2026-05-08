# backend/app/schemas/response.py
from flask import jsonify

def success_response(data=None, message="Permintaan berhasil", status_code=200):
    """Format standar untuk respon sukses"""
    return jsonify({
        "status": "success",
        "message": message,
        "data": data
    }), status_code

def error_response(message="Terjadi kesalahan", status_code=400, errors=None):
    """Format standar untuk respon error"""
    response_body = {
        "status": "error",
        "message": message
    }
    if errors:
        response_body["details"] = errors
        
    return jsonify(response_body), status_code