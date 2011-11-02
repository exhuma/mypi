from setuptools import setup, find_packages

PACKAGE = "mypi"
NAME = "mypi"
DESCRIPTION = "Private Python Package Index"
AUTHOR = "Michel Albert"
AUTHOR_EMAIL = "michel@albert.lu"
VERSION = __import__(PACKAGE).__version__

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=open("README.rst").read(),
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license="GPL",
    install_requires = [
      'Flask==0.8',
      'sqlalchemy-migrate==0.7.2',
      'SQLAlchemy==0.7.3'
      ],
    packages=find_packages(exclude=["tests.*", "tests"]),
    zip_safe=False,
)
