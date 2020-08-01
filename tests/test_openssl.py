import os.path
import subprocess


from picoca.main import main


def _openssl_x509(cert_path, *args):
    proc = subprocess.Popen(
        ["openssl", "x509", "-in", cert_path, "-noout"] + [arg for arg in args],
        stdout=subprocess.PIPE,
        stderr=None,
    )

    stdout = proc.communicate()[0].decode("utf-8")

    assert proc.returncode == 0

    return stdout


def test_end_to_end_openssl_verify(tmp_path):
    # execute as if calling: helpful --cert-path <path> foo.com bar.baz
    main(["--cert-path", str(tmp_path), "foo.com", "bar.baz", "127.0.0.1"])
    root_path = os.path.join(str(tmp_path), "__root__.pem")
    cert_path = os.path.join(str(tmp_path), "foo.com.pem")

    # now we're gonna call openssl to make sure that everything is okay with root
    subject = _openssl_x509(root_path, "-subject").strip().split("=", 1)[1]
    assert subject == "CN = PicoCA Root Certificate Authority, OU = PicoCA, O = PicoCA"

    issuer = _openssl_x509(root_path, "-issuer").strip().split("=", 1)[1]
    assert issuer == "CN = PicoCA Root Certificate Authority, OU = PicoCA, O = PicoCA"

    assert issuer == subject

    # now verify that the certs are signed correctly
    assert subprocess.call(["openssl", "verify", "-x509_strict", "-purpose", "sslclient",
                            "-CAfile", root_path, cert_path]) == 0

    # verify that the generated certificate will be expired in two years, not 30 days
    assert subprocess.call(["openssl", "x509", "-in", cert_path, "-checkend", "2592000"]) == 0
    assert subprocess.call(["openssl", "x509", "-in", cert_path, "-checkend", "63113904"]) == 1

    # verify that all the hostnames are properly in there
    stdout = _openssl_x509(cert_path, "-checkhost", "foo.com", "-checkhost", "bar.baz", "-checkip", "127.0.0.1")
    assert "NOT match" not in stdout

    # and nothing else is
    stdout = _openssl_x509(cert_path, "-checkhost", "pokeinthe.io")
    assert "NOT match" in stdout

    stdout = _openssl_x509(cert_path, "-checkip", "1.2.3.4")
    assert "NOT match" in stdout
