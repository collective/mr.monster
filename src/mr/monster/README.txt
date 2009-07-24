Mr Monster
==========

**He's fearsome.**

About
-----

Mr Monster is a WSGI middleware designed to make it easy to locally test
pipelines that will eventually be served behind apache with a rewrite rule in
place.

The configuration is very simple, the easiest case being::

    [filter:monster]
    use = egg:mr.monster#rewrite
    autodetect = true

which simply adds the correct VirtualHostBase/Root declarations.

Options
-------

:autodetect:
    Pick a host and port from the inbound request

:host:
    Set the canonical hostname to pass to Zope. If used you must provide a port.
    
:port:
    Set the canonical port.  If used you must provide a host.

:internalpath:
    A path in the form `/foo/site` that is the base of your application in Zope.

:externalpath:
    A path in the form `/bar/baz` to filter from a request using _vh_bar syntax.
