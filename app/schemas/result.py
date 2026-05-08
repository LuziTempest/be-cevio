# backend/app/schemas/result.py

def result_schema(result_obj):
    """Mengubah satu objek Result menjadi dictionary JSON"""
    if not result_obj:
        return None
    
    return {
        "id": result_obj.id,
        "theme": result_obj.theme,
        "focus": result_obj.focus,
        "foto": result_obj.foto,
        "data": result_obj.content, # Ini adalah JSON portofolio utuh
        "created_at": result_obj.created_at.isoformat() if result_obj.created_at else None
    }

def results_list_schema(results_list):
    """Mengubah list objek Result menjadi list of dictionaries"""
    return [result_schema(r) for r in results_list]