from datetime import datetime, timedelta, timezone

import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

JWT_SECRET = "asfjldbajfndalfhalndfkadbfadlujhadjlf"
JWT_ALGORITHM = "HS256"

bearer = HTTPBearer()


def token_uret(kullanici_adi: str):
    bitis = datetime.now(timezone.utc) + timedelta(minutes=30)

    return jwt.encode(
        {"sub": kullanici_adi, "exp": bitis},
        JWT_SECRET,
        algorithm=JWT_ALGORITHM,
    )


def sifre_kontrol(
    kimlik: HTTPAuthorizationCredentials = Depends(bearer),
):
    try:
        veri = jwt.decode(
            kimlik.credentials,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM],
        )
        kullanici_adi = veri.get("sub")

        if kullanici_adi is None:
            raise HTTPException(status_code=401, detail="Token içinde kullanıcı yok")

        return kullanici_adi

    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token geçersiz veya süresi dolmuş")