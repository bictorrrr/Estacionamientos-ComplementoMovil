from fastapi import Request

def get_current_user_web(request: Request):
    user_id = request.session.get("user_id")

    return user_id