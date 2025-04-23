import os

from utils.errors import throw


def get_required_env(name: str) -> str:
    return os.getenv(name) or throw(f'{name} is not set')

