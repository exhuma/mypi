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

The following will install the application in ``/var/www/mypi`` using a
non-privileged user and inside a python virtual environment. The application
will be made available under the URL ``http://your.server/mypi``. But this is
fully configurable. Two files are of particylar interest:

- ``/var/www/mypi/wsgi/app.wsgi``

  This file contains the startup code and application configuration. You are
  free to fool around in there as much as you like.

- ``/etc/apache2/sites-available/mypi``

  The apache config. Again, feel free to play around. Consult the ``mod_wsgi``
  docs for more info.

The installation procedure:

- Grab the source code. Let's assume you downloaded a ``mypi-x.y.tar.gz`` and
  stored it in ``/tmp``.

- Add a new user (security)::

      sudo useradd -m -r -d /var/www/mypi mypi

- Switch to the new user account, and do the basic installation::

      sudo -u mypi -i
      cd
      virtualenv --no-site-packages env
      tar xf /tmp/mypi-x.y.tar.gz
      cd mypi-x.y
      ../env/bin/python setup.py install
      cd ..

- Prepare the apache environment::

      mkdir wsgi
      cp mypi-x.y/mod_wsgi/app.wsgi wsgi
      cd wsgi

- Prepare the database::

      ../env/bin/migrate manage manage.py \
            --repository=../mypi-x.y/db_repo \
            --url=sqlite:///app.db
      ../env/bin/python manage.py version_control
      ../env/bin/python manage.py upgrade

- Leave the unprivileged environment::

      cd ..
      exit

- Configure apache::

      sudo cp /var/www/mypi/mypi-x.y/mod_wsgi/example.apache.conf
      /etc/apache2/sites-available/mypi
      sudo edit /etc/apache2/sites-available/mypi
      sudo a2ensite mypi
      sudo a2enmod wsgi
      sudo apache2ctl -t && sudo /etc/init.d/apache2 restart

- Cleanup::

      sudo rm -rf /var/www/mypi/mypi-x.y

Development
-----------

Note that this application currently uses a *very* naïve sqlite database. It
could use some imprevements. The database is versioned using
``sqlalchemy-migrate``. Be sure to read up on this before you make changes to
the schema. For your convenience there is a quick example ``postinst.sh``
script, which initialised the database and puts it into version-control.
