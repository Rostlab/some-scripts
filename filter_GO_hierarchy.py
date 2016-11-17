#!/usr/bin/env python3
import sys

assert sys.version_info.major == 3, "the script requires Python 3"


__author__ = "Juan Miguel Cejuela (@juanmirocks)"

__help__ = """  Filter given GO ontology by the given GO hierarchy.

                The script takes 2 arguments:
                    1. a file path with the downloaded GO ontology file (.obo; basic or normal)
                        example: http://purl.obolibrary.org/obo/go/go-basic.obo
                    2. the GO hierarchy to extract

                The script then outputs only those GO terms that belong to the desired GO hierarchy,
                thus potentially reducing the final file size significantly.

                Note: the output is printed to standard output. Redirect this to a file if needed.
           """


def parse_arguments(argv=[]):
    import argparse

    parser = argparse.ArgumentParser(description=__help__)

    parser.add_argument('go_file', help='GO ontology file in .obo format')
    parser.add_argument('hierarchy', choices=['biological_process', 'molecular_function', 'cellular_component'])

    args = parser.parse_args(argv)

    args.namespace = 'namespace: '+args.hierarchy

    return args


def run(args):

    state = 'no_term'

    with open(args.go_file) as f:
        for line in f:
            if line.startswith('[Term]'):
                term_token = line
                go_id = next(f)
                name = next(f)
                namespace = next(f)

                if namespace.startswith(args.namespace):
                    state = 'print'
                    print(term_token, end='')
                    print(go_id, end='')
                    print(name, end='')
                    print(namespace, end='')
                else:
                    state = 'no_print'

            elif line == f.newlines:
                if state == 'print':
                    print(line, end='')

                state = 'no_term'

            elif state == 'print':
                print(line, end='')

            else:
                continue


if __name__ == "__main__":
    import sys
    args = parse_arguments(sys.argv[1:])
    run(args)
