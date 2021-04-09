from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

'''
setup(
	cmdclass = {'build_ext': build_ext},
	ext_modules = [Extension("odestuff", ["odestuff.pyx"])]
)
'''

from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

ext_modules=[ Extension("odestuff", ["odestuff.pyx"], libraries=["m"], extra_compile_args = ["-ffast-math"])]

setup(name = "odestyff",cmdclass = {"build_ext": build_ext},ext_modules = ext_modules)

# compile in terminal:  python setupodestuff_full.py build_ext --inplace
