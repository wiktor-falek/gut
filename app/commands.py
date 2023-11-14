import os
import zlib
import hashlib
from pprint import pprint

import serialization


def init(args, repo_abspath: str) -> str:
    if repo_abspath is not None:
        # TODO: handle already existing repository
        print(f"Reinitialized existing Gut repository in {repo_abspath}")
        return repo_abspath

    os.mkdir(".gut/")
    os.mkdir(".gut/objects")
    os.mkdir(".gut/refs")
    with open(".gut/HEAD", "w") as f:
        f.write("ref: refs/heads/master\n")

    new_repo_abspath = os.path.join(os.getcwd(), ".gut/")
    print(f"Initialized Gut directory in {new_repo_abspath}")
    return new_repo_abspath


def cat_file(args, repo_abspath: str):
    """
    Git file mode
    https://git-scm.com/book/en/v2/Git-Internals-Git-Objects

    +------------>100644 blob 7da9034ba8a3faa2a5aa9622767aefb15c8d7685    .gitignore
    |  +--------->040000 tree c4d3b6ff63df9061e2a7fd99c2d41b811d6a46b1    app
    |  |  +------>100755 blob 410c61170ddcb767fec99cc099d94c4178f252b2    gut.sh
    |  |  |  +--->120000 blob 72155dacaa143b5d8365aaf8186267c31653764f    symlink
    |  |  |  |
    |  |  |  |
    |  |  |  |
    |  |  |  symbolic link
    |  |  |
    |  |  executable file
    |  |
    |  directory
    |
    normal file
    """

    object_name = args.object

    # TODO: set gut_object to the master tree if object_name == "master^{tree}"
    # print("100644 blob 7da9034ba8a3faa2a5aa9622767aefb15c8d7685    .gitignore")
    # print("040000 tree 8405473ebedbe924d9ea17b3ef8afd3ca2323a4a    app")
    # print("100755 blob 410c61170ddcb767fec99cc099d94c4178f252b2    gut.sh")

    gut_object_file_path = os.path.join(
        repo_abspath, f"objects/{object_name[0:2]}/{object_name[2:]}"
    )

    # TODO: implement abbreviations i.e. first letters of hash instead of whole thing

    gut_object = None
    try:
        with open(gut_object_file_path, "rb") as f:
            compressed_data = f.read()
            decompressed_data = zlib.decompress(compressed_data)
            gut_object = serialization.decode_object(decompressed_data)
    except FileNotFoundError:
        print(f"fatal: Not a valid object name '{object_name}'")
        exit(1)
    except zlib.error:
        print("fatal: Error during zlib decompression")
        exit(1)
    except serialization.error as e:
        print(e.args[0])
        exit(1)

    if args.type:
        print(gut_object.get("type"))
    elif args.size:
        print(gut_object.get("size"))
    elif args.pretty:
        if gut_object.get("type") == "blob":
            output = gut_object.get("decoded_file_content") or gut_object.get(
                "file_content"
            )
            print(output, end="")
        elif gut_object.get("type") == "tree":
            pprint(gut_object)
            pass
            # output = ""
            # for obj in gut_object.get("objects"):
            #     mode = obj.get("mode")
            #     name = obj.get("name")
            #     hash_ = obj.get("hash")
            #     type_ = "blob"  # TODO: find object by hash and get the type
            #     entry = f"{mode} {type_} {hash_}    {name}\n"
            #     output += entry
            # print(output, end="")
    elif args.exists:
        gut_object_file_exists = os.path.exists(gut_object_file_path)
        if not gut_object_file_exists:
            exit(1)


def hash_object(args, repo_abspath: str):
    file_path = args.file
    file_exists = file_path is not None and os.path.exists(file_path)
    if not file_exists:
        print(
            f"fatal: could not open '{file_path}' for reading: No such file or directory"
        )
        exit(1)

    if os.path.isdir(file_path):
        print(f"fatal: Unable to hash {os.path.basename(file_path)}")
        exit(1)

    file_content = None
    with open(file_path, "rb") as f:
        file_content: bytes = f.read()

    object_hash = hashlib.sha1(file_content).hexdigest()

    if args.write:
        if repo_abspath is None:
            print(
                "fatal: not a git repository (or any of the parent directories): .git"
            )
            exit(1)

        hash_prefix = object_hash[0:2]
        hash_suffix = object_hash[2:]

        # create prefix dir if it doesn't already exist
        prefix_dir = os.path.join(repo_abspath, f"objects/{hash_prefix}")
        os.makedirs(prefix_dir, exist_ok=True)

        # create the object file
        gut_object_file_path = os.path.join(
            repo_abspath, f"objects/{hash_prefix}/{hash_suffix}"
        )
        with open(gut_object_file_path, "wb") as f:
            blob_data = serialization.encode_blob(file_content)
            f.write(zlib.compress(blob_data))
    else:
        print(object_hash)


def write_tree(args, repo_abspath: str):
    print("write-tree")
    current_path = os.path.join(repo_abspath, "..")

    tree_data = []
    for root, dirs, files in os.walk(current_path, topdown=True):
        if ".gut" in dirs:
            dirs.remove(".gut")
        if ".git" in dirs:
            dirs.remove(".git")

        tree_data.append((root, dirs, files))

    """
    /dir
      file_1.txt
      file_2.txt

    1. go over each file and encode into a blob object
    2. store the blob objects for the tree of /dir directory
    3. encode the directory into a tree object
    4. repeat recursively for each directory

    # object = b"{type} {size}\x00{content}"
    # b"{type} {size}\x00{object}{object}"

    with open(gut_object_file_path, "wb") as f:
        blob_data = serialization.encode_blob(file_content)
        f.write(zlib.compress(blob_data))
    """


def ls_tree(args):
    print("Not implemented")
    exit(1)

    # if object not found
    # print(f"fatal: Not a valid object name {hash}")

    object_type = "blob"

    if object_type != "tree":
        print("fatal: not a tree object")
        exit(1)

    # for each object in tree
    # print(f"{mode} {type} {hash} {name}")
