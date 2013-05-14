
def RewriteFactory(global_config, **local_conf):

    if 'port' in local_conf and not 'host' in local_conf:
        raise AttributeError("Host must be specified to use port")

    if 'host' in local_conf and 'port' not in local_conf:
        raise AttributeError("Port must be specified to use host")


    # BBB: Removed the 'path' from internal and external
    for old in ['internalpath','externalpath']:
        if old in local_conf:
            local_conf[old[:-4]] = local_conf[old]
            del local_conf[old]

    # Autodetect is implied now (we fill in anything you don't specify)
    if 'autodetect' in local_conf:
        del local_conf['autodetect']
    
    def factory(app):
        return RewriteMiddleware(app, **local_conf)
    return factory

class RewriteMiddleware(object):
    """ Rewriting middleware which allows adding VHM path elements """
    
    def __init__(self, app, host=None, 
                            port=None, 
                            scheme=None,
                            internal='', 
                            external=''):
        
        # This is the WSGI app we wrap
        self.app = app

        # Clean up the specified internal path
        internal = internal.strip('/')
        if internal:
            internal = "/%s" % internal

        # Clean up the specified external path
        clean_external = []
        for element in external.split('/'):
            if element:
                element = "_vh_%s" % element
            clean_external.append(element)
        external = "/".join(clean_external)
        
        # Externals aren't allowed to end with a slash as the path
        # is guaranteed to start with one (or be empty)
        external = external.rstrip('/')
        
        # Build our overrides, to precompute the pattern
        overrides = {'scheme':scheme or '%(scheme)s',
                     'host':host or '%(host)s',
                     'port':port or '%(port)s',
                     'internal':internal,
                     'external':external}

        # Build the pattern
        self.pattern = "/VirtualHostBase/%(scheme)s/%(host)s:%(port)s%(internal)s/VirtualHostRoot%(external)s%%(path)s" % overrides


    def __call__(self, environ, start_response):
        
        # Look up the scheme
        scheme = environ.get('wsgi_url_scheme','http')

        # Lookup host and port
        host = environ.get('HTTP_HOST','')
        port = "80"
        if ':' in host:
            host,port = host.rsplit(':',1)

        # Fallback host and port for non HTTP/1.1 clients
        if not host:
            host = environ.get('SERVER_NAME')
            port = environ.get('SERVER_PORT',"80")
        
        # Rebuild the path
        path = "%s%s" % (environ.get('SCRIPT_NAME',''),environ.get('PATH_INFO',''))

        options = {'scheme':scheme,
                   'host':host,
                   'port':port,
                   'path':path}

        # Clobber SCRIPT_NAME to prevent any downstream 
        # middlewares from incorrectly regenerating URLs.
        environ['SCRIPT_NAME'] = None
        
        # Overwrite PATH_INFO with our new url
        environ['PATH_INFO'] = self.pattern % options
        
        # And we're done, don't try and wrap the response
        # so any iterables are appropriately passed through
        return self.app(environ,start_response)