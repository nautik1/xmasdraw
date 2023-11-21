import yaml
import secrets
from .helpers import drawings_filepath
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from os.path import exists


def is_admin_password_set():
    if not exists(drawings_filepath):
        return False

    with open(drawings_filepath) as f:
        configs = yaml.safe_load(f)
    if configs.get("admin_password_hash") is None:
        return False

    return True


def generate_passphrase():
    # See https://xkcd.com/936/
    with open("/usr/share/dict/words") as f:
        words = [word.strip() for word in f]
        passphrase = " ".join(secrets.choice(words) for i in range(4))

    ph = PasswordHasher()
    pass_hash = ph.hash(passphrase)

    with open(drawings_filepath) as f:
        configs = yaml.safe_load(f) or {}

    configs["admin_password_hash"] = pass_hash

    with open(drawings_filepath, "w") as f:
        yaml.dump(configs, f)

    return passphrase


def verify_passphrase(passphrase):
    with open(drawings_filepath) as f:
        configs = yaml.safe_load(f)
    ph = PasswordHasher()
    try:
        return ph.verify(configs.get("admin_password_hash"), passphrase)
    except VerifyMismatchError:
        return False
