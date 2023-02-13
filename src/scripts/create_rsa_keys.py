import logging

from Crypto.PublicKey import RSA

from src.scripts.dto import RSAKeypair

logger = logging.getLogger(__name__)


class CreateRSAKeypair:
    def execute(self) -> RSAKeypair:
        key = RSA.generate(2048)
        private_key = key.export_key("PEM")
        public_key = key.public_key().export_key("PEM")

        return RSAKeypair(
            private_key=private_key,
            public_key=public_key,
            n=key.n,
            e=key.e,
        )
