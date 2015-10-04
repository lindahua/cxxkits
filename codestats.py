# Compute simple code statistics for a given project
#
#  It will search all directories, except those begins with "build"
#

import os
import sys
import colorama
from sourcetree import collect_sources, SourceFile, SourceDir

def count_lines(filename):
    """Count the number of lines in a source file

        Return a pair (n0, n1), where n0 is the total
        number of lines, while n1 is the number of non-empty
        lines
    """

    with open(filename) as f:
        lines = f.readlines()

    n0 = len(lines)
    n1 = 0
    for line in lines:
        line = line.strip()
        if len(line) > 0:
            n1 += 1

    return (n0, n1)


def run_stats(s, quiet=False):
    if not quiet:
        if len(s.relpath) == 0:
            print "On", s.abspath

    tn0 = 0
    tn1 = 0
    if isinstance(s, SourceDir):
        for c in s.children:
            n0, n1 = run_stats(c, quiet=quiet)
            tn0 += n0
            tn1 += n1
    else:
        assert isinstance(s, SourceFile)
        n0, n1 = count_lines(s.abspath)
        tn0 += n0
        tn1 += n1

    if not quiet:
        if len(s.relpath) > 0:
            line = "%s (%d, %d)" % (s.relpath, tn0, tn1)
            if isinstance(s, SourceDir):
                print(colorama.Fore.BLUE + line + colorama.Fore.RESET)
            else:
                print(line)
    return tn0, tn1


if __name__ == '__main__':

    rootdir = sys.argv[1]
    if not os.path.isdir(rootdir):
        raise ValueError, "%s is not a directory" % rootdir

    sources = collect_sources(rootdir)
    nf = sources.num_source_files
    tn0, tn1 = run_stats(sources)
    line = "Total %d files, %d lines, %d non-empty" % (nf, tn0, tn1)
    print(colorama.Fore.RED + line + colorama.Fore.RESET)
