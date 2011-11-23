from setuptools import setup, find_packages
from setuptools.command.install import install
from os.path import join
from sys import prefix
import os

PACKAGE = "mypi"
NAME = "mypi"
DESCRIPTION = "Private Python Package Index"
AUTHOR = "Michel Albert"
AUTHOR_EMAIL = "michel@albert.lu"
VERSION = __import__(PACKAGE).__version__

def get_data_files(root, prefix=None) :
    """
    Returns a list readily formed for the ``data_files`` parameter in
    ``setup``.

    prefix
        prefix all target folders with this value
    """
    out = []
    for path, dirs, files in os.walk('db_repo'):

        if prefix:
            tgt_path = join(prefix, path)
        else:
            tgt_path = path

        out.append((tgt_path, [join(path, _) for _ in files]))
    return out

db_repo_files = get_data_files('db_repo', prefix=join(prefix,
    'usr/share/docs/mypi'))

class MypiInstall(install):
    def run(self):
        install.run(self)
        # TODO: ask the user for WSGI and DB settings
        pass

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=open("README.rst").read(),
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license="GPL",
    include_package_data=True,
    install_requires = [
      'Flask==0.8',
      'sqlalchemy-migrate==0.7.2',
      'SQLAlchemy==0.7.3'
      ],
    packages=find_packages(exclude=["tests.*", "tests"]),
    data_files=[
        (join(prefix,'usr/share/docs/mypi/examples'),
        ['mod_wsgi/app.wsgi', 'mod_wsgi/example.apache.conf']),
        ] + db_repo_files,
    cmdclass={'install': MypiInstall},
    zip_safe=False,
)

