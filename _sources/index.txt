.. mypi documentation master file, created by
   sphinx-quickstart on Tue Nov 22 13:13:02 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to mypi's documentation!
================================

.. Contents:
   .. toctree::
      :maxdepth: 2

mypi is a "personal" package index for Python packages. By default, it's
possible to publish packages to the main python package index (the
"cheeseshop"). But this list is public by default. Sometimes you cannot or
don't want to put packages on the public index. This is what mypi is for.

Here are some situations where this may be true:

- Your company does not allow publishing of your work, or you are bound to a
  NDA. In either case, you cannot legally upload packages to pypi.

- You would like to have an "incubator". A place where you can publish
  work-in-progress without the risk of breaking existing installs. As an
  example, a user could use ``pip install yourpackage``, which will use pypi
  by default. here you would only have the stable releases available. If
  someone wants to live on the edge, s/he could simply run ``pip install -i
  http://your-mypi-host yourpackage`` to get the latest release from your
  private index.

But why would you even want to bother with a package index at all. The main
reasons are:

- You want a central authoritative repository for all deployed applications,
  without publishing to the world.

- You want to be able to use ``pip`` to install packages

  When typing ``pip install yourpackage`` it will search a specific package
  index (by default ``pypi.python.org``) for ``yourpackage``. If found, it
  will try to find the newest release (unless otherwise specified), download
  and install it.

  So if your package is not published on pypi, you won't be able to use
  ``pip``. With mypi, this is now possible.

- You want to be able to add your *private* packages to package dependencies.

  Similar to the ``pip`` command, package dependencies rely on an
  authoritative site like pypi to be able to search for the packages. If your
  packages are registered on mypi, dependency retrievel will be automatic.

Usage
=====

In order to use a custom package index in python, you need to configure
``pip``, ``easy_install`` and ``python`` as needed.

See :ref:`index-config` for more details.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

