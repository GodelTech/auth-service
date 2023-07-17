from Crypto.PublicKey import RSA
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from src.data_access.postgresql.repositories import RSAKeysRepository
from src.data_access.postgresql.tables.rsa_keys import RSA_keys
from .dto import RSAKeypair

class RSAKeysService:

    def __init__(
            self,
            sync_session_factory: sessionmaker,
            rsa_keys_repo: RSAKeysRepository
    ) -> None:
        self.session = sync_session_factory
        self.rsa_keys_repo = rsa_keys_repo

    def get_rsa_keys(self) -> RSA_keys:
        try:
            with self.session() as session:
                if self.rsa_keys_repo.validate_keys_exists(session=session):
                    self.rsa_keys = self.rsa_keys_repo.get_keys_from_repository(session)
                else:
                    self.rsa_keys = self.create_rsa_keys()                         # RSAKeypair
                    self.rsa_keys_repo.put_keys_to_repository(rsa_keys=self.rsa_keys, session=session)
                    self.rsa_keys = self.rsa_keys_repo.get_keys_from_repository(session=session)  # RSA_keys
        except OperationalError:
            self.rsa_keys = None
        return self.rsa_keys

    def create_rsa_keys(self) -> RSAKeypair:    # or -> RSA_keys
        key = RSA.generate(2048)
        private_key = key.export_key("PEM")
        public_key = key.public_key().export_key("PEM")

        self.rsa_keys = RSAKeypair(
            private_key=private_key,
            public_key=public_key,
            n=key.n,
            e=key.e,
        )
        return self.rsa_keys