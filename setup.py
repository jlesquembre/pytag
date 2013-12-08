from setuptools import setup
import os

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst'), 'rt') as f:
    README = f.read()

version = '0.1.4'

setup(name='pytag',
      version=version,
      author='José Luis Lafuente',
      author_email='jlesquembre@gmail.com',
      description='A library to handle audio metadata',
      long_description=README,
      license='GNU General Public License v3 (GPLv3)',
      url='http://jlesquembre.github.io/pytag/',
      packages=['pytag'],
      install_requires=['filemagic'],
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Topic :: Multimedia :: Sound/Audio',
        'Topic :: Utilities',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.3',
        ],
      keywords=['audio', 'metadata'],
    )
