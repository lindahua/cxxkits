# module to analyze a source directory

import sys
import os
import os.path
import colorama

cxx_exts = set([".h", ".c", ".hpp", ".cpp", ".cxx"])

class SourceFile(object):
    """Representing a source file"""

    def __init__(self, rootdir, relpath, ext):
        self.rootdir = rootdir
        self.relpath = relpath
        if len(relpath) == 0:
            self.abspath = self.rootdir
        else:
            self.abspath = os.path.join(self.rootdir, self.relpath)
        self.ext = ext

    def __str__(self):
        return self.abspath

class SourceDir(object):
    """Representing a source directory"""

    def __init__(self, rootdir, relpath, children, nsfiles):
        self.rootdir = rootdir
        self.relpath = relpath
        self.abspath = os.path.join(self.rootdir, self.relpath)
        self.children = children
        self.num_source_files = nsfiles

    def __str__(self):
        return self.abspath

    @property
    def isroot(self):
        return len(self.relpath) == 0

    def all_source_files(self):
        r = []
        for c in self.children:
            if isinstance(c, SourceFile):
                r.append(c)
            else:
                cr = c.all_source_files()
                r.extend(cr)
        return r

def collect_sources(rootdir, relpath="", source_exts=cxx_exts):
    """Collect all sources in a given directory"""

    rootdir = os.path.abspath(rootdir)
    if len(relpath) == 0:
        dirpath = rootdir
    else:
        dirpath = os.path.join(rootdir, relpath)

    ns = 0
    children = []

    # scan children
    for cname in os.listdir(dirpath):
        # ignore hidden & backup files
        if cname.startswith('.') or cname.startswith('~'):
            continue

        # full path of the child
        cpath = os.path.join(dirpath, cname)

        if os.path.isdir(cpath):
            if cname.startswith("build") or cname.startswith("bin") or cname.startswith("deprecate"):
                continue
            subdir = collect_sources(rootdir,
                relpath=os.path.join(relpath, cname),
                source_exts=source_exts)
            if subdir:
                children.append(subdir)
                ns += subdir.num_source_files

        elif os.path.isfile(cpath):
            ext = os.path.splitext(cname)[1]
            if ext in cxx_exts:
                f = SourceFile(rootdir,
                    os.path.join(relpath, cname), ext)
                children.append(f)
                ns += 1

    # construct a SourceDir object for this directory
    if ns > 0:
        return SourceDir(rootdir, relpath, children, ns)
    else:
        return None

def print_sources(sdir):
    """Print all items in a source directory"""

    if sdir.isroot:
        line = "Root: %s (%d)" % (sdir.abspath, sdir.num_source_files)
        print(colorama.Fore.RED + line + colorama.Fore.RESET)
    else:
        line = "> %s (%d)" % (sdir.relpath, sdir.num_source_files)
        print(colorama.Fore.BLUE + line + colorama.Fore.RESET)

    for c in sdir.children:
        if isinstance(c, SourceDir):
            if len(c.children) > 0:
                print_sources(c)
        else:
            print ">", c.relpath


if __name__ == '__main__':

    rootdir = sys.argv[1]
    if not os.path.isdir(rootdir):
        raise ValueError, "%s is not a directory" % rootdir

    sources = collect_sources(rootdir)
    print_sources(sources)
