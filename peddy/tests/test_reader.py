from __future__ import print_function

import gzip
import bz2
import os
import tempfile
import sys

from peddy.reader import reader


def _tmp(contents, suffix=""):
    handle = tempfile.NamedTemporaryFile(mode="w", suffix=suffix, delete=False)
    try:
        handle.write(contents)
        return handle.name
    finally:
        handle.close()


def test_reader_tab_dict_rows():
    path = _tmp("#a\tb\n1\t2\n11\t22\n")
    try:
        rows = list(reader(path))
    finally:
        os.unlink(path)

    assert rows == [{"a": "1", "b": "2"}, {"a": "11", "b": "22"}]


def test_reader_comma_dict_rows():
    path = _tmp("sample_a,sample_b,rel\nA,B,0.5\n")
    try:
        rows = list(reader(path, sep=","))
    finally:
        os.unlink(path)

    assert rows == [{"sample_a": "A", "sample_b": "B", "rel": "0.5"}]


def test_reader_whitespace_no_header():
    path = _tmp("a b c\n1 2 3\n")
    try:
        rows = list(reader(path, header=False, sep=None))
    finally:
        os.unlink(path)

    assert rows == [["a", "b", "c"], ["1", "2", "3"]]


def test_reader_argv_index():
    path = _tmp("x\ty\n7\t9\n")
    old_argv = sys.argv
    sys.argv = [old_argv[0], path]
    try:
        rows = list(reader(1))
    finally:
        sys.argv = old_argv
        os.unlink(path)

    assert rows == [{"x": "7", "y": "9"}]


def test_reader_gzip():
    path = tempfile.mktemp(suffix=".gz")
    with gzip.open(path, "wt") as fh:
        fh.write("a\tb\n1\t2\n")
    try:
        rows = list(reader(path))
    finally:
        os.unlink(path)

    assert rows == [{"a": "1", "b": "2"}]


def test_reader_bz2():
    path = tempfile.mktemp(suffix=".bz2")
    with bz2.open(path, "wt") as fh:
        fh.write("a\tb\n1\t2\n")
    try:
        rows = list(reader(path))
    finally:
        os.unlink(path)

    assert rows == [{"a": "1", "b": "2"}]


def test_reader_quoted_field_with_newline():
    """Ensure newline='' lets csv.reader handle embedded newlines."""
    path = _tmp('a,b\n"hello\nworld",2\n', suffix=".csv")
    try:
        rows = list(reader(path, sep=","))
    finally:
        os.unlink(path)

    assert rows == [{"a": "hello\nworld", "b": "2"}]
