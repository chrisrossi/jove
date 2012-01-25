.. Jove documentation master file, created by
   sphinx-quickstart on Tue Jul 19 09:16:21 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Jove Application Server
=======================

`Jove` is an application server and site manager for `Pyramid` web
applications that use `ZODB`. With Jove you can have multiple "sites"
in one Python process, sharing a common code base,
but each having independent:

- Pyramid registry

- Database connection

- Persistent configuration settings

- ``var`` directory for data

Under Jove, each "site" thinks it is a WSGI application. Jove simply
acts as a router that calls the appropriate site.

Contents:

.. toctree::
   :maxdepth: 1

   background.rst
   site.rst
   application.rst
   settings.rst
   service.rst
   faq.rst

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

