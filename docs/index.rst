.. mypi documentation master file, created by
   sphinx-quickstart on Tue Nov 22 13:13:02 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to mypi's documentation!
================================

**Project state / Risk assessment**
    First "public" release. Tested only *very* roughly. But as this is hardly
    a mission-critical service, using it is not very risky.

    Worst case scenario if thins break: You lose the index and automtic
    installation won't work anymore. Assuming you keep your package sources
    around, you'll be safe.

    Note that this is *currently* not meant to be a persistent storage for
    your packages. If the project evolves (specifically the database and
    database migrations), this may change.

For the impatient:
------------------

To get started the only two pieces of information you need is the
installation, and configuration. Here you go:

.. toctree::
   :maxdepth: 2

   install
   index-config

What is mypi?
-------------

mypi is a "personal" package index for Python packages. By default, it's
possible to publish packages to `the main python package`_ index (a.k.a.
"cheeseshop"). But this list is *public* by default. Sometimes you cannot or
don't want to put packages on the public index. This is what mypi is for.

Here are some situations where this may be true:

- Your company does not allow publishing of your work, or you are bound to an
  NDA. In either case, you cannot legally upload packages to pypi.

- You would like to have an "incubator". A place where you can publish
  work-in-progress without the risk of breaking existing installs. As an
  example, a user could use ``pip install yourpackage``, which will use pypi
  by default. Here you would only make the stable releases available. If
  someone wants to live on the edge, s/he could simply run ``pip install -i
  http://your-mypi-host yourpackage`` to get the latest release from your
  incubator/private index.

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
  ``pip``. With mypi, this is possible.

- You want to be able to add your *private* packages to package dependencies.

  Similar to the ``pip`` command, package dependencies rely on an
  authoritative site like pypi to be able to search for the packages. If your
  packages are registered on mypi, dependency retrievel will be automatic.

Alternatives
------------

A simple indexable web-folder
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The python package managers (``pip``, ``easy_install``) both allow you to
specify URLs where you can package releases. They simply open these URLs and
search for links matching package names.

Advantages
""""""""""

- *Very* easy to set-up. Simply create a folder on the web-server and make it
  indexable. Done!

Disadvantages
"""""""""""""

- Package maintainers need write access to this folder.

- Auto-discovery does not work (as far as I know! Please correct me if I'm
  wrong). This means you won't be able to do ``pip install yourpackage``, but
  dependency resolution would still work in case of ``python setup.py
  install``.

djangopypi / chishop
~~~~~~~~~~~~~~~~~~~~

`djangopypi`_ actually is implementing pretty much the same ideas as mypi. So
instead of listing advantages/disadvantages, I am only going to list the major
differences:

- As the name implies, djangopypi is based on django. As such, you need
  experience in django to set it up. mypi on the other hand is based on Flask.
  As such, when installing mypi, you won't need to know *anything* in
  particular. After installation you will have a default WSGI application
  available which is deployable pretty much anywhere.

- django *requires* user's to log in. See :ref:`designdecisions` for more
  details.

.. _designdecisions:

Design Decisions
----------------

To give you an idea what this project is about, i'll list my decisions for
this project including their "state".

mypi should:

- ... be easy to install [**good enough for now** (could be improved)]

- ... run in a virtualenv [**works**]

- ... be well documented [**should be okay** (you're reading it...)]

- ... make it possible for package maintainers to upload packages via ``python
  setup.py sdist upload`` [**OK**]

- ... allow ``easy_install my_package`` or ``pip install my_package``.
  [**OK**] (see :ref:`index-config`)

- ... not necessarily require logins/passwords when uploading. This could be
  added later on but is not of biggest importance.

  **Rationale:** In our current environment network access is restricted using
  a firewall. So authentication is not strictly necessary. This is
  dogfood-ware. I am writing this for myself, and I am practising YAGNI. If I
  see that there is a real demand for this feature, and if I find the spare
  time, I might go ahead and implement it. For now, it's of no high importance
  though.

  .. note:: For people that *need* this, this chould *in theory* be solved
            with WSGI middleware if really required until it's built-in.

            As a starting point:
            http://stackoverflow.com/questions/723856/wsgi-authentication-homegrown-authkit-openid


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


.. _the main python package: http://pypi.python.org
.. _djangopypi: http://pypi.python.org/pypi/djangopypi
