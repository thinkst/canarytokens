import textwrap
from twisted.internet.protocol import DatagramProtocol
import nacl.public
import nacl.bindings
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
from pyblake2 import blake2s
import hmac
from enum import Enum
import collections
import struct
import base64
import queries
import random
import settings
import time

from twisted.logger import Logger
log = Logger()

DEFAULT_PORT = 51820

NOISE_CONSTRUCTION = "Noise_IKpsk2_25519_ChaChaPoly_BLAKE2s".encode('utf-8')
WG_IDENTIFIER = "WireGuard v1 zx2c4 Jason@zx2c4.com".encode('utf-8')
WG_LABEL_MAC1 = "mac1----".encode('utf-8')
WG_LABEL_COOKIE = "cookie--".encode('utf-8')
ZERO_NONCE = "\x00" * 12
BLAKE2S_256_SIZE = 32
BLAKE2S_128_SIZE = 16
WG_KEY_LEN = 32
class MessageType(Enum):
    Initiation = 1
    Response = 2
    CookieReply = 3
    Transport = 4

MSG_INITIATION_FMT = "<II32s48s28s16s16s"
MSG_INITIATION_LEN = struct.calcsize(MSG_INITIATION_FMT)
MSG_INITIATION_PREFIX = struct.pack('<I', MessageType.Initiation.value)
MSG_INITIATION_MAX_TIME_DIFF = 5

TAI64N_BASE = 0x400000000000000a

Device = collections.namedtuple('Device', 'privateKey,mac1_key')

# Cryptographic primitives
def AEAD(key, nonce, cipherText, authText):
    return ChaCha20Poly1305(key).decrypt(nonce, cipherText, authText)

def sharedSecret(key, ephemeral):
    """Diffie-Hellman shared secret for Curve25519"""
    return nacl.bindings.crypto_scalarmult(n=key, p=ephemeral)

def hash(data):
    return blake2s(data, digest_size=BLAKE2S_256_SIZE).digest()

# Noise protocol helpers for key derivation
#
# Follows WireGuard-Go userspace noise-helpers.go
def HMAC1(key, in0):
    return hmac.new(key, in0, blake2s).digest()

def HMAC2(key, in0, in1):
    return hmac.new(key, in0+in1, blake2s).digest()

def KDF1(key, input):
    return HMAC1(HMAC1(key, input), "\x01")

def KDF2(key, input):
    prk = HMAC1(key, input)
    t0 = HMAC1(prk, "\x01")
    t1 = HMAC2(prk, t0, "\x02")
    return t0, t1

def mixhash(hash, data):
    return blake2s(hash + data, digest_size=BLAKE2S_256_SIZE).digest()

def mixKey(c, data):
    return KDF1(c, data)

# Precomputations
#
INITIAL_CHAIN_KEY = hash(NOISE_CONSTRUCTION)
INITIAL_HASH = mixhash(INITIAL_CHAIN_KEY, WG_IDENTIFIER)

def _generateDevices():
    import settings
    keySeed = settings.WG_PRIVATE_KEY_SEED
    if not keySeed:
        print('Required setting WG_PRIVATE_KEY_SEED not defined in a *.env file')
        log.error('Required setting WG_PRIVATE_KEY_SEED not defined in a *.env file')
        exit()
    keyN = 1000
    if settings.WG_PRIVATE_KEY_N:
        keyN = int(settings.WG_PRIVATE_KEY_N)

    private_key_string = nacl.utils.randombytes_deterministic(size=WG_KEY_LEN*keyN, seed=base64.b64decode(keySeed))
    devices = []
    for i in range(0, WG_KEY_LEN*keyN, WG_KEY_LEN):
        privateKey = nacl.public.PrivateKey(private_key_string[i:i+WG_KEY_LEN])
        mac1_key = hash(WG_LABEL_MAC1 + privateKey.public_key.encode())
        devices.append(Device(privateKey, mac1_key))
    return devices

DEVICES = _generateDevices()
class WireGuardProtocol(DatagramProtocol):

    def __init__(self, channel):
        self.channel = channel
        self.devices = DEVICES
        # Random test key
        import random
        device = random.choice(self.devices)
        print "Console public key: ", device.privateKey.public_key.encode(encoder=nacl.encoding.Base64Encoder)

    def datagramReceived(self, data, src):
        # Supports only the Initiation message of WireGuard protocol
        #
        # All other message types and non-conforming data are dropped
        #
        if len(data) != MSG_INITIATION_LEN or not data.startswith(MSG_INITIATION_PREFIX):
            return

        # MAC offsets at the end of message
        smac2 = len(data) - BLAKE2S_128_SIZE
        smac1 = smac2 - BLAKE2S_128_SIZE

        device = None
        for deviceCandidate in self.devices:
            mac1 = blake2s(data[:smac1], digest_size=BLAKE2S_128_SIZE, key=deviceCandidate.mac1_key).digest()
            if (mac1 == data[smac1:smac2]):
                device = deviceCandidate
                break

        if not device:
            print("Could not find matching public key for message")
            return

        mtype, sessionIndex, ephemeral, static, timestamp, mac1, mac2 = struct.unpack(MSG_INITIATION_FMT, data)

        hash = mixhash(INITIAL_HASH, device.privateKey.public_key.encode())
        hash = mixhash(hash, ephemeral)
        chainKey = mixKey(INITIAL_CHAIN_KEY, ephemeral)
        ss = sharedSecret(device.privateKey.encode(), ephemeral)
        chainKey, key = KDF2(chainKey, ss)
        peerPK = AEAD(key, ZERO_NONCE, static, hash)

        hash = mixhash(hash, static)
        chainKey, key = KDF2(chainKey, sharedSecret(device.privateKey.encode(), peerPK))
        tai64nTimestamp = AEAD(key, ZERO_NONCE, timestamp, hash)
        if not tai64nTimestamp:
            log.debug("Timestamp not valid; Handshake not provably sent by peer key")
            return

        unix_seconds, nano = struct.unpack("!QI", tai64nTimestamp)
        unix_seconds -= TAI64N_BASE
        time_diff = abs(int(time.time()) - unix_seconds)
        if  time_diff >  MSG_INITIATION_MAX_TIME_DIFF:
            log.debug("Handshake timestamp too new or too old")
            return

        public_key = base64.b64encode(peerPK)
        canarytoken = queries.wireguard_keymap_get(public_key)
        if not canarytoken:
            log.debug("No matching token for valid handshake with client key {} from {}. Expected when Canarytoken is deleted, but WG client config still in use.".format(public_key, src))
            return

        event = {
            'src_ip': src[0],
            'src_data': {
                'src_port' : src[1],
                'server_public_key': device.privateKey.public_key.encode(encoder=nacl.encoding.Base64Encoder),
                'client_public_key': public_key,
                'session_index': sessionIndex
            }
        }
        print(event)
        self.channel.dispatch(canarytoken=canarytoken, **event)

def generateCanarytokenPrivateKey(canarytoken):
    privateKey = nacl.public.PrivateKey.generate()
    public_key = privateKey.public_key.encode(encoder=nacl.encoding.Base64Encoder)
    device_key_idx = random.randrange(len(DEVICES))
    queries.wireguard_keymap_add(public_key, canarytoken)
    wg_key = '{}|{}'.format(device_key_idx, privateKey.encode(encoder=nacl.encoding.Base64Encoder))
    return wg_key

def deleteCanarytokenPrivateKey(wg_key):
    _, private_key = wg_key.split('|')
    privateKey = nacl.public.PrivateKey(private_key, encoder=nacl.encoding.Base64Encoder)
    public_key = privateKey.public_key.encode(encoder=nacl.encoding.Base64Encoder)
    queries.wireguard_keymap_del(public_key)

def clientConfig(wg_key):
    device_key_idx, private_key = wg_key.split('|')
    device_key_idx = int(device_key_idx)
    config = textwrap.dedent("""
    [Interface]
      PrivateKey = {privateKey}
      Address = {clientAddress}

    [Peer]
      PublicKey = {serverPublicKey}
      AllowedIPs = {serverAllowedIPs}
      Endpoint = {serverIP}:{serverPort}
      PersistentKeepalive = {keepAlive}
    """).strip()

    return config.format(
    privateKey = private_key,
    clientAddress = "192.168.123.107/32",
    serverPublicKey = DEVICES[device_key_idx].privateKey.public_key.encode(encoder=nacl.encoding.Base64Encoder),
    serverIP = settings.PUBLIC_IP,
    serverPort = DEFAULT_PORT,
    serverAllowedIPs = "192.168.1.0/24",
    keepAlive = 30 * (random.randrange(10) + 1) # Keep Alive *must* be non-zero to trigger token
    )
