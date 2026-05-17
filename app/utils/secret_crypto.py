"""
敏感配置加密工具（AES-128-GCM）

用于对 config.yaml 中存储的第三方服务密码进行可逆加密，
防止配置文件泄露时明文密码一并暴露。

密钥来源（优先级从高到低）：
  1. 环境变量 APP_SECRET_KEY（推荐生产环境使用）
  2. 自动生成并持久化到 config/.secret_key（开发/Docker 单机场景）

加密格式（Base64-URL 编码）：
  enc:<base64url(nonce_12bytes + ciphertext + tag_16bytes)>

若值不以 "enc:" 开头，视为未加密的明文，直接返回原值（向后兼容）。

用法：
    from app.utils.secret_crypto import encrypt_secret, decrypt_secret

    # 存储时加密
    encrypted = encrypt_secret("mypassword")   # "enc:xxxx..."
    config.set("ikuai.password", encrypted)

    # 读取时解密
    plain = decrypt_secret(config.get("ikuai.password"))  # "mypassword"
"""

import base64
import os
import secrets
from pathlib import Path

from app.utils.logger import get_logger

logger = get_logger(__name__)

_ENC_PREFIX = "enc:"
_KEY_FILE = Path(os.environ.get("CONFIG_DIR", "config")) / ".secret_key"

# 缓存派生的 16 字节 AES 密钥
_cached_key: bytes | None = None


def _derive_key() -> bytes:
    """
    获取或生成 AES-128 密钥（16 字节）。

    优先使用环境变量 APP_SECRET_KEY（Base64 或原始字节）；
    否则自动生成并持久化到 config/.secret_key 文件。
    """
    global _cached_key
    if _cached_key is not None:
        return _cached_key

    # 1. 从环境变量读取
    env_key = os.environ.get("APP_SECRET_KEY", "")
    if env_key:
        try:
            raw = base64.urlsafe_b64decode(env_key + "==")  # 容错 padding
            if len(raw) >= 16:
                _cached_key = raw[:16]
                return _cached_key
        except Exception:
            pass
        # 若不是 base64，直接用 UTF-8 字节（取前 16 字节，不足则补零）
        raw_bytes = env_key.encode()[:16].ljust(16, b"\x00")
        _cached_key = raw_bytes
        return _cached_key

    # 2. 从持久化文件读取
    if _KEY_FILE.exists():
        try:
            raw = base64.urlsafe_b64decode(_KEY_FILE.read_text().strip() + "==")
            if len(raw) == 16:
                _cached_key = raw
                return _cached_key
        except Exception as exc:
            logger.warning(f"读取 .secret_key 失败，将重新生成：{exc}")

    # 3. 生成新密钥并持久化
    new_key = secrets.token_bytes(16)
    try:
        _KEY_FILE.parent.mkdir(parents=True, exist_ok=True)
        _KEY_FILE.write_text(base64.urlsafe_b64encode(new_key).decode())
        try:
            import stat
            _KEY_FILE.chmod(stat.S_IRUSR | stat.S_IWUSR)
        except (OSError, NotImplementedError):
            pass  # Windows 上忽略
        logger.info(f"已自动生成应用密钥并保存至：{_KEY_FILE}")
    except Exception as exc:
        logger.warning(f"保存 .secret_key 失败：{exc}")

    _cached_key = new_key
    return _cached_key


def encrypt_secret(plaintext: str) -> str:
    """
    对明文字符串进行 AES-128-GCM 加密，返回 "enc:<base64url>" 格式。

    若输入已是加密格式（以 "enc:" 开头），直接返回原值（幂等）。
    若输入为空字符串，直接返回空字符串。

    安全策略：新写入必须成功完成加密；若加密能力不可用或加密失败，直接拒绝写入。
    """
    if not plaintext:
        return plaintext
    if plaintext.startswith(_ENC_PREFIX):
        return plaintext  # 已加密，幂等

    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    except ImportError as exc:
        raise RuntimeError(
            "缺少 cryptography 依赖，无法安全加密敏感配置；已拒绝写入，请先安装 cryptography 并配置 APP_SECRET_KEY"
        ) from exc

    try:
        key = _derive_key()
        nonce = secrets.token_bytes(12)  # 96-bit nonce（GCM 推荐）
        aesgcm = AESGCM(key)
        ciphertext = aesgcm.encrypt(nonce, plaintext.encode(), None)
        encoded = base64.urlsafe_b64encode(nonce + ciphertext).decode()
        return f"{_ENC_PREFIX}{encoded}"
    except Exception as exc:
        raise RuntimeError(f"敏感配置加密失败，已拒绝写入：{exc}") from exc


def decrypt_secret(value: str) -> str:
    """
    解密 "enc:<base64url>" 格式的密文，返回明文。

    若输入不以 "enc:" 开头（明文或空值），直接返回原值（向后兼容）。
    """
    if not value or not value.startswith(_ENC_PREFIX):
        return value  # 未加密，直接返回

    encoded = value[len(_ENC_PREFIX):]

    # 优先尝试 AES-GCM 解密
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM

        raw = base64.urlsafe_b64decode(encoded + "==")
        nonce = raw[:12]
        ciphertext = raw[12:]
        key = _derive_key()
        aesgcm = AESGCM(key)
        return aesgcm.decrypt(nonce, ciphertext, None).decode()

    except ImportError:
        return _xor_decrypt(encoded)
    except Exception as exc:
        logger.warning(f"解密敏感配置失败，尝试 XOR 降级解密：{exc}")
        try:
            return _xor_decrypt(encoded)
        except Exception:
            logger.error("解密失败，返回原始加密值（可能密钥已更换）")
            return value


# ==================== 兼容旧版 XOR 数据解密（仅保留读取兼容，不再用于新写入） ====================

def _xor_encrypt(plaintext: str) -> str:
    """基于密钥的 XOR 混淆（非真加密，仅防配置文件直接泄露）。"""
    key = _derive_key()
    data = plaintext.encode()
    xored = bytes(b ^ key[i % len(key)] for i, b in enumerate(data))
    return f"enc:{base64.urlsafe_b64encode(xored).decode()}"


def _xor_decrypt(encoded: str) -> str:
    """XOR 混淆解码。"""
    key = _derive_key()
    data = base64.urlsafe_b64decode(encoded + "==")
    plain = bytes(b ^ key[i % len(key)] for i, b in enumerate(data))
    return plain.decode()
