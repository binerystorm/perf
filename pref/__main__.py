import sys 
import os
import logging as log
import os.path as osp
from typing import TextIO, Callable

Flag = dict[str, bool]

logger = log.getLogger("verbose")
stream_hndl = log.StreamHandler()

logger.addHandler(stream_hndl)
logger.setLevel(log.INFO)

class Conf:
    ops = {
        "-r": False,
        "-v": False,
        "-h": False,
        "-d": False
    }

def print_usage(out: TextIO) -> None:
    print("pref <directory> <prefix> [option]", file=out)
    print("Option:", file=out)
    print("\t-r: prefixes everything in the directory recursivly", file=out)
    print("\t-v: makes files verbosly", file=out)
    print("\t-h: prints this menu", file=out)
    print("\t-d: includes directories in renaming", file=out)

def parse_ops(args: list[str]) -> None:
    for arg in args:
        try:
            Conf.ops[arg] = True
        except IndexError:
            print(f"error: unknown flag `{arg}`")
            print_usage(sys.stderr)
            exit(1)


def pref_file(fobj: str, prefix: str) -> str:
    root, f = osp.split(fobj)
    new_f = osp.join(root, f"{prefix}{f}")
    logger.debug(f"renaming: {fobj} -> {new_f}")
    os.rename(fobj, new_f)
    return new_f

def treverse_dir(path: str, prefix: str) -> None:
    for fobj in map(lambda x: osp.join(path, x), os.listdir(path)):
        if not osp.isdir(fobj) or Conf.ops['-d']:
            pref_file(fobj, prefix)

def recursive_treverse_dir(path: str, prefix: str) -> None:
    for fobj in map(lambda x: osp.join(path, x), os.listdir(path)):
        if osp.isdir(fobj):
            if Conf.ops['-d']:
                new_f = pref_file(fobj, prefix)
                recursive_treverse_dir(new_f, prefix)
            else:
                recursive_treverse_dir(fobj, prefix)
        else:
            pref_file(fobj, prefix)

def run(directory: str, prefix: str) -> None:
    if Conf.ops['-v']:
        logger.setLevel(log.DEBUG)
        logger.debug("dir to search: " + directory)
        logger.debug("prefix: " + prefix)
    if Conf.ops['-h']:
        print_usage(sys.stdout)
    if Conf.ops['-r']:
        recursive_treverse_dir(directory, prefix)
    else:
        treverse_dir(directory, prefix)



def main() -> None:
    if len(sys.argv) < 3:
        print("error: prefix wasn't provided")
        print_usage(sys.stderr)
        exit(1)
    if len(sys.argv) < 2:
        print("error: no arguments were provided")
        print_usage(sys.stderr)
        exit(1)

    directory = osp.abspath(sys.argv[1])
    prefix = sys.argv[2]
    parse_ops(sys.argv[3:])


    if not osp.isdir(directory):
        print(f"error: {directory} is not a directory")
        exit(2)

    if '/' in prefix or '\\' in prefix:
        print(f"error: prefix may not contain `/` or `\\`")
        exit(3)

    run(directory, prefix)

main()



