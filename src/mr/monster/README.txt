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

:scheme:
    The URI scheme to use in the virtual host, by default this is detected automatically.

:host:
    Set the canonical hostname to pass to Zope. If used you must provide a port.
    
:port:
    Set the canonical port.  If used you must provide a host.

:internal:
    A path in the form `/foo/site` that is the base of your application in Zope.

:external:
    A path in the form `/bar/baz` to filter from a request using _vh_bar syntax.

:drop:
    A path in the form `/foo/bar` which will be dropped from the beginning of all
    request paths.  Use in conjunction with ``external`` when there is no upstream proxy
    or it doesn't remove the _vh_ elements automatically.

:passthrough:
    If `true` this will cause mr.monster to ignore requests which already have virtualhost
    declarations.  This is useful when the same configuration is used in development and
    production, but the production proxy (such as Apache) already adds the declarations. Off 
    by default.