from typing import Dict, Any, List, NamedTuple
from binascii import hexlify


class error(Exception):
    ...


class TreeObject(NamedTuple):
    name: str
    mode: str
    hash_bytes: bytes


def encode_blob(file_data: bytes) -> bytes:
    """
    Takes binary data of a file and outputs Gut blob object data in the following format:

    b"{type} {content_size}\\x00{content}"

    Example:
    b"blob 22\\x00print('Hello World')\\n"
    """

    byte_size = len(file_data)
    header = f"blob {byte_size}\x00".encode()
    return header + file_data


def encode_tree(tree_objects: List[TreeObject]) -> bytes:
    """
    Takes a list of TreeObject named tuples (name: str, mode: str, hash_bytes: bytes).

    Outputs Gut tree object data in the following format:

    b"{type} {content_size}\\x00{object}{object}..."

    where each object is represented as b"{file_mode} {file_name}{hash_bytes}"
    """

    objects_data = b""
    for obj in tree_objects:
        name = obj.name.encode()
        mode = obj.mode.encode()
        hash_bytes = bytes.fromhex(obj.hash_bytes)
        objects_data += f"{mode} {name}{hash_bytes}".encode()

    byte_size = len(objects_data)
    header = f"tree {byte_size}\x00".encode()

    return header + objects_data


def decode_file_content(binary_content: bytes) -> str | None:
    try:
        return binary_content.decode("utf-8")
    except UnicodeDecodeError:
        return None


def decode_object(binary_data: bytes) -> Dict[str, Any]:
    object_type = binary_data[0 : binary_data.find(b" ")].decode()
    first_nul_index = binary_data.find(b"\x00")

    if object_type == "blob":
        # b"{type} {size}\x00{content}"
        header = binary_data[0:first_nul_index]
        file_content = binary_data[first_nul_index + 1 :]
        content_byte_size = int(header.split(b" ")[1])
        decoded_file_content = decode_file_content(file_content)

        blob_object = {
            "type": "blob",
            "size": content_byte_size,
            "file_content": file_content,
            "decoded_file_content": decoded_file_content,
        }
        return blob_object

    elif object_type == "tree":
        # TODO: convince myself to refactor this shit
        # TODO: refactor this shit
        # b"{type} {size}\x00{object}{object}"
        size = int(binary_data[0:first_nul_index].split(b" ")[1].decode())

        entries_data = binary_data[first_nul_index + 1 :]

        indexes = [
            i for i in range(len(entries_data)) if entries_data.startswith(b" ", i)
        ]

        # split using the indexes, resulting in an array of binary data of each entry
        entry_splits = [
            entries_data[i:j] for i, j in zip([0] + indexes, indexes + [None])
        ]

        # extract the modes and remove them from entry_splits
        modes: List[str] = []
        for i in range(len(entry_splits) - 1):
            entry = entry_splits[i]
            mode_length = 6
            if entry.endswith(b"40000"):
                mode_length = (
                    5  # git just doesnt store the first 0 for tree because reasons
                )
            mode = entry[-mode_length:]
            if mode_length == 5:
                mode = (
                    b"0" + mode
                )  # add the missing 0 to 40000 to get the 040000 tree mode

            entry_splits[i] = entry_splits[i][
                :-mode_length
            ]  # remove mode at the end from entries
            modes.append(mode.decode())

        entries = list(map(lambda e: e[1:], entry_splits[1:]))

        object_entries: Dict[str, Any] = []
        for i in range(len(entries)):
            entry = entries[i]
            first_nul_index_entry = entries[i].index(b"\x00")

            mode = modes[i]
            name = entry[:first_nul_index_entry].decode()
            hash_ = hexlify(entry[first_nul_index_entry + 1 :]).decode()
            assert len(hash_) == 40

            object_entries.append({"mode": mode, "name": name, "hash": hash_})

        return {"type": "tree", "size": size, "objects": object_entries}

    raise error(f"fatal: decoding {object_type} object type is not implemented")
