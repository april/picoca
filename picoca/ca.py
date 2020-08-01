import datetime
import sys
import uuid

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID
from ipaddress import ip_address

import os.path

from .crypto import generate_private_key

CA_LIFESPAN = 7304  # 20 years


class CertificateAuthority:
    def __init__(self, cert_path, key_path):
        # load the root key and certificate from disk
        if os.path.exists(cert_path) and os.path.exists(key_path):
            try:
                with open(cert_path, "rb") as __f:
                    self.certificate = x509.load_pem_x509_certificate(__f.read(), backend=default_backend())
                with open(key_path, "rb") as __f:
                    self.private_key = serialization.load_pem_private_key(
                        __f.read(), password=None, backend=default_backend())
            except:
                print("Invalid private key or certificate for certificate authority")
                sys.exit(1)

            if not self.private_key.public_key().public_numbers() == self.certificate.public_key().public_numbers():
                print("Public key in {0} doesn't match private key in {1}".format(cert_path, key_path))
                sys.exit(1)

        # if not, create a private key and a signing cert
        else:
            from cryptography.hazmat.primitives.asymmetric.ec import SECP384R1

            self.private_key = generate_private_key(SECP384R1)

            certificate = self.construct(
                private_key=self.private_key,
                lifespan=CA_LIFESPAN,
                ca=True,
                cn=u"PicoCA Root Certificate Authority",
                o=u"PicoCA",
                ou=u"PicoCA",
            )

            self.certificate = self.sign(certificate, certificate._subject_name)

    def __subject_alt_name(self, hostname):
        try:
            return x509.IPAddress(ip_address(hostname))
        except ValueError:
            return x509.DNSName(hostname)

    def construct(self, private_key=None, lifespan=366, ca=False, hostnames=None, cn=None, ou=None, o=None):
        # derive the public key from the private key
        public_key = private_key.public_key()

        # construct x509 certificate
        builder = x509.CertificateBuilder()

        # construct the subject name
        if cn:
            subject_name = [x509.NameAttribute(NameOID.COMMON_NAME, cn)]
        else:
            subject_name = [x509.NameAttribute(NameOID.COMMON_NAME, hostnames[0])]

        if ou is not None:
            subject_name.append(x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, ou))
        if o is not None:
            subject_name.append(x509.NameAttribute(NameOID.ORGANIZATION_NAME, o))

        builder = builder.subject_name(x509.Name(subject_name))

        # not valid more than one day before today
        builder = builder.not_valid_before(datetime.datetime.now() - datetime.timedelta(1, 0, 0))
        builder = builder.not_valid_after(datetime.datetime.now() + datetime.timedelta(lifespan, 0, 0))

        # randomly generated 128-bit serial number
        builder = builder.serial_number(int(uuid.uuid4()))

        builder = builder.public_key(public_key)

        # add the subject key identifier (SKID)
        builder = builder.add_extension(x509.SubjectKeyIdentifier.from_public_key(public_key), critical=False)

        if ca:
            builder = builder.add_extension(x509.BasicConstraints(ca=True, path_length=0), critical=True)

            builder = builder.add_extension(x509.KeyUsage(
                digital_signature=True,
                content_commitment=False,
                key_encipherment=False,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=True,
                crl_sign=False,
                encipher_only=False,
                decipher_only=False), critical=True)
        else:
            builder = builder.add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)

            # for aesthetic reasons, let's do a mild sorting of hostnames and IP addresses in the sAN field
            sorted_hostnames = sorted(hostnames, key=lambda x: (x[0].isdigit() or ":" in x, x))
            builder = builder.add_extension(
                x509.SubjectAlternativeName([self.__subject_alt_name(hostname) for hostname in sorted_hostnames]),
                critical=False
            )

            builder = builder.add_extension(x509.KeyUsage(
                digital_signature=True,
                content_commitment=False,
                key_encipherment=True,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=False,
                crl_sign=False,
                encipher_only=False,
                decipher_only=False), critical=True)

            builder = builder.add_extension(x509.ExtendedKeyUsage([
                ExtendedKeyUsageOID.SERVER_AUTH,
                ExtendedKeyUsageOID.CLIENT_AUTH,
            ]), critical=False)

            builder = builder.add_extension(
                x509.AuthorityKeyIdentifier.from_issuer_public_key(self.certificate.public_key()),
                critical=False)

        return builder

    def sign(self, request, issuer=None):
        """
        :param request: x509.CertificateBuilder
        :param issuer: issuer subject
        :return: x509.Certificate
        """
        if issuer is None:
            request = request.issuer_name(self.certificate.subject)
        else:
            request = request.issuer_name(issuer)

        # maybe this will support other key types and sizes in the future?
        if request._public_key.key_size == 384:
            hash = hashes.SHA384()
        else:
            hash = hashes.SHA256()

        return request.sign(
            private_key=self.private_key,
            algorithm=hash,
            backend=default_backend(),
        )
