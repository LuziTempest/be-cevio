# backend/app/schemas/user.py

def user_schema(user_obj):
    """
    Mengubah satu objek ORM User menjadi dictionary yang aman dikirim ke frontend.
    Password hash sengaja dihilangkan demi keamanan.
    """
    if not user_obj:
        return None
    
    return {
        "id": user_obj.id,
        "name": user_obj.name,
        "email": user_obj.email,
        "created_at": user_obj.created_at.isoformat() if user_obj.created_at else None
    }

def users_list_schema(users_list):
    """Mengubah list berisi objek ORM menjadi list of dictionaries"""
    return [user_schema(user) for user in users_list]