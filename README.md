AdminSMS
========

**Author: Genilson Israel da Silva**
**Date: 16/10/2012**

Run commands remotely through SMS messages
------------------------------------------

> AdminSMS is a daemon utility that listens to events from a phone connected to
the host and runs commands received through SMS messages.


More information
================

> The html documentation can be found in doc/index.html


Feedback and bug reports
========================

> Feedbacks are welcome, please send emails to genilsonisrael[at]gmail[dot]com


Dependencies
------------
	
> For some reason python-gammu <http://wammu.eu/python-gammu/> can't be
installed through python package manager (pip), so you will need to install
it manually.


Usage
-----

> You can use the params start, stop and status to interact with the daemon.
Don't forget to edit settings.py before starting the daemon or you
will have to stop and start it again for the configuration to be effective.

>`python adminsms start`

>`python adminsms stop`

>`python adminsms status`