from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize
import numpy

ext_modules = [
    Extension(
        "picalc_pyx1",
        ["picalc_pyx1.pyx"],
        extra_compile_args=['-fopenmp','-I/Library/Developer/CommandLineTools/SDKs/MacOSX12.3.sdk/usr/include/'],
        extra_link_args=['-lgomp', '-Wl,-rpath,/opt/homebrew/opt/gcc/lib/gcc/current/','-L/Library/Developer/CommandLineTools/SDKs/MacOSX12.3.sdk/usr/lib/'])
]

setup(name="picalc_pyx1",include_dirs=[numpy.get_include()],
      ext_modules=cythonize(ext_modules))

