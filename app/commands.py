import os
import hashlib

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
        gut_object = object_database.get_object_by_hash_abbreviation(object_hash, repo_abspath)
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
