import io

from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA

BLOCK_SIZE = 16
CHUNK_SIZE = BLOCK_SIZE * 1024 * 1024 + BLOCK_SIZE
TAG_SIZE = BLOCK_SIZE
CIPHERTXT_SIZE = CHUNK_SIZE - TAG_SIZE
NONCE_SIZE = BLOCK_SIZE


class Crypter:
    def __init__(self, public_pem: str = None, private_pem: str = None):
        if public_pem and private_pem:
            pass
        else:
            key = RSA.generate(2048)
            private_pem = key.export_key().decode()
            public_pem = key.publickey().export_key().decode()

        assert isinstance(public_pem, str)
        assert isinstance(private_pem, str)
        self.public_pem = public_pem.encode()
        self.private_pem = private_pem.encode()

    def crypt(self, data):
        return crypt(data, self.public_pem)

    def decrypt(self, data):
        return decrypt(data, self.private_pem)


def get_public_keys(pem):
    public_key = PKCS1_OAEP.new(RSA.import_key(pem))
    # symmetric_key = get_random_bytes(BLOCK_SIZE * 2)
    symmetric_key = b"12345678901234567890123456789012"
    enc_symmetric_key = public_key.encrypt(symmetric_key)
    return symmetric_key, enc_symmetric_key


def crypt(data: str, public_pem: bytes) -> bytes:
    data = data.encode("utf-8")
    file_out = io.BytesIO()
    file_in = io.BytesIO(data)
    symmetric_key, enc_symmetric_key = get_public_keys(public_pem)
    file_out.write(enc_symmetric_key)
    while True:
        dataChunk = file_in.read(CIPHERTXT_SIZE)
        if dataChunk:
            cipher = AES.new(symmetric_key, AES.MODE_GCM)
            file_out.write(cipher.nonce + b"".join(reversed(cipher.encrypt_and_digest(dataChunk))))
        else:
            break
    file_out.seek(0)
    return file_out.read()


def decrypt(data: bytes, private_pem: bytes):
    file_in = io.BytesIO(data)
    file_in.seek(0)
    file_out = io.BytesIO()
    key = RSA.import_key(private_pem)
    private_key = PKCS1_OAEP.new(key)
    enc_key_size = key.size_in_bytes()
    symmetric_key = private_key.decrypt(file_in.read(enc_key_size))
    nonce = file_in.read(NONCE_SIZE)
    while nonce:
        ciphertxtTag = file_in.read(CHUNK_SIZE)
        cipher = AES.new(symmetric_key, AES.MODE_GCM, nonce)
        file_out.write(cipher.decrypt_and_verify(ciphertxtTag[BLOCK_SIZE:], ciphertxtTag[:BLOCK_SIZE]))
        nonce = file_in.read(NONCE_SIZE)

    file_out.seek(0)
    return file_out.read().decode()
