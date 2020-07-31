NanoCA is a simple CA intended for use in situations where the CA operator
also operates each host where a certificate will be used. It automatically
generates both a key and a certificate when asked to produce a certificate.
It does not offer OCSP or CRL services. NanoCA is appropriate, for instance,
for generating certificates for RPC systems or microservices.

On first run, NanoCA will generate a keypair and a root certificate in the
`certificates` subdirectory, and will reuse that same keypair and root
certificate unless they are deleted.

On each further run, NanoCA will generate a keypair and sign an end-entity (leaf)
certificate for that keypair. The certificate will contain a list of DNS names
and/or IP addresses from the command line flags. The key and certificate are
placed in the same directory as the root key and certificate, with a file name
chosen based upon the first domain name or IP address specified on the command
line. It will overwrite existing keys and certificates, e.g. for renewals.

The certificate will have a validity of 366 days, although this can be changed
by using the `--lifespan` flag. You can also change the directory where the
root and end-entity certificates are stored by using the `--cert-path` flag.

The code is designed to be simple and easy-to-read, for educational purposes.
If you stumble across a decision that doesn't make sense, please open an
[issue](https://github.com/april/nanoca/issues) so that it may be addressed.

NanoCA should work with Python 2.7, despite the incredible soul-rendering pain
this has caused me.

# Installation

```bash
$ python setup.py install

$ nanoca --help
usage: nanoca [-h] [--cert-path path] [--lifespan days] hostname [hostname ...]

positional arguments:
  hostname          domains and IP addresses to add to certificate

optional arguments:
  -h, --help        show this help message and exit
  --cert-path path  Directory to store keys and certificates (default: "./certificates")
  --lifespan days   Number of days for certificate to be valid (default: 366)
```

# Usage

```
# Initialize the certificate authority and sign a certificate for "foo.com":
$ nanoca foo.com
Successfully initialized NanoCA to: certificates/__root__.key and certificates/__root__.pem
Successfully wrote files to: certificates/foo.com.pem and certificates/foo.com.key

# Generate another certificate using the same certificate authority generated above
$ nanoca bar.org baz.net 127.0.0.1 2001:0db8:85a3:0000:0000:8a2e:0370:7334 qux.io
Successfully wrote files to: certificates/bar.org.pem and certificates/bar.org.key

# Verify that a proper certificate was generated
$ openssl verify -x509_strict -purpose sslclient -purpose sslserver -CAfile certificates/__root__.pem certificates/bar.org.pem
certificates/bar.org.pem: OK

# Look at the final generated certificate
$ openssl x509 -in certificates/bar.org.pem -noout -text
Certificate:
    Data:
        Version: 3 (0x2)
        Serial Number:
            4d:c5:c9:d7:ca:7e:48:40:85:36:d3:1d:79:69:70:2e
        Signature Algorithm: ecdsa-with-SHA256
        Issuer: CN = NanoCA Root Certificate Authority, OU = NanoCA, O = NanoCA
        Validity
            Not Before: Jul 30 11:36:31 2020 GMT
            Not After : Aug  1 11:36:31 2021 GMT
        Subject: CN = bar.org
        Subject Public Key Info:
            Public Key Algorithm: id-ecPublicKey
                Public-Key: (256 bit)
                pub:
                    04:cd:36:8b:e2:10:50:4d:a5:90:d1:e5:9f:43:56:
                    c2:55:b0:df:55:a5:e1:61:a8:9a:fd:4a:be:f5:9c:
                    75:dc:b6:8b:98:d0:ed:70:41:ed:1b:9b:8d:cf:85:
                    6c:e0:fd:78:a9:06:a0:d8:70:00:0b:18:7b:2e:2c:
                    f4:aa:5d:2d:8b
                ASN1 OID: prime256v1
                NIST CURVE: P-256
        X509v3 extensions:
            X509v3 Subject Key Identifier:
                2D:B2:48:97:2E:D7:81:5B:D9:A1:91:C5:79:58:A3:03:2C:68:CF:E2
            X509v3 Basic Constraints: critical
                CA:FALSE
            X509v3 Subject Alternative Name:
                DNS:bar.org, DNS:baz.net, DNS:qux.io, IP Address:127.0.0.1, IP Address:2001:DB8:85A3:0:0:8A2E:370:7334
            X509v3 Key Usage: critical
                Digital Signature, Key Encipherment
            X509v3 Extended Key Usage:
                TLS Web Server Authentication, TLS Web Client Authentication
            X509v3 Authority Key Identifier:
                keyid:48:02:99:16:C6:6E:5B:BA:89:AD:AB:24:14:51:F9:7E:1C:88:8D:5A

    Signature Algorithm: ecdsa-with-SHA256
         30:64:02:30:30:5a:7b:b8:5c:d5:19:62:90:a6:16:86:c4:5a:
         4a:fd:9c:7a:1f:97:56:ea:21:17:50:6c:47:ab:fa:9d:71:38:
         ae:b0:fe:f1:8a:ca:75:40:37:02:86:49:0d:f3:c9:d5:02:30:
         58:e7:97:e6:c3:95:15:c6:11:94:a2:a2:e2:78:f7:e7:b8:d0:
         74:b5:64:47:1b:91:33:a4:99:c6:bc:fe:1b:b3:47:03:af:b4:
         95:6e:aa:05:44:b3:d5:84:92:f4:45:46

# And the generated certificate authority, verifying the aKI field matches
$ openssl x509 -in certificates/__root__.pem -noout -text
Certificate:
    Data:
        Version: 3 (0x2)
        Serial Number:
            f4:c4:4d:84:5f:b8:42:03:b6:cf:56:ad:ac:09:14:dd
        Signature Algorithm: ecdsa-with-SHA384
        Issuer: CN = NanoCA Root Certificate Authority, OU = NanoCA, O = NanoCA
        Validity
            Not Before: Jul 30 11:36:31 2020 GMT
            Not After : Jul 30 11:36:31 2040 GMT
        Subject: CN = NanoCA Root Certificate Authority, OU = NanoCA, O = NanoCA
        Subject Public Key Info:
            Public Key Algorithm: id-ecPublicKey
                Public-Key: (384 bit)
                pub:
                    04:39:e6:3d:66:cd:15:ad:c7:65:38:02:20:71:f8:
                    8f:11:fa:f2:d6:25:80:05:f4:37:a2:35:84:72:fc:
                    27:45:f5:f2:3d:5f:8f:23:cc:e3:b0:7c:e9:3a:3f:
                    f9:a1:b4:b2:22:ba:0f:54:30:b7:52:15:a0:dc:48:
                    3c:ff:1c:ab:de:2e:4f:98:3e:a9:1e:f7:9c:d8:fc:
                    2b:cb:00:1f:53:40:bb:5a:9f:3c:05:1f:03:1c:47:
                    ee:68:df:c1:a4:87:11
                ASN1 OID: secp384r1
                NIST CURVE: P-384
        X509v3 extensions:
            X509v3 Subject Key Identifier:
                48:02:99:16:C6:6E:5B:BA:89:AD:AB:24:14:51:F9:7E:1C:88:8D:5A
            X509v3 Basic Constraints: critical
                CA:TRUE, pathlen:0
            X509v3 Key Usage: critical
                Digital Signature, Certificate Sign
    Signature Algorithm: ecdsa-with-SHA384
         30:64:02:30:5b:fc:75:2b:03:82:30:0b:3e:f8:ec:e5:ee:07:
         e8:c1:81:9b:a6:ff:50:49:fb:44:d5:a7:57:0b:55:22:0c:8d:
         81:cb:fe:22:af:03:cc:eb:a6:0c:ec:67:1d:58:9f:8e:02:30:
         46:fc:e8:1b:1c:dd:00:54:24:03:f5:c4:93:9c:26:8e:a7:ea:
         74:ee:7b:17:29:a5:4c:37:91:89:57:1c:10:5a:5f:c1:19:55:
         bd:43:23:f7:9f:33:35:51:82:fb:7c:ad

# Verify that TLS works
$ openssl s_server -quiet -www -port 443 -cert certificates/bar.org.pem -key certificates/bar.org.key

$ curl --cacert certificates/__root__.pem --output /dev/null "https://127.0.0.1/"
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100  5070    0  5070    0     0  1650k      0 --:--:-- --:--:-- --:--:-- 1650k
```

# Credits

NanoCA was directly inspired by [Jacob Hoffman-Andrew](https://github.com/jsha)'s
[minica](https://github.com/jsha/minica), and builds on top of the towering amount
of work done in [pyca/cryptography](https://cryptography.io) by
[Alex Gaynor](https://github.com/alex), [Paul Kehrer](https://github.com/reaperhulk) and
a ton of other heroic [volunteers](https://github.com/pyca/cryptography/blob/master/AUTHORS.rst).