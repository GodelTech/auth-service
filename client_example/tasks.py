from celery import Celery
from sqlalchemy import insert, select, update
from sqlalchemy.orm import sessionmaker

from client_example.db.database import engine
from client_example.db.models import UserInfo
from client_example.utils import client

app = Celery("tasks")
app.config_from_object("client_example.config.celeryconfig")


@app.task
def add_users_from_identity_server(access_token: str):
    userinfo = client.get_user_info(access_token)
    session_factory = sessionmaker(engine, expire_on_commit=False)
    with session_factory() as session:
        user = session.execute(
            select(UserInfo).where(UserInfo.email == userinfo["email"])
        ).scalar_one_or_none()
        if user is None:
            session.execute(insert(UserInfo).values(**userinfo))
            session.commit()
            return "New user added"
        else:
            session.execute(update(UserInfo).values(**userinfo))
            session.commit()
            return "Updated user's data"
