from fastapi import HTTPException, Request, status


def get_current_user(request: Request) -> dict:
    """API用の認証ガード。未ログインなら401を返す（ページ遷移用のリダイレクトはmain.py側で行う）。"""
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="ログインが必要です。")
    return user
