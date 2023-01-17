import logging

from Crypto.PublicKey import RSA
from .dto import RSAKeypair


logger = logging.getLogger('is_app')


class CreateRSAKeypair:
    def execute(self) -> RSAKeypair:
        key = RSA.generate(2048)
        private_key = key.export_key('PEM')
        public_key = key.public_key().export_key('PEM')

        return RSAKeypair(
            private_key=private_key, 
            public_key=public_key
        )
