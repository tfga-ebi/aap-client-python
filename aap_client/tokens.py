import jwt
from jwt import MissingRequiredClaimError

from aap_client.crypto_files import (
    load_public_from_x509,
    load_private_from_pem
)


_DEFAULT_CLAIMS = {u'iat', u'exp', u'sub', u'email', u'name', u'nickname'}


class TokenDecoder(object):  # pylint: disable=too-few-public-methods
    def __init__(self, filename, required_claims=None):
        if required_claims is None:
            required_claims = []

        self._required_claims = required_claims
        self._key = load_public_from_x509(filename)

    def decode(self, serialized_token, audience=None):
        return decode_token(serialized_token, self._key,
                            required_claims=self._required_claims,
                            audience=audience)


class TokenEncoder(object):  # pylint: disable=too-few-public-methods
    def __init__(self, key_filename, secret=None):
        '''
        Args:
            key_filename: relative path to the file that contains the
                secret key.
            secret: string that decodes the secret key.
        '''
        self._private_key = load_private_from_pem(key_filename, secret)

    def encode(self, claims):
        '''
        Args:
            claims: dictionary that stores the claims
        '''
        return encode_token(claims, self._private_key)


# Functions that can be used when an object to store the keys cannot be

def decode_token(serialized_token, public_key,
                 required_claims=None, audience=None):
    if required_claims is None:
        required_claims = []

    required_claims = set(required_claims).union(_DEFAULT_CLAIMS)
    payload = jwt.decode(serialized_token, public_key,
                         audience=audience,
                         algorithms=[u'RS256'])
    for claim in required_claims:
        if payload.get(claim) is None:
            raise MissingRequiredClaimError(claim)

    return payload


def encode_token(claims, private_key):
    return jwt.encode(claims, private_key, algorithm=u'RS256')
