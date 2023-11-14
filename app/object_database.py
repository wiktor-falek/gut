from typing import Dict, Any
import os
import zlib
import hashlib

import serialization


class error(Exception):
    ...


def _get_object_abspath(object_hash: str, repo_abspath: str) -> str:
    hash_prefix = object_hash[0:2]
    hash_suffix = object_hash[2:]
    obj_abspath = os.path.join(repo_abspath, f"objects/{hash_prefix}/{hash_suffix}")
    return obj_abspath


def write_blob_object(file_content: bytes, repo_abspath: str):
    object_hash = hashlib.sha1(file_content).hexdigest()

    object_abspath = _get_object_abspath(object_hash, repo_abspath)

    # create prefix dir if it doesn't already exist
    prefix_dir_abspath = os.path.join(object_abspath, "..")
    os.makedirs(prefix_dir_abspath, exist_ok=True)

    with open(object_abspath, "wb") as f:
        blob_data = serialization.encode_blob(file_content)
        f.write(zlib.compress(blob_data))


def get_commit_tree_object(repo_abspath: str) -> Dict[str, Any]:
    return error("error: getting commit tree is not implemented")


def get_file_content_by_hash(
    object_hash: str, repo_abspath: str
) -> bytes | None:
    """
    Returns decompressed file content of the object if file exists or None.
    """
    prefix = object_hash[0:2]
    suffix = object_hash[2:]

    file_path = os.path.join(repo_abspath, f"objects/{prefix}/{suffix}")

    with open(file_path, "rb") as f:
        compressed_data = f.read()
        return zlib.decompress(compressed_data)


def object_exists(object_hash: str, repo_abspath: str) -> bool:
    file_path = _get_object_abspath(object_hash, repo_abspath)
    return os.path.exists(file_path)


def get_object_by_hash(object_hash: str, repo_abspath: str) -> Dict[str, Any]:
    file_content = None
    try:
        file_content = get_file_content_by_hash(object_hash, repo_abspath)
    except FileNotFoundError:
        raise error(
            f"error: unable to open loose object {object_hash}: Not a directory"
        )

    gut_object = serialization.decode_object(file_content)
    return gut_object


def get_object_by_hash_abbreviation(
    hash_abbr: str, repo_abspath: str
) -> Dict[str, Any]:
    raise error("error: getting object by abbreviation is not implemented")
