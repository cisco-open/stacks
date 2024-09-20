#!/usr/bin/env python3

# Copyright 2024 Cisco Systems, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

def main(string, public_key_path):
    import base64
    import cryptography.hazmat.backends
    import cryptography.hazmat.primitives.asymmetric.padding
    import cryptography.hazmat.primitives.ciphers
    import cryptography.hazmat.primitives.hashes
    import cryptography.hazmat.primitives.padding
    import cryptography.hazmat.primitives.serialization
    import os

    padder = cryptography.hazmat.primitives.padding.PKCS7(128).padder()
    padded = padder.update(string.encode()) + padder.finalize()

    symmetric_key = os.urandom(32)

    init_vector = os.urandom(12)
    init_vector_base64 = base64.b64encode(init_vector).decode("utf-8")

    encryptor = cryptography.hazmat.primitives.ciphers.Cipher(cryptography.hazmat.primitives.ciphers.algorithms.AES(symmetric_key), cryptography.hazmat.primitives.ciphers.modes.GCM(init_vector), backend=cryptography.hazmat.backends.default_backend()).encryptor()

    string_encrypted = encryptor.update(padded) + encryptor.finalize()
    string_encrypted_base64 = base64.b64encode(string_encrypted).decode("utf-8")

    encryptor_tag_base64 = base64.b64encode(encryptor.tag).decode("utf-8")

    with open(public_key_path, "rb") as f:
        public_key = cryptography.hazmat.primitives.serialization.load_pem_public_key(
            f.read(),
            backend = cryptography.hazmat.backends.default_backend(),
        )

    symmetric_key_encrypted_base64 = base64.b64encode(public_key.encrypt(
        symmetric_key,
        cryptography.hazmat.primitives.asymmetric.padding.OAEP(
            mgf = cryptography.hazmat.primitives.asymmetric.padding.MGF1(algorithm=cryptography.hazmat.primitives.hashes.SHA256()),
            algorithm = cryptography.hazmat.primitives.hashes.SHA256(),
            label = None,
        )
    )).decode("utf-8")

    return f"ENC[{symmetric_key_encrypted_base64};{encryptor_tag_base64};{init_vector_base64};{string_encrypted_base64}]"


if __name__ == "__main__":
    import cli_wrapper
    cli_wrapper.main(main)
