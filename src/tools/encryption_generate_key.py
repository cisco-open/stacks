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

def main(public_key_path, private_key_path):
    import cryptography.hazmat.backends
    import cryptography.hazmat.primitives.serialization
    import cryptography.hazmat.primitives.asymmetric.rsa

    key = cryptography.hazmat.primitives.asymmetric.rsa.generate_private_key(
        backend = cryptography.hazmat.backends.default_backend(),
        key_size = 2**11,
        public_exponent = 2**16+1,
    )
    with open(private_key_path, "wb") as f:
        f.write(key.private_bytes(
            encoding = cryptography.hazmat.primitives.serialization.Encoding.PEM,
            format = cryptography.hazmat.primitives.serialization.PrivateFormat.PKCS8,
            encryption_algorithm = cryptography.hazmat.primitives.serialization.NoEncryption(),
        ))
    with open(public_key_path, "wb") as f:
        f.write(key.public_key().public_bytes(
            encoding = cryptography.hazmat.primitives.serialization.Encoding.PEM,
            format = cryptography.hazmat.primitives.serialization.PublicFormat.SubjectPublicKeyInfo,
        ))


if __name__ == "__main__":
    import cli_wrapper
    cli_wrapper.main(main)
