from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec


DEFAULT_CURVE = ec.SECP256R1


def generate_private_key(curve=None):
    if curve is None:
        curve = DEFAULT_CURVE

    return ec.generate_private_key(curve, backend=default_backend())


def to_pem(thing):
    if hasattr(thing, 'private_bytes'):
        encoded = thing.private_bytes(
            encoding=serialization.Encoding.PEM,
            encryption_algorithm=serialization.NoEncryption(),
            format=serialization.PrivateFormat.TraditionalOpenSSL,
        )
    else:
        encoded = thing.public_bytes(
            encoding=serialization.Encoding.PEM,
        )

    return encoded.decode('ascii')
