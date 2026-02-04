"""Core module initialization."""
from .config import settings, get_settings
from .logging import setup_logging, get_logger, recognition_logger
from .security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    create_token_pair,
    decode_token,
    get_current_user_data,
    require_roles,
    require_admin,
    TokenPair,
    TokenData,
)

__all__ = [
    "settings",
    "get_settings",
    "setup_logging",
    "get_logger",
    "recognition_logger",
    "hash_password",
    "verify_password",
    "create_access_token",
    "create_refresh_token",
    "create_token_pair",
    "decode_token",
    "get_current_user_data",
    "require_roles",
    "require_admin",
    "TokenPair",
    "TokenData",
]
