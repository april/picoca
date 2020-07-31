import argparse
import os.path
import sys

from nanoca.ca import CertificateAuthority
from nanoca.crypto import generate_private_key, to_pem

# Python 2.x support makes me so very sad
if sys.version_info[0] >= 3:
    unicode = str
_utf8 = unicode


def __write_pem_to_disk(path, cert):
    with open(path, "w") as __f:
        __f.write(to_pem(cert))


def main(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--cert-path", type=_utf8, nargs=1, default="certificates", metavar="path",
                        help="Directory to store keys and certificates (default: \"./%(default)s\")")
    parser.add_argument("--lifespan", type=int, nargs=1, default=366, metavar="days",
                        help="Number of days for certificate to be valid (default: %(default)d)")
    parser.add_argument("hostnames", type=_utf8, nargs="+", default=[], metavar="hostname",
                        help="domains and IP addresses to add to certificate")

    args = parser.parse_args(args) if args else parser.parse_args(sys.argv[1:])

    args.cert_path = args.cert_path[0] if type(args.cert_path) is list else args.cert_path
    args.lifespan = args.lifespan[0] if type(args.lifespan) is list else args.lifespan

    if not os.path.exists(args.cert_path):
        try:
            os.mkdir(args.cert_path)
        except:
            print("Unable to create or load certificate path: {0}. "
                  "Maybe it's missing a parent directory?".format(args.cert_path))
            sys.exit(1)

    # load the certificate authority
    ca_cert_path = os.path.join(args.cert_path, "__root__.pem")
    ca_key_path = os.path.join(args.cert_path, "__root__.key")

    CA = CertificateAuthority(
        cert_path=os.path.join(args.cert_path, "__root__.pem"),
        key_path=os.path.join(args.cert_path, "__root__.key"),
    )

    # if the certificate files don't exist, attempt to write them to disk
    try:
        if not os.path.exists(ca_cert_path) or not os.path.exists(ca_key_path):
            __write_pem_to_disk(ca_cert_path, CA.certificate)
            __write_pem_to_disk(ca_key_path, CA.private_key)

            print("Successfully initialized NanoCA to: {0} and {1}".format(ca_cert_path, ca_key_path))
    except:
        print("Error: Unable to write {0} and {1} to disk.".format(ca_cert_path, ca_key_path))
        sys.exit(1)

    # create a private key
    private_key = generate_private_key()

    # construct a certificate and then sign it
    certificate = CA.construct(private_key, lifespan=args.lifespan, hostnames=args.hostnames)
    certificate = CA.sign(certificate)

    # write files to disk
    cert_path = os.path.join(args.cert_path, args.hostnames[0] + ".pem")
    key_path = os.path.join(args.cert_path, args.hostnames[0] + ".key")
    try:
        __write_pem_to_disk(cert_path, certificate)
        __write_pem_to_disk(key_path, private_key)
    except:
        print("Error: Unable to write {0} and {1} to disk.".format(cert_path, key_path))
        sys.exit(1)
    print("Successfully wrote files to: {0} and {1}".format(cert_path, key_path))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
