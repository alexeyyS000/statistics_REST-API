from datetime import datetime

import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from users.models import Token


class JWT:
    def encode(payload) -> str:
        # payload['creation_time'] = str(datetime.utcnow())
        return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

    def decode(token: str):
        try:
            payload = jwt.decode(
                jwt=token,
                key=settings.SECRET_KEY,
                algorithms=[
                    "HS256",
                ],
            )
        except jwt.InvalidSignatureError:
            return None
        return payload

    # def decode(self, token: str, secret: str):
    #     try:
    #         payload = jwt.decode(token, secret, algorithms=[self._config.algorithm], issuer=self._config.issuer)
    #         return Payload.model_validate(payload), None
    #     except InvalidTokenError as e:
    #         return None, ErrorObj(type='jwt', message=str(e))
