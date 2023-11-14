from typing import Dict, Any


class error(Exception):
    ...


def encode_blob(file_data: bytes) -> bytes:
    """
    Takes binary data of a file and outputs blob object data in the following format:
    b"{type} {size}\\x00{content}"

    Example:
    b"blob 22\\x00print('Hello World')\\n"
    """
    byte_size = len(file_data)
    header = f"blob {byte_size}\x00".encode()
    return header + file_data


def encode_tree():
    pass


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
        # b"{type} {size}\x00{object}{object}"
        size = int(binary_data[0:first_nul_index].split(b" ")[1].decode())

        entries_data = binary_data[first_nul_index + 1 :]

        space_indexes = [
            i for i in range(len(entries_data)) if entries_data.startswith(b" ", i)
        ]

        # where to split the entries
        indexes = list(map(lambda i: i - 6, space_indexes[1:]))

        # split using the indexes, resulting in an array of binary data of each entry
        entry_splits = [
            entries_data[i:j] for i, j in zip([0] + indexes, indexes + [None])
        ]

        object_entries = []
        for entry in entry_splits:
            b'100644 .gitignore\x00}\xa9\x03K\xa8\xa3\xfa\xa2\xa5\xaa\x96"vz\xef\xb1\\\x8dv'
            b"\x8540000 app\x00\x9eu\x86ej2'\x8b\r\xd8G\xf2\x0b\xb2\xec\x96\x9bG\xa3W" # why the fuck is there a 0x85 instead of 0
            b'100755 gut.sh\x00nU\xf9-W\xd2\xe7W\x89\x82\xcak\x17X%\xb1F\x95\xa7\xd7'
            print(entry)
            # first_nul_index = entry.find(b"\x00")
            # print(entry)
            # mode = entry[0:6].decode()
            # name = entry[7:first_nul_index].decode()
            # _hash = "".join([format(b, "02x") for b in entry[first_nul_index + 1 :]])
            # object_entries.append({"mode": mode, "name": name, "hash": _hash})
        return {"type": "tree", "size": size, "objects": object_entries}
    else:
        raise error(f"fatal: decoding {object_type} object type is not implemented")
