# -*- coding: utf-8 -*-
"""Release manifest signatures (Ed25519, RFC 8032). Pure Python, no IO, Python 2.7/3 compatible.

The release manifest carries the package hashes, so authenticating its exact bytes with a key that
is never stored on GitHub authenticates the whole release. Verification is enforced as soon as
TRUSTED_KEYS contains at least one public key; the matching private key must stay offline.
"""
import base64
import binascii
import hashlib

# Hex-encoded 32-byte Ed25519 public keys accepted for releases. Several entries allow key rotation.
TRUSTED_KEYS = ()
SIGNATURE_ASSET = 'release.json.sig'
MAX_SIGNATURE = 256

_P = 2 ** 255 - 19
_Q = 2 ** 252 + 27742317777372353535851937790883648493


def _inv(value):
    return pow(value, _P - 2, _P)


_D = -121665 * _inv(121666) % _P
_I = pow(2, (_P - 1) // 4, _P)


def _recover_x(y, sign):
    if y >= _P:
        return None
    x2 = (y * y - 1) * _inv(_D * y * y + 1) % _P
    if x2 == 0:
        return None if sign else 0
    x = pow(x2, (_P + 3) // 8, _P)
    if (x * x - x2) % _P:
        x = x * _I % _P
    if (x * x - x2) % _P:
        return None
    return x if (x & 1) == sign else _P - x


_BY = 4 * _inv(5) % _P
_BX = _recover_x(_BY, 0)
_G = (_BX, _BY, 1, _BX * _BY % _P)
_ZERO = (0, 1, 1, 0)


def _add(a, b):
    first = (a[1] - a[0]) * (b[1] - b[0]) % _P
    second = (a[1] + a[0]) * (b[1] + b[0]) % _P
    third = 2 * a[3] * b[3] * _D % _P
    fourth = 2 * a[2] * b[2] % _P
    e, f, g, h = second - first, fourth - third, fourth + third, second + first
    return (e * f % _P, g * h % _P, f * g % _P, e * h % _P)


def _mul(scalar, point):
    result = _ZERO
    while scalar > 0:
        if scalar & 1:
            result = _add(result, point)
        point = _add(point, point)
        scalar >>= 1
    return result


def _equal(a, b):
    return (a[0] * b[2] - b[0] * a[2]) % _P == 0 and (a[1] * b[2] - b[1] * a[2]) % _P == 0


def _int(data):
    return sum(value << (8 * index) for index, value in enumerate(bytearray(data)))


def _bytes(value, length):
    return bytes(bytearray((value >> (8 * index)) & 255 for index in range(length)))


def _compress(point):
    zinv = _inv(point[2])
    x, y = point[0] * zinv % _P, point[1] * zinv % _P
    return _bytes(y | ((x & 1) << 255), 32)


def _decompress(data):
    value = _int(data)
    y, sign = value & ((1 << 255) - 1), value >> 255
    x = _recover_x(y, sign)
    return None if x is None else (x, y, 1, x * y % _P)


def _hash(data):
    return _int(hashlib.sha512(data).digest())


def _expand(seed):
    digest = hashlib.sha512(seed).digest()
    scalar = _int(digest[:32])
    scalar &= (1 << 254) - 8
    scalar |= 1 << 254
    return scalar, digest[32:]


def public_key(seed):
    """Public key for a 32-byte private seed (used by build tooling only)."""
    return _compress(_mul(_expand(seed)[0], _G))


def sign(seed, message):
    """Detached 64-byte signature (used by build tooling only)."""
    scalar, prefix = _expand(seed)
    public = _compress(_mul(scalar, _G))
    r = _hash(prefix + message) % _Q
    point = _compress(_mul(r, _G))
    k = _hash(point + public + message) % _Q
    return point + _bytes((r + k * scalar) % _Q, 32)


def verify(public, message, signature):
    """True only for a valid canonical signature; never raises for malformed input."""
    try:
        if len(public) != 32 or len(signature) != 64:
            return False
        key, point = _decompress(public), _decompress(signature[:32])
        scalar = _int(signature[32:])
        if key is None or point is None or scalar >= _Q:
            return False
        k = _hash(signature[:32] + public + message) % _Q
        return _equal(_mul(scalar, _G), _add(point, _mul(k, key)))
    except (TypeError, ValueError):
        return False


def enforced():
    return bool(TRUSTED_KEYS)


def verify_manifest(raw, encoded, keys=None):
    """Raise ValueError unless the base64 signature matches one trusted key for these exact bytes."""
    keys = TRUSTED_KEYS if keys is None else keys
    if not isinstance(raw, bytes):
        raise ValueError('Manifest bytes required')
    try:
        signature = base64.b64decode(bytes(encoded).strip())
    except (TypeError, ValueError, binascii.Error):
        raise ValueError('Invalid manifest signature encoding')
    for key in keys:
        if verify(binascii.unhexlify(key), raw, signature):
            return
    raise ValueError('Manifest signature rejected')
