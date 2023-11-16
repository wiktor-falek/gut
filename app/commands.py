from typing import Dict, List, Any
import os
import hashlib
import json

import object_database


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
    object_hash: str = args.object

    gut_object_file_path = os.path.join(
        repo_abspath, f"objects/{object_hash[0:2]}/{object_hash[2:]}"
    )

    # minimum 4 chars for abbreviation
    if 4 > len(object_hash) <= 40:
        print(f"fatal: Not a valid object name {object_hash}")
        exit(1)

    if object_hash == "master^{tree}":
        gut_object = object_database.get_commit_tree_object(repo_abspath)
    if len(object_hash) < 40:
        gut_object = object_database.get_object_by_hash_abbreviation(
            object_hash, repo_abspath
        )
    else:
        gut_object = object_database.get_object_by_hash(object_hash, repo_abspath)

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
            output = ""
            for obj in gut_object.get("objects"):
                mode = obj.get("mode")
                name = obj.get("name")
                hash_ = obj.get("hash")
                type_ = None
                try:
                    obj = object_database.get_object_by_hash(hash_, repo_abspath)
                    type_ = obj.get("type")
                except object_database.error as e:
                    print(e)
                    exit(1)
                    # TODO: print other errors if present

                entry = f"{mode} {type_} {hash_}    {name}\n"
                output += entry
            print(output, end="")
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

        object_database.write_blob_object(file_content, repo_abspath)
    else:
        print(object_hash)


def write_tree(args, repo_abspath: str):
    root_path = os.path.abspath(os.path.join(repo_abspath, ".."))

    EXCLUDED_DIRS = (".gut", ".git", "__pycache__")

    def create_tree(current_dir: str) -> Dict[str, Any]:
        tree = {
            "name": os.path.basename(current_dir),
            "type": "tree",
            "mode": "040000",
            "hash": None,
            "objects": [],
        }
        for entry in os.listdir(current_dir):
            if entry.endswith(EXCLUDED_DIRS):
                continue
            entry_path = os.path.join(current_dir, entry)

            if os.path.isdir(entry_path):
                subtree = create_tree(entry_path)
                tree.get("objects").append(subtree)
            else:
                # TODO: read file contents at entry_path
                # TODO: create and write a blob to the database

                # TODO: check if file is a symlink or is executable and set appropriate mode
                blob = {"name": entry, "type": "blob", "mode": "100644", "hash": None}
                blob["hash"] = "TODO"
                tree.get("objects").append(blob)

        # ignore empty trees
        if len(tree.get("objects")) != 0:
            tree["hash"] = "TODO"
            # write the tree
            pass

        return tree

    tree = create_tree(root_path)

    # print(tree.get("hash"))
    # TODO: move code below to ls-tree

    objects: List[Dict[str, Any]] = tree.get("objects")

    objects.sort(key=lambda obj: obj.get("name"))

    output = ""
    for obj in objects:
        mode = obj.get("mode")
        type_ = obj.get("type")
        hash_ = obj.get("hash")
        name = obj.get("name")

        output += f"{mode} {type_} {hash_}    {name}\n"

    print(output, end="")

    """
    100644 blob 7da9034ba8a3faa2a5aa9622767aefb15c8d7685    .gitignore
    040000 tree 1ea2d05d385f2b4b4215875c45a9141db2546e58    app
    100755 blob 6e55f92d57d2e7578982ca6b175825b14695a7d7    gut.sh
    """

    """
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
