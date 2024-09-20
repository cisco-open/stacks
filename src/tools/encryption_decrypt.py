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

def main(string, private_key_path):
    import base64
    import cryptography.hazmat.backends
    import cryptography.hazmat.primitives.asymmetric.padding
    import cryptography.hazmat.primitives.hashes
    import cryptography.hazmat.primitives.padding
    import cryptography.hazmat.primitives.serialization

    symmetric_key_encrypted_base64, encryptor_tag_base64, init_vector_base64, string_encrypted_base64 = string.removeprefix("ENC[").removesuffix("]").split(";")

    with open(private_key_path, "rb") as key_file:
        symmetric_key = cryptography.hazmat.primitives.serialization.load_pem_private_key(
            key_file.read(),
            password = None,
            backend = cryptography.hazmat.backends.default_backend(),
        ).decrypt(
            base64.b64decode(symmetric_key_encrypted_base64.encode()),
            cryptography.hazmat.primitives.asymmetric.padding.OAEP(
                mgf = cryptography.hazmat.primitives.asymmetric.padding.MGF1(algorithm=cryptography.hazmat.primitives.hashes.SHA256()),
                algorithm = cryptography.hazmat.primitives.hashes.SHA256(),
                label = None,
            )
        )

    decryptor = cryptography.hazmat.primitives.ciphers.Cipher(
        cryptography.hazmat.primitives.ciphers.algorithms.AES(symmetric_key),
        cryptography.hazmat.primitives.ciphers.modes.GCM(
            base64.b64decode(init_vector_base64.encode()),
            base64.b64decode(encryptor_tag_base64.encode()),
        ),
        backend = cryptography.hazmat.backends.default_backend(),
    ).decryptor()
    padded = decryptor.update(base64.b64decode(string_encrypted_base64.encode())) + decryptor.finalize()

    unpadder = cryptography.hazmat.primitives.padding.PKCS7(128).unpadder()
    unpadded = unpadder.update(padded) + unpadder.finalize()

    return unpadded.decode("utf-8")


if __name__ == "__main__":
    import cli_wrapper
    cli_wrapper.main(main)
