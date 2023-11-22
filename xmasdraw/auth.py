import secrets
from os.path import exists

import yaml
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from .helpers import drawings_filepath


def is_admin_password_set():
    if not exists(drawings_filepath):
        return False

    with open(drawings_filepath) as f:
        configs = yaml.safe_load(f)
    if configs is None or configs.get("admin_password_hash") is None:
        return False

    return True


def generate_passphrase(language=None):
    words_list_filepaths = {
        "fr": "/usr/share/dict/french",
        "en": "/usr/share/dict/american-english",
    }

    words_list_path = (
        words_list_filepaths[language] if language else words_list_filepaths["en"]
    )

    # See https://xkcd.com/936/
    with open(words_list_path) as f:
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
