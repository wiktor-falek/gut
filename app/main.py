import sys

from utils import get_repository_abspath
import commands
from create_parser import create_parser


REPO_ABSPATH = get_repository_abspath()


def main():
    parser = create_parser()

    help_message = parser.format_help()
    args = parser.parse_args()

    if len(sys.argv) < 2:
        return print(help_message)

    command = sys.argv[1]

    if command == "init":
        global REPO_ABSPATH
        REPO_ABSPATH = commands.init(args, REPO_ABSPATH)
    elif command == "cat-file":
        commands.cat_file(args, REPO_ABSPATH)
    elif command == "hash-object":
        commands.hash_object(args, REPO_ABSPATH)
    elif command == "write-tree":
        commands.write_tree(args, REPO_ABSPATH)

if __name__ == "__main__":
    main()
