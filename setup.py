#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  Copyright 2014-2021 Ramil Nugmanov <nougmanoff@protonmail.com>
#  Copyright 2014-2022 Timur Madzhidov <tmadzhidov@gmail.com>
#  This file is part of CGRtools.
#
#  CGRtools is free software; you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with this program; if not, see <https://www.gnu.org/licenses/>.
#
import sys
from pathlib import Path
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext as _build_ext


class build_ext(_build_ext):
    """Custom build_ext to handle Cython compilation."""
    
    def run(self):
        # Import Cython here and compile just before building
        try:
            from Cython.Build import cythonize
            if self.distribution.ext_modules:
                self.distribution.ext_modules = cythonize(
                    self.distribution.ext_modules,
                    language_level=3,
                    compiler_directives={'embedsignature': True}
                )
        except ImportError:
            # If Cython is not available during build, look for pre-generated C files
            print("Cython not found. Looking for pre-generated C files...", file=sys.stderr)
            c_file = Path('CGRtools/containers/_unpack.c')
            if c_file.exists() and self.distribution.ext_modules:
                # Replace .pyx with .c in sources
                for ext in self.distribution.ext_modules:
                    ext.sources = [src.replace('.pyx', '.c') for src in ext.sources]
            else:
                print("Warning: Neither Cython nor pre-generated C files found. "
                      "Extension modules will not be built.", file=sys.stderr)
                self.distribution.ext_modules = []
        
        super().run()


def get_data_files():
    """Get platform-specific INCHI library files for wheel."""
    import platform
    
    data_files = []
    system = platform.system()
    machine = platform.machine()
    
    # Include INCHI libraries based on platform
    if system == 'Windows' and machine in ('AMD64', 'x86_64'):
        dll_path = Path('INCHI/libinchi.dll')
        if dll_path.exists():
            data_files.append(('lib', ['INCHI/libinchi.dll']))
    elif system == 'Linux' and machine in ('x86_64',):
        so_path = Path('INCHI/libinchi.so')
        if so_path.exists():
            data_files.append(('lib', ['INCHI/libinchi.so']))
    #TODO for MacOS InChI library should be built from source 
    
    return data_files


# Extension modules
ext_modules = [
    Extension(
        'CGRtools.containers._unpack',
        ['CGRtools/containers/_unpack.pyx'],
        extra_compile_args=['-O3']
    )
]

# For source distributions, include both library files
if 'sdist' in sys.argv:
    data_files = [('lib', ['INCHI/libinchi.so', 'INCHI/libinchi.dll'])]
else:
    data_files = get_data_files()

setup(
    ext_modules=ext_modules,
    data_files=data_files,
    cmdclass={'build_ext': build_ext},
    zip_safe=False,
)
