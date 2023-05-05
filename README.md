# pytest-smtpd

⚠ **Not intended for use with production systems.** ⚠

This fixture is intended to address cases where to test an application that sends an email, it needs to be intercepted for subsequent processing. For example, sending an email with a code for password reset or two-factor authentication. This fixture allows a test to trigger the email being sent, ensure that it's sent, and read the email.

## Installing

To install using pip, first upgrade pip to the latest version to avoid any issues installing `cryptography`:

```bash
$ python -m pip install --upgrade pip
$ pip install pytest-smtpd
```

Or, if you're using setuptools, it can be included in the `extras_require` argument of a `setup.py` file:

```python
setup(
    ...
    extras_require={
        "test": [
            "pytest",
            "pytest-smtpd",
        ],
    },
)
```

and then installed with pip (-e assumes that you want your project to be editable):

```bash
$ python -m pip install --upgrade pip
$ pip install -e .[test]
```

## Using

The `SMTPDFix` plugin, `smtpd`, automatically registers for use with pytest when you install smtpdfix. To use it simply add to your test method.

```python
from smtplib import SMTP


def test_sendmail(smtpd):
    from_addr = "from.addr@example.org"
    to_addrs = "to.addr@example.org"
    msg = (f"From: {from_addr}\r\n"
           f"To: {to_addrs}\r\n"
           f"Subject: Foo\r\n\r\n"
           f"Foo bar")

    with SMTP(smtpd.hostname, smtpd.port) as client:
        client.sendmail(from_addr, to_addrs, msg)

    assert len(smtpd.messages) == 1
```

To use STARTTLS:

```python
from smtplib import SMTP


def test_sendmail(smtpd):
    smptd.config.use_starttls = True
    from_ = "from.addr@example.org"
    to_ = "to.addr@example.org"
    msg = (f"From: {from_}\r\n"
           f"To: {to_}\r\n"
           f"Subject: Foo\r\n\r\n"
           f"Foo bar")

    with SMTP(smtpd.hostname, smtpd.port) as client:
        client.starttls()  # Note that you need to call starttls first.
        client.sendmail(from_addr, to_addrs, msg)

    assert len(smtpd.messages) == 1
```

To use TLS encryption on the connections:

```python
from smtplib import STMP_SSL  # Note the different client class.


def test_custom_certificate(smtpd):
    smtpd.config.use_ssl = True

    from_ = "from.addr@example.org"
    to_ = "to.addr@example.org"
    msg = (f"From: {from_}\r\n"
           f"To: {to_}\r\n"
           f"Subject: Foo\r\n\r\n"
           f"Foo bar")

    with SMTP_SSL(smtpd.hostname, smtpd.port) as client:
        client.sendmail(from_addr, to_addrs, msg)

    assert len(smtpd.messages) == 1
```

The certificates included with the fixture will work for addresses localhost, localhost.localdomain, 127.0.0.1, 0.0.0.1, ::1. If using other addresses the key (key.pem) and certificate (cert.pem) must be in a location specified under `SMTP_SSL_CERTS_PATH`.

### Configuration

Configuration is handled through properties in the `config` of the fixture and are initially set from environment variables:

Property         | Variable               | Default              | Description
-----------------|------------------------|----------------------|------------
`host`           | `SMTPD_HOST`           | `127.0.0.1` or `::1` | The hostname that the fixture will listen on.
`port`           | `SMTPD_PORT`           | `a random free port` | The port that the fixture will listen on.
`ready_timeout`  | `SMTPD_READY_TIMEOUT`  | `10.0`               | The seconds the server will wait to start before raising a `TimeoutError`.
`login_username` | `SMTPD_LOGIN_NAME`     | `user`               | Username for default authentication.
`login_password` | `SMTPD_LOGIN_PASSWORD` | `password`           | Password for default authentication.
`use_ssl`        | `SMTPD_USE_SSL`        | `False`              | Whether the fixture should use fixed TLS/SSL for transactions. If using smtplib requires that `SMTP_SSL` be used instead of `SMTP`.
`use_starttls`   | `SMTPD_USE_STARTTLS`   | `False`              | Whether the fixture should use StartTLS to encrypt the connections. If using `smtplib` requires that `SMTP.starttls()` is called before other commands are issued. Overrides `use_tls` as the preferred method for securing communications with the client.
`enforce_auth`   | `SMTPD_ENFORCE_AUTH`   | `False`              | If set to true then the fixture refuses MAIL, RCPT, DATA commands until authentication is completed.
`ssl_cert_path`  | `SMTPD_SSL_CERTS_PATH` | `./certs/`           | The path to the key and certificate in PEM format for encryption with SSL/TLS or StartTLS.
`ssl_cert_files` | `SMTPD_SSL_CERT_FILE` and `SMTPD_SSL_KEY_FILE` | `("cert.pem", None)` | A tuple of the path for the certificate file and key file in PEM format.



## Alternatives

Many libraries for sending email have built-in methods for testing and using these methods should generally be prefered over pytest-smtpd. Some known solutions:

+ **fastapi-mail**: has a `record_messsages()` method to intercept the mail. Instructions on how to suppress the sending of mail and implement it can be seen at [https://sabuhish.github.io/fastapi-mail/example/#unittests-using-fastapimail](https://sabuhish.github.io/fastapi-mail/example/#unittests-using-fastapimail)
+ **flask-mail**: has a method to suppress sending and capture the email for testing purposes. [Instructions](https://pythonhosted.org/Flask-Mail/#unit-tests-and-suppressing-emails)

## Developing

To develop and test smtpdfix you will need to install [pytest-asyncio](https://github.com/pytest-dev/pytest-asyncio) to run asynchronous tests, [isort](https://pycqa.github.io/isort/) to sort imports and [flake8](https://flake8.pycqa.org/en/latest/) to lint. To install in a virtual environment for development:

```bash
$ python -m venv venv
$ ./venv/scripts/activate
$ pip install -e .[dev]
```

Code is tested using tox:

```bash
$ tox
```

Quick tests can be handled by running pytest directly:

```bash
$ pytest
```

We include a [pre-commit](https://pre-commit.com/) configuration file to automate checks and clean up imports before pushing code. In order to install pre-commit git hooks:

```bash
$ pip install pre-commit
$ pre-commit install
```

## Known Issues

+ Firewalls may interfere with the operation of the smtp server.
+ Authenticating with LOGIN and PLAIN mechanisms fails over TLS/SSL, but works with STARTTLS. [Issue #10](https://github.com/bebleo/smtpdfix/issues/10)
+ Currently no support for termination through signals. [Issue #4](https://github.com/bebleo/smtpdfix/issues/4)
+ If the fixture start exceeds the `ready_timeout` and aborts the host and port are not consistently released and subsequent uses may result in an error. [Issue #80](https://github.com/bebleo/smtpdfix/issues/80)

Written with ☕ and ❤ in Montreal, QC


