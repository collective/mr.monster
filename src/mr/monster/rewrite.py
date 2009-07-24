from webob import Request, Response

def RewriteFactory(global_config, **local_conf):
    if "host" in local_conf:
        if "port" not in local_conf:
            raise AttributeError("You must also supply a port")
    elif "port" in local_conf:
        raise AttributeError("You must also supply a host")
    
    def factory(app):
        return RewriteMiddleware(app, **local_conf)
    return factory

class RewriteMiddleware(object):
    """An endpoint"""
    
    def __init__(self, app, host=None, 
                            port=None, 
                            internalpath='', 
                            externalpath='', 
                            autodetect=False):
        self.host = host
        self.port = port
        self.internalpath = internalpath.split("/")
        self.externalpath = externalpath.split("/")
        self.autodetect = str(autodetect).lower() == "true"
            
        self.app = app
    
    def __call__(self, environ, start_response):
        
        options = {"host": self.host, 
                   "port": self.port, 
                   "inpath":"/".join(self.internalpath),
                   "outpath":"/_vh_".join(self.externalpath)}
        
        if self.autodetect:
            options['host'] = environ['SERVER_NAME']
            options['port'] = environ['SERVER_PORT']
        
    
        if "SCRIPT_NAME" in environ:
            options['PATH_INFO'] = environ['SCRIPT_NAME']
            environ['SCRIPT_NAME'] = ''
        else:
            options['PATH_INFO'] = ''
        
        options['PATH_INFO'] += environ['PATH_INFO']

        
        format = "/VirtualHostBase/http/"   \
                 "%(host)s:%(port)s"        \
                 "%(inpath)s"              \
                 "/VirtualHostRoot"         \
                 "%(outpath)s"             \
                 "%(PATH_INFO)s"    % options
        
        if options['host'] is not None:
            environ['PATH_INFO'] = format
        
        request = Request(environ)
        response = request.get_response(self.app)
        return response(environ, start_response)