from fastapi import APIRouter, HTTPException, Response, Request
from app.core.auth import verify_password, create_token, revoke_token, change_password, verify_token
from app.models import LoginReq, ChangePasswordReq

router = APIRouter()

@router.post("/login")
def login(req: LoginReq, response: Response):
    if verify_password(req.password):
        token = create_token()
        response.set_cookie(key="ea_token", value=token, httponly=True)
        return {"token": token}
    raise HTTPException(status_code=401, detail="Invalid password")

@router.post("/logout")
def logout(request: Request, response: Response):
    token = request.cookies.get("ea_token")
    if token:
        revoke_token(token)
    response.delete_cookie("ea_token")
    return {"message": "Logged out"}

@router.post("/change_password")
def change_pwd(req: ChangePasswordReq):
    if not verify_password(req.old_password):
        raise HTTPException(status_code=401, detail="Invalid old password")
    change_password(req.new_password)
    return {"message": "Password changed successfully"}

@router.get("/check")
def check_auth(request: Request):
    token = request.cookies.get("ea_token")
    if token and verify_token(token):
        return {"authenticated": True}
    return {"authenticated": False}
