from utils import get_repository_abspath
import commands
from create_parser import create_parser


def main():
    repo_abspath = get_repository_abspath()

    parser = create_parser()
    args = parser.parse_args()
    
    command = args.command

    if command is None:
        print(parser.format_help())
        exit(0)

    if command == "init":
        repo_abspath = commands.init(args, repo_abspath)

    if repo_abspath is None:
        print("fatal: not a git repository (or any of the parent directories): .git")
        exit(1)

    if command == "cat-file":
        commands.cat_file(args, repo_abspath)
    elif command == "hash-object":
        commands.hash_object(args, repo_abspath)
    elif command == "write-tree":
        commands.write_tree(args, repo_abspath)


if __name__ == "__main__":
    main()
