# scan header inclusion

import os
import re
import colorama
import argparse

from sourcetree import collect_sources, SourceDir
from graphviz import Digraph


class IncludeGraph(object):
    """A graph to represent the inclusion relation"""

    def __init__(self, prefix):
        self.gph = Digraph(prefix)
        self.prefix = prefix
        self.nodes = set([])
        self.internal_color = "blue"
        self.external_color = "green"

    def node(self, x):
        xp = self.normalize_name(x)
        if xp not in self.nodes:
            self.nodes.add(xp)
            icr = self.internal_color
            ecr = self.external_color
            if self.isinternal(x):
                self.gph.node(xp, color=icr, fontcolor=icr)
            else:
                self.gph.node(xp, color=ecr, fontcolor=ecr)

    def edge(self, x, y):
        xp = self.normalize_name(x)
        yp = self.normalize_name(y)
        self.node(x)
        self.node(y)
        if self.isinternal(x):
            self.gph.edge(xp, yp, color=self.internal_color)
        else:
            self.gph.edge(xp, yp, color=self.external_color)

    def isinternal(self, x):
        return x.startswith(self.prefix)

    def normalize_name(self, x):
        pf = self.prefix
        if x.startswith(pf):
            return x[len(pf)+1:]
        else:
            return '<' + x + '>'

    def write(self, filename):
        with open(filename, 'w') as f:
            f.write(self.gph.source)



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

    # command line options

    argp = argparse.ArgumentParser(description="C++ header inclusion analysis.")
    argp.add_argument("source", help="the source including path")
    argp.add_argument("-g", "--graph", type=str, help="specify the output graph file")
    argp.add_argument("-q", "--quiet", help="enable quiet mode", action="store_true")
    argp.add_argument("-V", "--view", help="view the graph at the end", action="store_true")
    argp.add_argument("-E", "--external", help="specify whether to include external headers", action="store_true")

    args = argp.parse_args()
    rootdir = args.source
    outgraph = args.graph
    quiet = args.quiet
    viewgraph = args.view
    ext = args.external

    # collect source files
    if not os.path.isdir(rootdir):
        raise ValueError, "%s is not a directory" % rootdir
    rootsrc = collect_sources(rootdir)

    # find common prefix of include
    if len(rootsrc.children) == 1 and \
        isinstance(rootsrc.children[0], SourceDir):
            prefixdir = rootsrc.children[0]
    else:
        raise ValueError, "The include path must have exactly one sub-directory."

    prefix = prefixdir.relpath
    srcfiles = rootsrc.all_source_files()

    # main process

    if outgraph:
        g = IncludeGraph(prefix)

    for src in srcfiles:
        t = src.relpath
        if outgraph:
            if ext or g.isinternal(t):
                g.node(t)
        if not quiet:
            print colorama.Fore.BLUE + t + colorama.Fore.RESET

        incs = scan_includes(src.abspath)
        for s in incs:
            if not quiet:
                print "|  ", s                
                if outgraph:
                    if ext or g.isinternal(s):
                        g.edge(s, t)

    if outgraph:
        if not quiet:
            print "Writing to graph file:", outgraph
        g.write(outgraph)
        if viewgraph:
            g.gph.view()
