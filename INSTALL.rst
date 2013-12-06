.. note:: This document *may* be outdated. The most recent version will always
          be available at http://exhuma.github.com/mypi/

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
      cp env/usr/share/docs/mypi/examples/app.wsgi wsgi
      cd wsgi

- Prepare the database::

      ../env/bin/alembic upgrade head

- Leave the unprivileged environment::

      cd ..
      exit

- Configure apache::

      sudo cp ~mypi/env/usr/share/docs/mypi/examples/example.apache.conf \
              /etc/apache2/sites-available/mypi
      sudo ${EDITOR} /etc/apache2/sites-available/mypi
      sudo ${EDITOR} ~mypi/wsgi/app.wsgi
      sudo a2ensite mypi
      sudo a2enmod wsgi
      sudo apache2ctl -t && sudo /etc/init.d/apache2 restart

- Cleanup::

      sudo rm -rf /var/www/mypi/mypi-x.y


