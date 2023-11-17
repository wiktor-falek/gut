from utils import get_repository_abspath
from create_parser import create_parser
import commands


def main():
    repo_abspath = get_repository_abspath()

    parser = create_parser()
    args = parser.parse_args()

    command: str = args.command

    if repo_abspath is None and command != "init":
        print("fatal: not a git repository (or any of the parent directories): .git")
        exit(1)

    match command:
        case "init":
            commands.init(args, repo_abspath)
        case "cat-file":
            commands.cat_file(args, repo_abspath)
        case "hash-object":
            commands.hash_object(args, repo_abspath)
        case "write-tree":
            commands.write_tree(args, repo_abspath)
        case _:
            print(parser.format_help())


if __name__ == "__main__":
    main()
