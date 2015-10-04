# scan header inclusion

import sys
import os
import re
import colorama
from sourcetree import collect_sources
from graphviz import Digraph

# group(2) is the included path
include_regex = re.compile(r"#\s*include\s*(\<|\")\s*([\w\/.]+)\s*(\>|\")")

def scan_includes(filename):
    """Return a list of included files"""

    with open(filename) as f:
        lines = f.readlines()

    included = []

    for line in lines:
        line = line.strip()
        if len(line) == 0 or line.startswith('/'):
            continue

        m = include_regex.match(line)
        if m:
            included.append(m.group(2))

    return included


if __name__ == '__main__':

    rootdir = sys.argv[1]
    if not os.path.isdir(rootdir):
        raise ValueError, "%s is not a directory" % rootdir

    outfile = sys.argv[2]

    rootsrc = collect_sources(rootdir)
    srcfiles = rootsrc.all_source_files()

    nodes = set([])
    g = Digraph()

    for src in srcfiles:
        t = src.relpath
        if t not in nodes:
            nodes.add(t)
            g.node(t)

        print colorama.Fore.BLUE + src.relpath + colorama.Fore.RESET
        incs = scan_includes(src.abspath)
        for s in incs:
            print "|  ", s
            if s.endswith(".h") or s.endswith(".hpp"):
                if s not in nodes:
                    nodes.add(s)
                    g.node(s)
                g.edge(s, t)

    with open(outfile, "w") as fout:
        fout.write(g.source)
