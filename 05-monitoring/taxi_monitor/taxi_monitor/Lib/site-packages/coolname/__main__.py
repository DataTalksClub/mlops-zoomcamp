import argparse
import sys

from coolname import generate


def parse_args(argv):
    parser = argparse.ArgumentParser(description='Generate slug to stdout')
    parser.add_argument('pattern', nargs='?', type=int, choices=[2, 3, 4], default=None)
    parser.add_argument('-s', '--separator', default='-')
    parser.add_argument('-n', '--number', type=int, default=1, help='how many slugs to generate (default: 1)')
    return parser.parse_args(argv)


def main():
    args = parse_args(sys.argv[1:])
    for _ in range(args.number):
        print(args.separator.join(generate(args.pattern)))


if __name__ == '__main__':
    main()  # pragma: nocover
