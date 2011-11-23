Private Python Package Index
============================

This application provides a private package index. Sometimes you want to be
able to ``easy_install``/``pip install`` your packages without putting them on
``pypi``. The reasons for this can vary. Maybe you package is not "ripe"
enough to release it into the wild, or, you may be working on
proprietary/closed code.

If you need this, you are required to do two things:

#. You need to make the packages available somewhere, where
   ``setuptools``/``distribute`` can find them.
#. You need to dpecify this location in your ``setup.py`` script using
   ``dependency_links``

Adding the ``dependency_links`` information is easy. But "publishing" your
packages can be more cumbersome. You have to manually upload the packages to a
reachable location, and make the packages discoverable via HTTP (using
``httpd`` for example).

This is how I got started. I used ``scp`` to upload the packages, and put them
into a folder which was published by ``httpd``.

You could automate this step using a third-party tool like ``fabric``. This
was my next choice. And it works well.

But ``python`` is perfectly able to solve all this using ``setup.py`` with a
custom ``~/.pypirc``. Once set up, the only thing you need to do is to run::

    python setup.py register -r local
    python setup.py sdist upload -r local

Example ``~/.pypirc``::

    [local]
    repository: http://my.installed.mypi.instance
    username: user
    password: passwd

.. note:: Currently, authentication is not yet implemented. So
          username/password will be ignored.

Uploading your packages like this just "feels right". Additionally, it
encourages you to keep your metadata inside ``setup.py`` up-to-date.

Usage
-----

Once this application is installed, it will be possible to list your published
packages using the URL you configured during installation.

Also, if you added a section in you pypirc, you can easily upload packages
using::

    python setup.py register -r local
    python setup.py sdist upload -r local

In this case, ``local`` is the repository name configured in your ``.pypirc``.

Installation (mod_wsgi)
-----------------------

see INSTALL.rst

Development
-----------

The database is versioned using ``sqlalchemy-migrate``. Be sure to read up on
this before you make changes to the schema.

.. important:: It turned out that certain schema modifications are not working
               well with SQLite. For this reason, sqlalchemt-migrate is
               currently not being used to it's fullest extent. It's primarily
               used to create the database. New installations should
               re-create the database from scratch. I know that this is far
               from perfect. But so far I only tested with SQLite. If new
               migrations are added which require a DB recycle, I will note
               this in the installation docs!

