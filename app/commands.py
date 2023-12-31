from typing import Dict, List, Any
import os
import hashlib

import object_database
import serialization


def init(args, repo_abspath: str):
    if repo_abspath is not None:
        # TODO: handle already existing repository
        print(f"Reinitialized existing Gut repository in {repo_abspath}")
        exit(0)

    os.mkdir(".gut/")
    os.mkdir(".gut/objects")
    os.mkdir(".gut/refs")
    with open(".gut/HEAD", "w") as f:
        f.write("ref: refs/heads/master\n")

    new_repo_abspath = os.path.join(os.getcwd(), ".gut/")
    print(f"Initialized Gut directory in {new_repo_abspath}")


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
    elif len(object_hash) < 40:
        gut_object = object_database.get_object_by_hash_abbreviation(
            object_hash, repo_abspath
        )
    else:
        gut_object = object_database.get_object_by_hash(object_hash, repo_abspath)

    if args.type:
        if gut_object is None:
            print("fatal: git cat-file: could not get object info")
            exit(1)
        print(gut_object["type"])

    elif args.size:
        if gut_object is None:
            print("fatal: git cat-file: could not get object info")
            exit(1)
        print(gut_object["size"])

    elif args.pretty:
        if gut_object is None:
            print(f"fatal: Not a valid object name {object_hash}")
            exit(1)

        if gut_object["type"] == "blob":
            output = gut_object["decoded_file_content"] or gut_object.get(
                "file_content"
            )
            print(output, end="")
        elif gut_object["type"] == "tree":
            output = ""
            for obj in gut_object["objects"]:
                mode = obj["mode"]
                name = obj["name"]
                hash_ = obj["hash"]
                type_ = None
                try:
                    obj = object_database.get_object_by_hash(hash_, repo_abspath)
                    type_ = obj["type"]
                except object_database.error as e:
                    print(e)
                    exit(1)
                    # TODO: print other errors if present

                entry = f"{mode} {type_} {hash_}    {name}\n"
                output += entry
            print(output, end="")
    elif args.exists:
        if gut_object is None:
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
    root_path = os.path.dirname(repo_abspath)

    gut_ignore_file_path = os.path.dirname(repo_abspath)
    gut_ignore_entries = [".git", "app/__pycache__"]  # TODO: read from file
    EXCLUDED_DIRS = [
        os.path.join(gut_ignore_file_path, entry)
        for entry in (".gut", *gut_ignore_entries)
    ]

    def create_and_write_tree(current_dir: str) -> Dict[str, Any]:
        tree = {
            "name": os.path.basename(current_dir),
            "type": "tree",
            "mode": "040000",
            "hash": None,
            "objects": [],
        }

        for entry in os.listdir(current_dir):
            entry_abspath = os.path.join(current_dir, entry)

            if entry_abspath in EXCLUDED_DIRS:
                continue

            if os.path.isdir(entry_abspath):
                # TODO: recursive -> iterative
                subtree = create_and_write_tree(entry_abspath)
                tree["objects"].append(subtree)
            else:
                file_content = None
                with open(entry_abspath, "rb") as f:
                    file_content = f.read()

                hash_ = hashlib.sha1(file_content).hexdigest()

                object_database.write_blob_object(file_content, repo_abspath)

                is_symlink = os.path.islink(entry_abspath)
                is_executable = bool(os.stat(entry_abspath).st_mode & 0o111)

                if is_symlink:
                    mode = "120000"
                elif is_executable:
                    mode = "100755"
                else:
                    mode = "100644"

                blob = {"name": entry, "type": "blob", "mode": mode, "hash": hash_}
                tree["objects"].append(blob)

        tree_objects = tree["objects"]

        # convert tree_object dicts to TreeObject named tuples
        tuple_tree_objects = [
            serialization.TreeObject(obj["name"], obj["mode"], obj["hash"])
            for obj in tree_objects
        ]

        encoded_tree_object = serialization.encode_tree(tuple_tree_objects)
        hash_ = hashlib.sha1(encoded_tree_object).hexdigest()
        tree["hash"] = hash_

        # do not write a tree without any files
        if len(tree_objects) != 0:
            object_database.write_tree_object(tuple_tree_objects, hash_, repo_abspath)

        return tree

    tree = create_and_write_tree(root_path)
    print(tree["hash"])

    # TODO: move code below to ls-tree

    # objects: List[Dict[str, Any]] = tree["objects"]

    # objects.sort(key=lambda obj: obj["name"])

    # output = ""
    # for obj in objects:
    #     mode = obj["mode"]
    #     type_ = obj["type"]
    #     hash_ = obj["hash"]
    #     name = obj["name"]

    #     output += f"{mode} {type_} {hash_}    {name}\n"

    # print(output, end="")


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
