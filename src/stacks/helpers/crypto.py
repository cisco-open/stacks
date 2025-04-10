import base64
import cryptography.hazmat.backends
import cryptography.hazmat.primitives.asymmetric.padding
import cryptography.hazmat.primitives.asymmetric.rsa
import cryptography.hazmat.primitives.ciphers
import cryptography.hazmat.primitives.hashes
import cryptography.hazmat.primitives.padding
import cryptography.hazmat.primitives.serialization
import os


def genkey(public_key_path, private_key_path):
    """Generate a public/private key pair to use with 'encrypt' and 'decrypt'.

    Keyword arguments:
      public_key_path[pathlib.Path]: where to store the generated public key
      private_key_path[pathlib.Path]: where to store the generated private key
    """
    key = cryptography.hazmat.primitives.asymmetric.rsa.generate_private_key(
        backend=cryptography.hazmat.backends.default_backend(),
        key_size=2**11,
        public_exponent=2**16 + 1,
    )
    with open(private_key_path, "wb") as f:
        f.write(
            key.private_bytes(
                encoding=cryptography.hazmat.primitives.serialization.Encoding.PEM,
                format=cryptography.hazmat.primitives.serialization.PrivateFormat.PKCS8,
                encryption_algorithm=cryptography.hazmat.primitives.serialization.NoEncryption(),
            )
        )
    with open(public_key_path, "wb") as f:
        f.write(
            key.public_key().public_bytes(
                encoding=cryptography.hazmat.primitives.serialization.Encoding.PEM,
                format=cryptography.hazmat.primitives.serialization.PublicFormat.SubjectPublicKeyInfo,
            )
        )


def encrypt(public_key_path, string):
    """Encrypt 'string' using 'public_key_path'.

    Keyword arguments:
      public_key_path[pathlib.Path]: path to public key
      string[str]: string to encrypt
    """
    padder = cryptography.hazmat.primitives.padding.PKCS7(128).padder()
    padded = padder.update(string.encode()) + padder.finalize()

    symmetric_key = os.urandom(32)

    init_vector = os.urandom(12)
    init_vector_base64 = base64.b64encode(init_vector).decode("utf-8")

    encryptor = cryptography.hazmat.primitives.ciphers.Cipher(
        cryptography.hazmat.primitives.ciphers.algorithms.AES(symmetric_key),
        cryptography.hazmat.primitives.ciphers.modes.GCM(init_vector),
        backend=cryptography.hazmat.backends.default_backend(),
    ).encryptor()

    string_encrypted = encryptor.update(padded) + encryptor.finalize()
    string_encrypted_base64 = base64.b64encode(string_encrypted).decode("utf-8")

    encryptor_tag_base64 = base64.b64encode(encryptor.tag).decode("utf-8")

    with open(public_key_path, "rb") as f:
        public_key = cryptography.hazmat.primitives.serialization.load_pem_public_key(
            f.read(),
            backend=cryptography.hazmat.backends.default_backend(),
        )

    symmetric_key_encrypted_base64 = base64.b64encode(
        public_key.encrypt(
            symmetric_key,
            cryptography.hazmat.primitives.asymmetric.padding.OAEP(
                mgf=cryptography.hazmat.primitives.asymmetric.padding.MGF1(algorithm=cryptography.hazmat.primitives.hashes.SHA256()),
                algorithm=cryptography.hazmat.primitives.hashes.SHA256(),
                label=None,
            ),
        )
    ).decode("utf-8")

    return f"ENC[{symmetric_key_encrypted_base64};{encryptor_tag_base64};{init_vector_base64};{string_encrypted_base64}]"


def decrypt(data, private_key_path=os.getenv("STACKS_PRIVATE_KEY_PATH"), must_decrypt=True):
    """Decrypt 'data' using 'private_key_path'.

    Keyword arguments:
      data[any]: any data structure
      private_key_path[pathlib.Path]: path to private key
      must_decrypt[bool]: whether decryption should succeed (if False and fails, returns encrypted value)
    """
    if isinstance(data, str) and data.startswith("ENC[") and data.endswith("]"):
        (
            symmetric_key_encrypted_base64,
            encryptor_tag_base64,
            init_vector_base64,
            string_encrypted_base64,
        ) = data.removeprefix("ENC[").removesuffix("]").split(";")

        private_key_paths = private_key_path.split(",")
        for i in range(len(private_key_paths)):
            with open(private_key_paths[i], "rb") as f:
                private_key = cryptography.hazmat.primitives.serialization.load_pem_private_key(
                    f.read(),
                    password=None,
                    backend=cryptography.hazmat.backends.default_backend(),
                )

            try:
                symmetric_key = private_key.decrypt(
                    base64.b64decode(symmetric_key_encrypted_base64.encode()),
                    cryptography.hazmat.primitives.asymmetric.padding.OAEP(
                        mgf=cryptography.hazmat.primitives.asymmetric.padding.MGF1(algorithm=cryptography.hazmat.primitives.hashes.SHA256()),
                        algorithm=cryptography.hazmat.primitives.hashes.SHA256(),
                        label=None,
                    ),
                )
                break
            except ValueError as e:
                if i < len(private_key_paths)-1:
                    continue
                elif must_decrypt:
                    raise e
                else:
                    return data

        init_vector = base64.b64decode(init_vector_base64.encode())

        string_encrypted = base64.b64decode(string_encrypted_base64.encode())

        encryptor_tag = base64.b64decode(encryptor_tag_base64.encode())

        decryptor = cryptography.hazmat.primitives.ciphers.Cipher(
            cryptography.hazmat.primitives.ciphers.algorithms.AES(symmetric_key),
            cryptography.hazmat.primitives.ciphers.modes.GCM(init_vector, encryptor_tag),
            backend=cryptography.hazmat.backends.default_backend(),
        ).decryptor()

        unpadder = cryptography.hazmat.primitives.padding.PKCS7(128).unpadder()
        padded = decryptor.update(string_encrypted) + decryptor.finalize()

        string_decrypted = unpadder.update(padded) + unpadder.finalize()

        return string_decrypted.decode("utf-8")

    elif isinstance(data, list):
        return [decrypt(private_key_path=private_key_path, data=item, must_decrypt=must_decrypt) for item in data]

    elif isinstance(data, dict):
        return {key: decrypt(private_key_path=private_key_path, data=value, must_decrypt=must_decrypt) for key, value in data.items()}

    return data
