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

def deepformat(value, params):
    if isinstance(value, dict):
        return {
            deepformat(key, params): deepformat(value, params)
            for key, value in value.items()
        }
    if isinstance(value, list):
        return [
            deepformat(item, params)
            for item in value
        ]
    if isinstance(value, str):
        return value.format(**params)
    return value


__all__ = [
    deepformat,
]
