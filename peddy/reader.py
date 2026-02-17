from __future__ import print_function

import bz2
import csv
import gzip
import io
import os.path as op
import sys

try:
    int_types = (int, long)  # noqa: F821
except NameError:
    int_types = (int,)


def _open_text(source):
    """
    Open source as a text stream.

    `source` can be a path, "-" (stdin), an integer argv index, or a
    file-like object.
    """
    if isinstance(source, int_types):
        source = sys.argv[source]

    if hasattr(source, "read"):
        return source, False

    source = op.expanduser(op.expandvars(source))
    if source == "-":
        return sys.stdin, False

    if source.endswith((".gz", ".Z", ".z")):
        return gzip.open(source, "rt"), True

    if source.endswith((".bz", ".bz2", ".bzip2")):
        try:
            return bz2.open(source, "rt"), True
        except AttributeError:
            return io.TextIOWrapper(bz2.BZ2File(source, "r")), True

    return io.open(source, "r", newline=''), True


def _rows(source, sep, quotechar):
    stream, close_stream = _open_text(source)
    try:
        if sep is None:
            for line in stream:
                toks = line.rstrip("\r\n").split()
                if toks:
                    yield toks
            return

        if len(sep) == 1:
            kwargs = {"delimiter": sep}
            if quotechar:
                kwargs["quotechar"] = quotechar
            else:
                kwargs["quoting"] = csv.QUOTE_NONE
            for toks in csv.reader(stream, **kwargs):
                if toks:
                    yield toks
            return

        import re
        rex = re.compile(sep)
        for line in stream:
            toks = rex.split(line.rstrip("\r\n"))
            if toks:
                yield toks
    finally:
        if close_stream:
            stream.close()


def reader(source, header=True, sep="\t", quotechar='"'):
    """
    Yield rows from delimited text files.

    If `header` is True, yield dictionaries keyed by the first row.
    If `header` is False, yield token lists.
    If `header` is a list/tuple, use it as column names.
    If `header` is callable, call it with token lists.
    """
    line_gen = _rows(source, sep=sep, quotechar=quotechar)

    if callable(header):
        for toks in line_gen:
            yield header(toks)
        return

    if header is True:
        header = next(line_gen)
        header[0] = header[0].lstrip("#")

    if header:
        for toks in line_gen:
            yield dict(zip(header, toks))
    else:
        for toks in line_gen:
            yield toks
