import sys

from utils import get_repository_abspath
import commands
from create_parser import create_parser


def main():
    repo_abspath = get_repository_abspath()

    parser = create_parser()

    help_message = parser.format_help()
    args = parser.parse_args()

    if len(sys.argv) < 2:
        return print(help_message)

    command = sys.argv[1]

    if command == "init":
        repo_abspath = commands.init(args, repo_abspath)
    elif command == "cat-file":
        commands.cat_file(args, repo_abspath)
    elif command == "hash-object":
        commands.hash_object(args, repo_abspath)
    elif command == "write-tree":
        commands.write_tree(args, repo_abspath)


if __name__ == "__main__":
    main()
