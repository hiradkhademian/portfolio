# generate_token.py
from app import create_app
from flask_jwt_extended import create_access_token
from datetime import timedelta

app = create_app()
app.app_context().push()

# <-- PUT the simulator user's numeric id here:
USER_ID = 1

token = create_access_token(
    identity=str(USER_ID),        # identity MUST be string
    expires_delta=timedelta(days=3650)  # 10 years
)

print(token)