import base64
import random
import struct
import time
from hashlib import blake2s
from typing import Optional, Tuple

import nacl.bindings
import nacl.encoding
import nacl.public
from twisted.application import internet
from twisted.internet.protocol import DatagramProtocol
from twisted.logger import Logger

from canarytokens import queries
from canarytokens.canarydrop import Canarydrop
from canarytokens.channel import InputChannel
from canarytokens.constants import INPUT_CHANNEL_WIREGUARD
from canarytokens.models import TokenTypes, WireguardTokenHit
from canarytokens.settings import SwitchboardSettings
from canarytokens.switchboard import Switchboard
from canarytokens.tokens import Canarytoken
from canarytokens.exceptions import NoCanarytokenFound
from canarytokens.wireguard import (
    AEAD,
    KDF2,
    MSG_INITIATION_FMT,
    MSG_INITIATION_LEN,
    MSG_INITIATION_MAX_TIME_DIFF,
    MSG_INITIATION_PREFIX,
    TAI64N_BASE,
    Device,
    getDevices,
    hash,
    mixhash,
    mixKey,
    sharedSecret,
)

log = Logger()

NOISE_CONSTRUCTION = "Noise_IKpsk2_25519_ChaChaPoly_BLAKE2s".encode("utf-8")
WG_IDENTIFIER = "WireGuard v1 zx2c4 Jason@zx2c4.com".encode("utf-8")
WG_LABEL_COOKIE = "cookie--".encode("utf-8")
ZERO_NONCE = b"\x00" * 12
BLAKE2S_128_SIZE = 16


class WireGuardProtocol(DatagramProtocol):
    INITIAL_CHAIN_KEY = hash(NOISE_CONSTRUCTION)
    INITIAL_HASH = mixhash(INITIAL_CHAIN_KEY, WG_IDENTIFIER)

    def __init__(
        self, channel: InputChannel, switchboard_settings: SwitchboardSettings
    ) -> None:
        self.channel = channel
        self.devices = getDevices(
            wg_private_key_seed=switchboard_settings.WG_PRIVATE_KEY_SEED,
            wg_private_key_n=switchboard_settings.WG_PRIVATE_KEY_N,
        )
        # Random test key
        device: Device = random.choice(self.devices)
        log.info(
            f"Console public key: {device.privateKey.public_key.encode(encoder=nacl.encoding.Base64Encoder)!r}"
        )

    def datagramReceived(
        self, data: bytes, src: Tuple[str, int]
    ) -> None:  # pragma: no cover
        log.debug(f"received data: {data!r} from src: {src}")
        # Supports only the Initiation message of WireGuard protocol
        #
        # All other message types and non-conforming data are dropped
        #
        if len(data) != MSG_INITIATION_LEN or not data.startswith(
            MSG_INITIATION_PREFIX
        ):
            return

        # MAC offsets at the end of message
        smac2 = len(data) - BLAKE2S_128_SIZE
        smac1 = smac2 - BLAKE2S_128_SIZE

        data_smac1 = data[:smac1]
        search_mac = data[smac1:smac2]

        try:
            device = next(
                filter(
                    lambda candidateDevice: search_mac
                    == blake2s(
                        data_smac1,
                        digest_size=BLAKE2S_128_SIZE,
                        key=candidateDevice.mac1_key,
                    ).digest(),
                    self.devices,
                )
            )
        except StopIteration:
            log.error(
                f"Could not find matching public key for message from {src}: {data!r}"
            )
            return

        mtype, sessionIndex, ephemeral, static, timestamp, mac1, mac2 = struct.unpack(
            MSG_INITIATION_FMT, data
        )

        hash0 = mixhash(self.INITIAL_HASH, device.privateKey.public_key.encode())
        hash1 = mixhash(hash0, ephemeral)
        chainKey0 = mixKey(self.INITIAL_CHAIN_KEY, ephemeral)
        ss = sharedSecret(device.privateKey.encode(), ephemeral)
        chainKey1, key0 = KDF2(chainKey0, ss)
        peerPK = AEAD(key0, ZERO_NONCE, static, hash1)

        hash2 = mixhash(hash1, static)
        chainKey2, key1 = KDF2(
            chainKey1, sharedSecret(device.privateKey.encode(), peerPK)
        )
        tai64nTimestamp = AEAD(key1, ZERO_NONCE, timestamp, hash2)
        if not tai64nTimestamp:
            log.debug("Timestamp not valid; Handshake not provably sent by peer key")
            return

        unix_seconds, nano = struct.unpack("!QI", tai64nTimestamp)
        unix_seconds -= TAI64N_BASE
        time_diff = abs(int(time.time()) - unix_seconds)
        if time_diff > MSG_INITIATION_MAX_TIME_DIFF:
            log.debug("Handshake timestamp too new or too old")
            return

        public_key = base64.b64encode(peerPK)
        token_value = queries.wireguard_keymap_get(public_key)
        if not token_value:
            raise NoCanarytokenFound
        canarytoken = Canarytoken(value=token_value)
        if not canarytoken:
            log.debug(
                f"No matching token for valid handshake with client key {public_key!r} from {src}. Expected when Canarytoken is deleted, but WG client config still in use."
            )
            return

        # TODO: If canarydrop no longer exists, delete key -> canarytoken mapping in WireGuard keymap
        canarydrop: Optional[Canarydrop] = queries.get_canarydrop(canarytoken)

        src_host = src[0]
        src_data = {
            "src_port": src[1],
            "server_public_key": device.privateKey.public_key.encode(
                encoder=nacl.encoding.Base64Encoder
            ),
            "client_public_key": public_key,
            "session_index": sessionIndex,
        }

        token_hit: WireguardTokenHit = canarytoken.create_token_hit(
            token_type=TokenTypes.WIREGUARD,
            input_channel=INPUT_CHANNEL_WIREGUARD,
            src_ip=src_host,
            hit_info={"src_data": src_data},
        )
        canarydrop.add_canarydrop_hit(token_hit=token_hit)
        log.debug(f"wireguard token hit: {token_hit}")

        self.channel.dispatch(canarydrop=canarydrop, token_hit=token_hit)


class ChannelWireGuard(InputChannel):
    CHANNEL = INPUT_CHANNEL_WIREGUARD

    def __init__(
        self,
        port: int,
        switchboard: Switchboard,
        switchboard_scheme: str,
        switchboard_hostname: str,
        switchboard_settings: SwitchboardSettings,
    ) -> None:
        InputChannel.__init__(
            self,
            switchboard=switchboard,
            switchboard_scheme=switchboard_scheme,
            switchboard_hostname=switchboard_hostname,
            name=self.CHANNEL,
            unique_channel=True,
        )
        self.service = internet.UDPServer(
            port,
            WireGuardProtocol(channel=self, switchboard_settings=switchboard_settings),
        )
