import argparse


def create_parser():
    parser = argparse.ArgumentParser(
        description="Gut - Git clone that will make me understand how Git actually works"
    )
    subparsers = parser.add_subparsers(
        dest="command", title="commands", description="Available commands"
    )

    subparsers.add_parser("init", description="Initialize a repository")

    cat_file_parser = subparsers.add_parser(
        "cat-file", description="Display the content of an object"
    )
    cat_file_parser_group = cat_file_parser.add_mutually_exclusive_group(required=True)
    cat_file_parser_group.add_argument(
        "-p",
        "--pretty",
        action="store_true",
        help="Display contents of the object in human-readable format",
    )
    cat_file_parser_group.add_argument(
        "-e",
        "--exists",
        action="store_true",
        help="Returns exit code (0) if file exists, otherwise returns exit (1)",
    )
    cat_file_parser_group.add_argument(
        "-t", "--type", action="store_true", help="Display the type of the object"
    )
    cat_file_parser_group.add_argument(
        "-s",
        "--size",
        action="store_true",
        help="Display the byte size of the object contents",
    )
    cat_file_parser.add_argument("object", help="The SHA hash of the object")

    hash_object_parser = subparsers.add_parser(
        "hash-object", description="Create an object from a file"
    )
    hash_object_parser.add_argument(
        "-w",
        "--write",
        action="store_true",
        help="Write the object into the object database",
    )
    hash_object_parser.add_argument(
        "file", nargs="?", type=str, help="The path to a file to hash"
    )

    write_tree_parser = subparsers.add_parser(
        "write-tree", description="Create a tree object using the current index"
    )

    return parser
