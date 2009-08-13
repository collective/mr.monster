Mr Monster
==========

**He's fearsome.**

About
-----

Mr Monster is a WSGI middleware designed to make it easy to locally test
pipelines that will eventually be served behind apache with a rewrite rule in
place.

The configuration is very simple, a common case being::

    [filter:monster]
    use = egg:mr.monster#rewrite
    host = www.example.com
    port = 80

which simply adds the correct VirtualHostBase/Root declarations.

If no configuration options are supplied the inbound request will be
introspected. To avoid this, set an explicit host and port. For users wanting to
use autodetection the ``egg:mr.monster#rewrite`` line can be added directly to a
pipeline.

Options
-------

:autodetect:
    Pick a host and port from the inbound request.

:host:
    Set the canonical hostname to pass to Zope. If used you must provide a port.
    
:port:
    Set the canonical port.  If used you must provide a host.

:internalpath:
    A path in the form `/foo/site` that is the base of your application in Zope.

:externalpath:
    A path in the form `/bar/baz` to filter from a request using _vh_bar syntax.
