===
FAQ
===

Does Jove use traversal to get to the app?
------------------------------------------

While it may look like it, no, it doesn't. Basically, Jove has a webapp
whose only job is to figure out which site a request is bound for and
then call the site's wsgi_app to handle the request. There are a few
ways Jove can figure out which site to use.

Can I use virtual hosting to point at a site?
---------------------------------------------

You can use a full-URL to point at the site you want. Or you can use a
virtual host for the site and the HOST header can match.

What exists above each site?
----------------------------

Zero or one site can be configured as the root and be served at
``/`` without a virtual host. This could be used to implement an admin
tool for listing/managing sites.

Is this ZODB-only?
------------------

Yup, first sentence in docs say so.

