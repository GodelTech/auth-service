from Crypto.PublicKey import RSA
from src.business_logic.dto.rsa_keys_dto import RSAKeypair

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