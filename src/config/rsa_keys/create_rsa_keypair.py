import logging

from Crypto.PublicKey import RSA

from .dto import RSAKeypair

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class CreateRSAKeypair:
    def execute(self) -> RSAKeypair:
        key = RSA.generate(2048)
        private_key = key.export_key("PEM")
        public_key = key.public_key().export_key("PEM")
        # print(f"create_rsa_keypair.py; private_key {private_key}")
        # print(f"create_rsa_keypair.py; public_key {public_key}")

        return RSAKeypair(
            private_key=private_key,
            public_key=public_key,
            n=key.n,
            e=key.e,
        )
