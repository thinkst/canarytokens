from typing import Sequence, Tuple

import pytest

from canarytokens.tokens import Canarytoken
from canarytokens.wireguard import (
    AEAD,
    HMAC1,
    HMAC2,
    KDF1,
    KDF2,
    clientConfig,
    deleteCanarytokenPrivateKey,
    generateCanarytokenPrivateKey,
    getDevices,
    hash,
    mixhash,
    mixKey,
    sharedSecret,
)


@pytest.mark.parametrize(
    "key, nonce, cipherText, authText, expected_AEAD",
    [
        (
            b"\xbeY\xad\x9150\xd6\x8e\xcf\x9a}\xd9\xf0\xf8\xee\xb8Iu?#0\x97laA#\r\xdfyN%q",
            b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
            b"\xe2\x8e\x97l\xbe\x9c\x87\xce\xa4\x0b\xd5\xb0\xdd7\xad+!=\x15}CZf\x97\x9a\xf51rW\xb4\x94\xee\x14\xc5\xe3\xb6zhW\x80\x13~*\x05t\xa1\x18:",
            b"\xca\x85*\xc7\x19\xbd\x18\xeeF\xb8-\xe2y\x13\x99\x0f$B\xcf\xd76\x9c\xf5B\x0f\xbd\xb7\xf1\x84\xdbct",
            b"\xed\x05\xba\xb7\x80\x12\xd2(N\x04\xf8\x13\xfa\xf0\x9208Z\xc4e\xcf\xa6\x04-\x88v\x0ez'\xfamV",
        )
    ],
)
def test_AEAD(
    key: bytes, nonce: bytes, cipherText: bytes, authText: bytes, expected_AEAD: bytes
) -> None:
    assert AEAD(key, nonce, cipherText, authText) == expected_AEAD


@pytest.mark.parametrize(
    "key, ephemeral, expected_sharedSecret",
    [
        (
            b"fZ\xc2d,\x0f%\\57\x97)\x99\r\xc5\xae\x03=\xa2\x9cz\xfd=\x9e\x9es\xac\x86\xfbX\xa0\x9f",
            b"\xed\x05\xba\xb7\x80\x12\xd2(N\x04\xf8\x13\xfa\xf0\x9208Z\xc4e\xcf\xa6\x04-\x88v\x0ez'\xfamV",
            b"\x95pq\x8c':kz\xe0\xdd\x85Ys\xfe\xcf\x17sB\x16\xd6\x00\xdb\x9fE*\x06\x02\x89QX\xc0j",
        ),
    ],
)
def test_sharedSecret(
    key: bytes, ephemeral: bytes, expected_sharedSecret: bytes
) -> None:
    assert sharedSecret(key, ephemeral) == expected_sharedSecret


@pytest.mark.parametrize(
    "data, expected_hash",
    [
        (
            b"Noise_IKpsk2_25519_ChaChaPoly_BLAKE2s",
            b"`\xe2m\xae\xf3'\xef\xc0.\xc35\xe2\xa0%\xd2\xd0\x16\xebB\x06\xf8rw\xf5-8\xd1\x98\x8bx\xcd6",
        ),
        (
            b"mac1----\xad\x93uvq5\x87\x8e(*\x82Zu\xf4\x16v\xbb\xb4G\xd4\xcd\xa6t\n\x97\x0bt\x8f~i\xc3\x17",
            b"\x12\xe2g\xa5\xad\x80\xaf\xb8K\x00\xd4\x86\x08v\xca\xf9\x0b\xf3\x80\xf7\x89y0Y\x17\xf4\x15\xdc\x1ctk\xee",
        ),
    ],
)
def test_hash(data: bytes, expected_hash: bytes) -> None:
    assert hash(data) == expected_hash


@pytest.mark.parametrize(
    "key, in0, expected_hmac1",
    [
        (
            b"`\xe2m\xae\xf3'\xef\xc0.\xc35\xe2\xa0%\xd2\xd0\x16\xebB\x06\xf8rw\xf5-8\xd1\x98\x8bx\xcd6",
            b"A\x8a\xc9h\xd0\xc6Sz\xf4\r\xf3\xd4D\xae \x8a\xe6n}\t\xf9Y\xea\x9c\xb2\xf0\xa2\xc7\x89\xb4\x00d",
            b"\x06rd`H\xb0U\x80\xf6\xcc4\x1d\x05\x98IIDL@N\t\xe0\xd9\x19\x91\x9c\xc4\x92;kD:",
        ),
    ],
)
def test_HMAC1(key: bytes, in0: bytes, expected_hmac1: bytes) -> None:
    assert HMAC1(key, in0) == expected_hmac1


@pytest.mark.parametrize(
    "key, in0, in1, expected_HMAC2",
    [
        (
            b'\xdc#Fa#\xf0\xe7"-\xdf\xc4J3wVu]\x8a~S\xdb\x83$\xf9\xa0\xd5,Y\xed\xa1\xec\xb1',
            b"P\xa1\xfc^\xe3J\xd6\x8ai`r(\xfb\x89\xce[\x85\x8fc\x1f\x92\xecLD\x97&\xeb\x88>%\x92\xf1",
            b"\x02",
            b"?\x1a\x89\xa3M\xf9\x1e\x17KQ\xeb\x81R\x1e8\xc3\n\x9c\xba-\xa7\x8dS\xc1T\xe2YK\x9b\xd2 C",
        ),
    ],
)
def test_HMAC2(key: bytes, in0: bytes, in1: bytes, expected_HMAC2: bytes) -> None:
    assert HMAC2(key, in0, in1) == expected_HMAC2


@pytest.mark.parametrize(
    "key, input, expected_kdf1",
    [
        (
            b"`\xe2m\xae\xf3'\xef\xc0.\xc35\xe2\xa0%\xd2\xd0\x16\xebB\x06\xf8rw\xf5-8\xd1\x98\x8bx\xcd6",
            b"\xf7\xee\x05\xfd\xaeL\x90O\x14O\xd8)/s\xc8\xc7\x11kLC\x83.\x91]\x0cO\xf1\xe2\xa5\xe3\xcd\x1e",
            b"\x07\x849\xf3\xbc\xdb\xdc\xf7N\xb6\x16l\x16\xb5\xb5\xa6\x12\xcd\xd6\xec%\x93\x80\x88\xf0^\xff\r\xb5\x11\xbf?",
        ),
    ],
)
def test_KDF1(key: bytes, input: bytes, expected_kdf1: bytes) -> None:
    assert KDF1(key, input) == expected_kdf1


@pytest.mark.parametrize(
    "key, input, expected_kdf2",
    [
        (
            b"k\x11h\xa8\x06\xbaf\xc6$7\x9b\x8bgX\x82\xc1\xfd\x9e\xdc\x0c3\xd3n\xec\xcaoM\xb8/\x90\xe8\x03",
            b"\x96E\xf9\x05p\xac!\xa2\x95\x0f\x18m\xce\xaa \x9b%\xe6\xb7\x11\x18\xcf[-T\xd1F<\x14\xee\x8aF",
            (
                b"Hl\xbe\x08\x07u=\x18V\xdb\xfb\xe3\xe9\xb0\x1a(w\x04\xe456\xf86a\xcb\x88\x7f&\xa9\x15DU",
                b"\xbeY\xad\x9150\xd6\x8e\xcf\x9a}\xd9\xf0\xf8\xee\xb8Iu?#0\x97laA#\r\xdfyN%q",
            ),
        ),
    ],
)
def test_KDF2(key: bytes, input: bytes, expected_kdf2: bytes) -> None:
    assert KDF2(key, input) == expected_kdf2


@pytest.mark.parametrize(
    "hash, data, expected_mixhash",
    [
        (
            b'"\x11\xb3a\x08\x1a\xc5fi\x12C\xdbE\x8a\xd52-\x9clf"\x93\xe8\xb7\x0e\xe1\x9ce\xba\x07\x9e\xf3',
            b"\x81\xdds\x0b\xda\xb5\x02\x8f\xdc\xb0\xd8\x05\n\x8e\xba\xd6\x03\x17\x10\xef~\xf0h\xac:Fq\xad\x05\x8e\xc8\n",
            b'"L\x83o\xc9\xe8\x88\x13\xcc\xd1Y\xd2t\xa2a z.\x8f\x94\x1a\xfamF\\\x89\xa2Z\xd3\xbd\x85-',
        ),
    ],
)
def test_mixhash(hash, data, expected_mixhash):
    assert mixhash(hash, data) == expected_mixhash


@pytest.mark.parametrize(
    "c, data, expected_mixKey",
    [
        (
            b"`\xe2m\xae\xf3'\xef\xc0.\xc35\xe2\xa0%\xd2\xd0\x16\xebB\x06\xf8rw\xf5-8\xd1\x98\x8bx\xcd6",
            b"\xf7\xee\x05\xfd\xaeL\x90O\x14O\xd8)/s\xc8\xc7\x11kLC\x83.\x91]\x0cO\xf1\xe2\xa5\xe3\xcd\x1e",
            b"\x07\x849\xf3\xbc\xdb\xdc\xf7N\xb6\x16l\x16\xb5\xb5\xa6\x12\xcd\xd6\xec%\x93\x80\x88\xf0^\xff\r\xb5\x11\xbf?",
        ),
    ],
)
def test_mixKey(c, data, expected_mixKey):
    assert mixKey(c, data) == expected_mixKey


@pytest.mark.parametrize(
    "wg_private_key_seed, wg_private_key_n, expected_devices",
    [
        (
            "vk/GD+frlhve/hDTTSUvqpQ/WsQtioKAri0Rt5mg7dw=",
            "3",
            [
                (
                    b"go\xa4\xb3\xe8\x15\xf3S\x1c\xe5\xea\x94\xd0\xaf\xc7\xe3\x92\x11?s\xd9\xdf\xe1(\x04^\xb5\xb9X\x9c\xdb\xc4",
                    b"\x12\xe2g\xa5\xad\x80\xaf\xb8K\x00\xd4\x86\x08v\xca\xf9\x0b\xf3\x80\xf7\x89y0Y\x17\xf4\x15\xdc\x1ctk\xee",
                ),
                (
                    b"\x9e%\xfd]\x1d\xe1\xf9k0Y\xebpp\xabU-\xa6(\xaa\x9d\xeb0\xf9\xd6\xb7\xf5\xd8\x06\xc8\x08\xb5\x15",
                    b"6\xc63$\x9b\x1d\x97\xf26\x17\xbf)\xdd\xd2\xa5\x9d\xf84\x8d_\xb7\xb1\xce~@\xd4<\x8b\xd7\x01%\x94",
                ),
                (
                    b"fZ\xc2d,\x0f%\\57\x97)\x99\r\xc5\xae\x03=\xa2\x9cz\xfd=\x9e\x9es\xac\x86\xfbX\xa0\x9f",
                    b"dN)\xd5\xb5\xf2\xa1\xc7:\xecH\x9b\x82]\xc9\x94 '\xb9\x1a\x94\xf4iz\xb4N\xeb\x0bb\x841\xf8",
                ),
            ],
        ),
        ("", "", []),
    ],
)
def test_getDevices(
    wg_private_key_seed: str,
    wg_private_key_n: str,
    expected_devices: Sequence[Tuple[bytes, bytes]],
) -> None:
    if not wg_private_key_seed:
        try:
            devices = getDevices(wg_private_key_seed, wg_private_key_n)
        except ValueError:
            return
        raise AssertionError("getDevices() should fail without wg_private_key_seed.")

    devices = getDevices(wg_private_key_seed, wg_private_key_n)
    mod_devices = [(bytes(device.privateKey), device.mac1_key) for device in devices]
    assert mod_devices == expected_devices


@pytest.mark.parametrize(
    "wg_private_key_seed, wg_private_key_n",
    [
        ("vk/GD+frlhve/hDTTSUvqpQ/WsQtioKAri0Rt5mg7dw=", "3"),
    ],
)
def test_clientConfig(wg_private_key_seed: str, wg_private_key_n: str, setup_db):
    canarytoken = Canarytoken()
    wg_key = generateCanarytokenPrivateKey(
        canarytoken=canarytoken.value(),
        wg_private_key_seed=wg_private_key_seed,
        wg_private_key_n=wg_private_key_n,
    )
    config = clientConfig(
        wg_key=wg_key,
        public_ip="1.2.3.4",
        wg_private_key_seed=wg_private_key_seed,
        wg_private_key_n=wg_private_key_n,
    )
    assert config.startswith("[Interface]")
    deleteCanarytokenPrivateKey(wg_key)
