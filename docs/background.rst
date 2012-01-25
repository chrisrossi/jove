==========================
Background and Motivations
==========================

The KARL project (open source collaboration system built atop Pyramid)
had an operational need. We wanted to lower the cost/effort needed to
host lots of smaller KARL sites. They couldn't justify their own server
or VM. In fact, they couldn't justify their own Python process.

Besides computing resources, we were concerned about sysadmin time.
Doing software production updates on a number of customers was not
attractive. But having different customers with different versions of
software was not sustainable. We wanted a less labor-intensive way to
manage a potentially large number of medium-to-small KARL sites.

That is, we wanted a "Multi-KARL". That is, a single Python process with
a single pile of KARL software, but with multiple KARL "sites". With
this, the incremental human/hardware costs of adding and maintaining a
new KARL site was reduced.

In our first pass, Chris Rossi created "karlserve", then refactored into
and replaced by Jove.
