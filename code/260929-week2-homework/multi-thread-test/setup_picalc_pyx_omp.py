from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize
# CC=gcc-14 python setup_picalc_pyx_omp.py build_ext -fi

ext_modules = [
    Extension(
        "picalc_pyx_omp",
        ["picalc_pyx_omp.pyx"],
        extra_compile_args=['-fopenmp','-I/Library/Developer/CommandLineTools/SDKs/MacOSX14.2.sdk/usr/include/'],
        extra_link_args=['-lgomp', '-Wl,-rpath,/opt/homebrew/opt/gcc/lib/gcc/current/','-L/Library/Developer/CommandLineTools/SDKs/MacOSX14.2.sdk/usr/lib/']
    )
]

setup(name="picalc_pyx_omp",
      ext_modules=cythonize(ext_modules))

