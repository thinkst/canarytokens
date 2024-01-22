import base64
import hmac
import random
import struct
import textwrap
from enum import Enum
from functools import cache
from hashlib import blake2s
from typing import MutableSequence, NamedTuple, Sequence, Tuple

import nacl.bindings
import nacl.encoding
import nacl.public
import nacl.utils
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
from twisted.logger import Logger

from canarytokens import queries

log = Logger()

DEFAULT_PORT = 51820
WG_LABEL_MAC1 = "mac1----".encode("utf-8")
BLAKE2S_256_SIZE = 32
WG_KEY_LEN = 32


class MessageType(Enum):
    Initiation = 1
    Response = 2
    CookieReply = 3
    Transport = 4


MSG_INITIATION_FMT = "<II32s48s28s16s16s"
MSG_INITIATION_LEN = struct.calcsize(MSG_INITIATION_FMT)
MSG_INITIATION_PREFIX = struct.pack("<I", MessageType.Initiation.value)
MSG_INITIATION_MAX_TIME_DIFF = 5

TAI64N_BASE = 0x400000000000000A


class Device(NamedTuple):
    privateKey: nacl.public.PrivateKey
    mac1_key: bytes


# Cryptographic primitives
def AEAD(key: bytes, nonce: bytes, cipherText: bytes, authText: bytes) -> bytes:
    return ChaCha20Poly1305(key).decrypt(nonce, cipherText, authText)


def sharedSecret(key: bytes, ephemeral: bytes) -> bytes:
    """Diffie-Hellman shared secret for Curve25519"""
    return nacl.bindings.crypto_scalarmult(n=key, p=ephemeral)


def hash(data: bytes) -> bytes:
    return blake2s(data, digest_size=BLAKE2S_256_SIZE).digest()


# Noise protocol helpers for key derivation
#
# Follows WireGuard-Go userspace noise-helpers.go
def HMAC1(key: bytes, in0: bytes) -> bytes:
    return hmac.new(key, in0, blake2s).digest()


def HMAC2(key: bytes, in0: bytes, in1: bytes) -> bytes:
    return hmac.new(key, in0 + in1, blake2s).digest()


def KDF1(key: bytes, input: bytes) -> bytes:
    return HMAC1(HMAC1(key, input), b"\x01")


def KDF2(key: bytes, input: bytes) -> Tuple[bytes, bytes]:
    prk = HMAC1(key, input)
    t0 = HMAC1(prk, b"\x01")
    t1 = HMAC2(prk, t0, b"\x02")
    return t0, t1


def mixhash(hash: bytes, data: bytes) -> bytes:
    return blake2s(hash + data, digest_size=BLAKE2S_256_SIZE).digest()


def mixKey(c: bytes, data: bytes) -> bytes:
    return KDF1(c, data)


@cache
def getDevices(
    wg_private_key_seed: str,
    wg_private_key_n: str,
) -> Sequence[Device]:
    """Generates devices the first time it's called, thereafter returns the same."""
    keySeed = wg_private_key_seed
    if not keySeed:
        log.error("Required setting WG_PRIVATE_KEY_SEED not defined in a *.env file")
        # TODO (DESIGN): decide what to do here... original just dies:
        # exit()
        raise ValueError(
            "Required setting WG_PRIVATE_KEY_SEED not defined in a *.env file"
        )

    keyN = int(wg_private_key_n)

    private_key_string = nacl.utils.randombytes_deterministic(
        size=WG_KEY_LEN * keyN, seed=base64.b64decode(keySeed)
    )
    devices: MutableSequence[Device] = []
    for i in range(0, WG_KEY_LEN * keyN, WG_KEY_LEN):
        privateKey = nacl.public.PrivateKey(
            private_key_string[i : i + WG_KEY_LEN]  # noqa: E203
        )
        mac1_key = hash(WG_LABEL_MAC1 + privateKey.public_key.encode())
        devices.append(Device(privateKey, mac1_key))
    return devices


def generateCanarytokenPrivateKey(
    canarytoken: str, wg_private_key_seed: str, wg_private_key_n: str
) -> str:
    privateKey = nacl.public.PrivateKey.generate()
    public_key = privateKey.public_key.encode(encoder=nacl.encoding.Base64Encoder)
    device_key_idx = random.randrange(
        len(getDevices(wg_private_key_seed, wg_private_key_n))
    )
    queries.wireguard_keymap_add(public_key, canarytoken)
    wg_key = f"{device_key_idx}|{privateKey.encode(encoder=nacl.encoding.Base64Encoder).decode()}"
    return wg_key


def deleteCanarytokenPrivateKey(wg_key: str) -> None:
    _, private_key = wg_key.split("|")
    privateKey = nacl.public.PrivateKey(
        private_key.encode("utf-8"), encoder=nacl.encoding.Base64Encoder
    )
    public_key = privateKey.public_key.encode(encoder=nacl.encoding.Base64Encoder)
    queries.wireguard_keymap_del(public_key)


def clientConfig(
    wg_key: str, public_ip: str, wg_private_key_seed: str, wg_private_key_n: str
) -> str:
    device_key_idx_raw, private_key = wg_key.split("|")
    device_key_idx = int(device_key_idx_raw)
    config = textwrap.dedent(
        f"""
        [Interface]
          PrivateKey = {private_key}
          Address = 192.168.123.107/32

        [Peer]
          PublicKey = {getDevices(wg_private_key_seed, wg_private_key_n)[
            device_key_idx]
            .privateKey.public_key.encode(encoder=nacl.encoding.Base64Encoder)
            .decode()}
          AllowedIPs = 192.168.1.0/24
          Endpoint = {public_ip}:{DEFAULT_PORT}
          PersistentKeepalive = {30 * (random.randrange(10) + 1)}
    """
    ).strip()  # Keep Alive *must* be non-zero to trigger token
    return config
