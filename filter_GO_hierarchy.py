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
    parser.add_argument('--hierarchy', required=False, default='', choices=['biological_process', 'molecular_function', 'cellular_component'])

    args = parser.parse_args(argv)

    args.namespace = 'namespace: '+args.hierarchy

    return args


def simple_parse(args, print_out=False, create_dictionary=True):
    import re

    print_out = (lambda line: print(line, end='')) if print_out else (lambda _: None)

    dictionary = {} if create_dictionary else None

    state = 'no_term'
    go_id = None
    regex_go_id = re.compile('GO:[0-9]+')

    with open(args.go_file) as f:
        for line in f:
            if line.startswith('[Term]'):
                term_token = line
                go_id_line = next(f)
                go_id = regex_go_id.search(go_id_line).group()
                name_line = next(f)
                namespace_line = next(f)

                if namespace_line.startswith(args.namespace):
                    state = 'print'
                    print_out(term_token)
                    print_out(go_id_line)
                    print_out(name_line)
                    print_out(namespace_line)
                else:
                    state = 'no_print'

            elif line == f.newlines:
                if state == 'print':
                    print_out(line)

                state = 'no_term'

            elif state == 'print':
                print_out(line)

                if create_dictionary and (line.startswith('is_a: ') or line.startswith('relationship: part_of')):
                    parent = regex_go_id.search(line).group()
                    parents = dictionary.get(go_id, [])
                    dictionary[go_id] = [*parents, parent]

            else:
                continue

    return dictionary


if __name__ == "__main__":
    import sys
    args = parse_arguments(sys.argv[1:])
    ret = simple_parse(args, print_out=True, create_dictionary=True)
