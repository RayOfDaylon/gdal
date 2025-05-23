#!/usr/bin/env python
# -*- coding: utf-8 -*-
###############################################################################
#
# Project:  GDAL/OGR Test Suite
# Purpose:  Test GDAL as a SQLite3 dynamically loaded extension
# Author:   Even Rouault <even dot rouault at spatialys.com>
#
###############################################################################
# Copyright (c) 2012, Even Rouault <even dot rouault at spatialys.com>
#
# SPDX-License-Identifier: MIT
###############################################################################

# This file is meant at being run by ogr_virtualogr_3()
# This is a bit messy with heavy use of ctypes. The sqlite3 python module
# is rarely compiled with support of extension loading, so we just simulate
# what a tiny C program would do

import sys


def do(sqlite3name, gdalname):
    try:
        import ctypes
    except ImportError:
        print("skip")
        return 0

    sqlite_handle = ctypes.cdll.LoadLibrary(sqlite3name)
    if sqlite_handle is None:
        print("skip")
        return 0

    db = ctypes.c_void_p(0)
    pdb = ctypes.pointer(db)
    if hasattr(sqlite_handle, "sqlite3_open"):
        ret = sqlite_handle.sqlite3_open(":memory:".encode("ascii"), pdb)
    elif hasattr(sqlite_handle, "SPLite3_open"):
        ret = sqlite_handle.SPLite3_open(":memory:".encode("ascii"), pdb)
    else:
        print("skip")
        return 0
    if ret != 0:
        print("Error sqlite3_open ret = %d" % ret)
        return 1

    if hasattr(sqlite_handle, "sqlite3_enable_load_extension"):
        ret = sqlite_handle.sqlite3_enable_load_extension(db, 1)
    elif hasattr(sqlite_handle, "SPLite3_enable_load_extension"):
        ret = sqlite_handle.SPLite3_enable_load_extension(db, 1)
    else:
        print("skip")
        return 0
    if ret != 0:
        print("skip")
        return 0

    gdalname = gdalname.encode("ascii")

    if hasattr(sqlite_handle, "sqlite3_load_extension"):
        ret = sqlite_handle.sqlite3_load_extension(db, gdalname, None, None)
    else:
        ret = sqlite_handle.SPLite3_load_extension(db, gdalname, None, None)
    if ret != 0:
        print("Error sqlite3_load_extension ret = %d" % ret)
        return 1

    tab = ctypes.c_void_p()
    ptab = ctypes.pointer(tab)
    nrow = ctypes.c_int(0)
    pnrow = ctypes.pointer(nrow)
    ncol = ctypes.c_int(0)
    pncol = ctypes.pointer(ncol)

    if hasattr(sqlite_handle, "sqlite3_get_table"):
        ret = sqlite_handle.sqlite3_get_table(
            db, "SELECT ogr_version()".encode("ascii"), ptab, pnrow, pncol, None
        )
    else:
        ret = sqlite_handle.SPLite3_get_table(
            db, "SELECT ogr_version()".encode("ascii"), ptab, pnrow, pncol, None
        )
    if ret != 0:
        print("Error sqlite3_get_table ret = %d" % ret)
        return 1

    cast_tab = ctypes.cast(tab, ctypes.POINTER(ctypes.c_char_p))
    sys.stdout.write(cast_tab[1].decode("ascii"))
    sys.stdout.flush()

    if hasattr(sqlite_handle, "sqlite3_close"):
        ret = sqlite_handle.sqlite3_close(db)
    else:
        ret = sqlite_handle.SPLite3_close(db)
    if ret != 0:
        return 1


def main(argv):
    if len(argv) != 3:
        print("python ogr_as_sqlite_extension name_of_libsqlite3 name_of_libgdal")
        return 1

    return do(argv[1], argv[2])


if __name__ == "__main__":
    sys.exit(main(sys.argv))
