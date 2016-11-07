from distutils.core import setup
from distutils.sysconfig import get_python_lib

setup(
    name='PILcompat',
    description='PIL compatibility hack',
    packages=['PILcompat'],
    author='Ubuntu Developers',
    author_email='ubuntu-devel-discuss@lists.ubuntu.com',
    data_files=[(get_python_lib(), ['PILcompat.pth'])],
    )
