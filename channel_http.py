import simplejson
from twisted.web import server, resource
from twisted.application import internet
from twisted.web.server import Site, GzipEncoderFactory
from twisted.web.resource import Resource, EncodingResourceWrapper, ForbiddenResource
from twisted.web.util import Redirect
from twisted.python import log

from tokens import Canarytoken
from canarydrop import Canarydrop
from channel import InputChannel
from queries import get_canarydrop
from constants import INPUT_CHANNEL_HTTP

class CanarytokenPage(resource.Resource, InputChannel):
    CHANNEL = INPUT_CHANNEL_HTTP
    isLeaf = True
    GIF = '\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff'+\
          '\xff\xff\xff\x21\xf9\x04\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00'+\
          '\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00\x3b' #1x1 GIF

    def getChild(self, name, request):
        if name == '':
            return self
        return Resource.getChild(self, name, request)

    def render_GET(self, request):
        try:
            token = Canarytoken(value=request.path)
            canarydrop = Canarydrop(**get_canarydrop(canarytoken=token.value()))
            useragent = request.getHeader('User-Agent')
            src_ip    = request.getHeader('x-forwarded-for')
            self.dispatch(canarydrop=canarydrop, src_ip=src_ip, 
                          useragent=useragent)
        except:
            log.err('No canarytoken seen in: {path}'.format(path=request.path))

        request.setHeader("Content-Type", "image/gif")
        request.setHeader("Server",       "Apache")
        return self.GIF

    def render_POST(self, request):
        return self.render_GET(request)

    def format_additional_data(self, **kwargs):
        log.msg('%r' % kwargs)
        if kwargs.has_key('src_ip') and kwargs['src_ip']:
            additional_report = 'Source IP : {ip}'.format(ip=kwargs['src_ip'])
        if kwargs.has_key('useragent') and kwargs['useragent']:
            additional_report += '\nUser-agent: {useragent}'.format(useragent=kwargs['useragent'])
        return additional_report

    def init(self, switchboard=None):
        InputChannel.__init__(self, switchboard=switchboard, name=self.CHANNEL)

class ChannelHTTP():
    def __init__(self, port=80, switchboard=None):
        self.port = port

        canarytoken_page = CanarytokenPage()
        canarytoken_page.init(switchboard=switchboard)
        wrapped = EncodingResourceWrapper(canarytoken_page, [GzipEncoderFactory()])
        site = server.Site(wrapped)
        self.service = internet.TCPServer(self.port, site)
        return None
