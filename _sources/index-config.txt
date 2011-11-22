.. _index-config:

Index Configuration
===================

Downloading / Installing packages *from* the index
--------------------------------------------------

.. note:: The mypi index-urls all begin with ``/simple``

pip config file
~~~~~~~~~~~~~~~

The pip config file is locate in ``~/.pip/pip.conf`` (See `the pip docs`_ for
more details).

Example::

    [global]
    timeout = 60
    extra-index-url = http://path/to/your/mypi/install/simple

.. note:: Using ``extra-index-url`` adds a URL to the search. Using
          ``index-url`` will *replace* the search list!

pip command-line
~~~~~~~~~~~~~~~~

With ``pip`` you can specify an index URL directly on the command line::

    pip install --extra-index-url http://path/to/your/index/simple yourpackage

or, if you want to completely override pypi::

    pip install -i http://path/to/your/index/simple yourpackage


Parsing requirements (pip)
~~~~~~~~~~~~~~~~~~~~~~~~~~

It's also possible to define your index-urls for package requirements. You can
either use the ``setuptools`` option inside ``setup.py``::

    setup(...
        dependency_links = ["http://path/to/mypi/simple/<yourpackage>"],
         )

or, you can add the ``index-url``/``extra-index-url`` to your
``requirements.txt`` file. See the `pip requirements`_ page for more info.

easy_install
~~~~~~~~~~~~

``easy_install`` is "the old way" of installing packages. It also allows you
to specify and ``index-url``. See the `easy_install docs`_ for more info.

Uploading packages to your index
--------------------------------

To upload packages to pypi, you first need to register your package::

    python setup.py register

Next you can upload files to the index::

    python setup.py sdist upload # uploads a source distribution

In order to upload to your private index, you first need to edit ``~/.pypirc``
to define your index. Here's an example::

    [distutils]
    index-servers =
        myindex
        my2ndindex

    [myindex]
    repository: http://pyrepo:8080

    [my2ndindex]
    repository: http://pyrepo/mypi


Then you can upload like so::

    python setup.py register -r myindex
    python setup.py sdist upload -r myindex

.. _the pip docs: http://www.pip-installer.org/en/latest/configuration.html
.. _pip requirements: http://www.pip-installer.org/en/latest/requirements.html
.. _easy_install docs: http://packages.python.org/distribute/easy_install.html#configuration-files
