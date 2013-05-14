import unittest
import logging
from mr.monster.rewrite import RewriteFactory

class UnexpectedPathException(Exception):
    pass

def PathAssertionEndpoint(expected_path_info, expected_script_name=None):
    def _(environ, start_response):

        valid = True
        if expected_script_name is not None:
            script_name = environ.get("SCRIPT_NAME")
            if script_name != expected_script_name:
                logging.error("Expected SCRIPT_NAME %s - got %s" % (expected_script_name, script_name))
                valid = False
        
        path_info = environ.get('PATH_INFO')
        if path_info != expected_path_info:
            logging.error("Expected PATH_INFO %s - got %s" % (expected_path_info,path_info))
            valid = False
        
        if not valid:
            raise UnexpectedPathException("Nope")
                
        start_response("204 No Content",[])
        
    return _
    

def dummy_start_response(status,headers):
    pass


class test_urls(unittest.TestCase):
    
    def _make_assertion_stack(self,expected_path_info,**options):
        app = PathAssertionEndpoint(expected_path_info)
        factory = RewriteFactory({},**options)
        return factory(app)

    def _catch_unexpected(self,stack,environ,message="Something went wrong"):
        try:
            stack(environ,dummy_start_response)
        except UnexpectedPathException:
            self.fail(message)


    def test_autodetect_if_no_options(self):
        stack = self._make_assertion_stack("/VirtualHostBase/http/127.0.0.1:8080/VirtualHostRoot/")
        environ = {"SERVER_NAME":"127.0.0.1",
                   "SERVER_PORT":"8080",
                   "REQUEST_METHOD":"GET",
                   "PATH_INFO":"/"}

        self._catch_unexpected(stack,environ)

    def test_fail_if_host_provided_but_not_port(self):
        self.assertRaises(AttributeError, RewriteFactory, object(), host="www.example.com")

    def test_fail_if_port_provided_but_not_host(self):
        self.assertRaises(AttributeError, RewriteFactory, object(), port="80")

    def test_legacy_options(self):
        stack = self._make_assertion_stack("/VirtualHostBase/http/127.0.0.1:8080/site/VirtualHostRoot/_vh_mysite/cheese",
                                           autodetect="true",
                                           internalpath="site",
                                           externalpath="/mysite")
        environ = {"SERVER_NAME":"127.0.0.1",
                   "SERVER_PORT":"8080",
                   "REQUEST_METHOD":"GET",
                   "PATH_INFO":"/mysite/cheese"}
        self._catch_unexpected(stack,environ)

    def test_vhm_on_host_and_port(self):
        stack = self._make_assertion_stack("/VirtualHostBase/http/www.example.com:80/VirtualHostRoot/",
                                           host="www.example.com", port="80")
        environ = {"REQUEST_METHOD":"GET",
                   "PATH_INFO":"/"}
        self._catch_unexpected(stack,environ)
    
    def test_vhm_host_autodetect_http1_1_no_port(self):
        stack = self._make_assertion_stack("/VirtualHostBase/http/www.example.com:80/VirtualHostRoot/")
        environ = {"HTTP_HOST":"www.example.com",
                   "SERVER_NAME":"127.0.0.1",
                   "SERVER_PORT":"8080",
                   "REQUEST_METHOD":"GET",
                   "PATH_INFO":"/"}
        self._catch_unexpected(stack,environ)

    def test_vhm_host_autodetect_http1_1_explicit_port(self):
        stack = self._make_assertion_stack("/VirtualHostBase/http/www.example.com:8080/VirtualHostRoot/")
        environ = {"HTTP_HOST":"www.example.com:8080",
                   "SERVER_NAME":"127.0.0.1",
                   "SERVER_PORT":"8080",
                   "REQUEST_METHOD":"GET",
                   "PATH_INFO":"/"}
        self._catch_unexpected(stack,environ)

    def test_trailing_slash_external(self):
        stack = self._make_assertion_stack("/VirtualHostBase/http/www.example.com:80/foo/VirtualHostRoot/_vh_supersite/",
                                           host="www.example.com",port="80",internal="/foo",external="/supersite/")
        environ = {"REQUEST_METHOD":"GET",
                   "PATH_INFO":"/supersite"}
        self._catch_unexpected(stack,environ)

    def test_trailing_slash_internal(self):
        stack = self._make_assertion_stack("/VirtualHostBase/http/www.example.com:80/foo/VirtualHostRoot/_vh_supersite",
                                           host="www.example.com",port="80",internal="/foo/",external="/supersite")
        environ = {"REQUEST_METHOD":"GET",
                   "PATH_INFO":"/supersite"}
        self._catch_unexpected(stack,environ)

    def test_single_slash_external(self):
        stack = self._make_assertion_stack("/VirtualHostBase/http/www.example.com:80/foo/VirtualHostRoot/",
                                           host="www.example.com",port="80",internal="/foo",external="/")

        environ = {"REQUEST_METHOD":"GET",
                   "PATH_INFO":"/"}
        self._catch_unexpected(stack,environ)
    
    def test_single_slash_internal(self):
        stack = self._make_assertion_stack("/VirtualHostBase/http/www.example.com:80/VirtualHostRoot/_vh_bar",
                                           host="www.example.com",port="80",internal="/",external="/bar")

        environ = {"REQUEST_METHOD":"GET",
                   "PATH_INFO":"/"}
        self._catch_unexpected(stack,environ)

    def test_no_external(self):
        stack = self._make_assertion_stack("/VirtualHostBase/http/www.example.com:80/foo/VirtualHostRoot/",
                                           host="www.example.com",port="80",internal="/foo")
        environ = {"REQUEST_METHOD":"GET",
                   "PATH_INFO":"/"}
        self._catch_unexpected(stack,environ)

    def test_no_internal(self):
        stack = self._make_assertion_stack("/VirtualHostBase/http/www.example.com:80/VirtualHostRoot/_vh_bar",
                                           host="www.example.com",port="80",external="/bar")
        environ = {"REQUEST_METHOD":"GET",
                   "PATH_INFO":"/"}
        self._catch_unexpected(stack,environ)

    def test_subpath(self):
        stack = self._make_assertion_stack("/VirtualHostBase/http/www.example.com:80/VirtualHostRoot/my/thing/is/cool",
                                           host="www.example.com",port="80")
        environ = {"REQUEST_METHOD":"GET",
                   "PATH_INFO":"/my/thing/is/cool"}
        self._catch_unexpected(stack,environ)

    def test_via_script(self):
        stack = self._make_assertion_stack("/VirtualHostBase/http/www.example.com:80/VirtualHostRoot/isay/my/thing/is/cool",
                                           host="www.example.com",port="80")
        environ = {"REQUEST_METHOD":"GET",
                   "SCRIPT_NAME":"/isay",
                   "PATH_INFO":"/my/thing/is/cool"}
        self._catch_unexpected(stack,environ)
    
    def test_scheme(self):
        stack = self._make_assertion_stack("/VirtualHostBase/https/www.example.com:80/VirtualHostRoot/hello",
                                           host="www.example.com",port="80",scheme="https")
        environ = {"REQUEST_METHOD":"GET",
                   "PATH_INFO":"/hello"}
        self._catch_unexpected(stack,environ)
