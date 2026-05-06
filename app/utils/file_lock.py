"""
文件读写锁（跨平台：Windows msvcrt / POSIX fcntl）
防止多进程/多线程并发写同一文件导致 YAML 损坏
"""
import os
import sys
from contextlib import contextmanager

# 静态分析器在非 Windows 平台会跳过 Windows 分支，反之亦然，这是预期行为
# pylint: disable=possibly-used-before-assignment


@contextmanager
def file_lock(lock_path: str):
    """
    文件锁上下文管理器

    用法：
        with file_lock("config/config.yaml.lock"):
            with open("config/config.yaml", "w") as f:
                f.write(data)
    """
    if sys.platform == "win32":
        import msvcrt

        lock_file = open(lock_path, "w")
        try:
            msvcrt.locking(lock_file.fileno(), msvcrt.LK_LOCK, 1)
            yield
        finally:
            try:
                msvcrt.locking(lock_file.fileno(), msvcrt.LK_UNLCK, 1)
            except OSError:
                pass
            lock_file.close()
            try:
                os.remove(lock_path)
            except OSError:
                pass
    else:  # pyright: ignore[unreachable]
        import fcntl

        lock_file = open(lock_path, "w")
        try:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
            yield
        finally:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
            lock_file.close()
            try:
                os.remove(lock_path)
            except OSError:
                pass
