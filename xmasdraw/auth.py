import yaml
import secrets
from .helpers import drawings_filepath
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from functools import wraps


def check_init_status(need_init_done=True):
    def _check_init_status(func):
        @wraps(func)
        def __check_init_status(*args, **kwargs):
            with open(drawings_filepath) as f:
                configs = yaml.safe_load(f)
            if need_init_done and configs.get("admin_password_hash") is None:
                return "Need init done"
            elif not need_init_done and configs.get("admin_password_hash") is not None:
                return "Too late, init already done"

            return func(*args, **kwargs)

        return __check_init_status

    return _check_init_status


def generate_passphrase():
    # See https://xkcd.com/936/
    with open("/usr/share/dict/words") as f:
        words = [word.strip() for word in f]
        passphrase = " ".join(secrets.choice(words) for i in range(4))

    ph = PasswordHasher()
    pass_hash = ph.hash(passphrase)

    with open(drawings_filepath) as f:
        configs = yaml.safe_load(f)

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
