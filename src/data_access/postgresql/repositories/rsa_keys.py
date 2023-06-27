from typing import Optional

from sqlalchemy import exists, select, insert
from sqlalchemy.orm import Session

from src.config.rsa_keys import RSAKeypair
from src.data_access.postgresql.tables.rsa_keys import RSA_keys

class RSAKeysRepository:

    def get_keys_from_repository(self, session: Session) -> Optional[RSA_keys]:
        result = session.execute(select(RSA_keys))
        rsa_keys_list = result.scalars().all()
        rsa_keys = rsa_keys_list[-1] if len(rsa_keys_list) > 0 else None
        return rsa_keys

    def put_keys_to_repository(self, rsa_keys: RSAKeypair, session: Session) -> None:
        session.execute(insert(RSA_keys).values(
            private_key=rsa_keys.private_key,
            public_key=rsa_keys.public_key,
            n=rsa_keys.n,
            e=rsa_keys.e
        ))
        session.commit()

    def validate_keys_exists(self, session: Session) -> bool:
        result = session.execute(
            select([1]).where(exists().where(RSA_keys.id.isnot(None)).select_from(RSA_keys))
        )
        return result.scalars().first() is not None

