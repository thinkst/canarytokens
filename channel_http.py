import simplejson
from twisted.web import server, resource
from twisted.application import internet
from twisted.web.server import Site, GzipEncoderFactory
from twisted.web.resource import Resource, EncodingResourceWrapper, ForbiddenResource
from twisted.web.util import Redirect
from twisted.python import log
from jinja2 import Environment, FileSystemLoader
import subprocess

from tokens import Canarytoken
from canarydrop import Canarydrop
from channel import InputChannel
from queries import get_canarydrop
from constants import INPUT_CHANNEL_HTTP
from settings import TOKEN_RETURN

env = Environment(loader=FileSystemLoader('templates'))

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
        accept_html = accept_images = False

        try:
            token = Canarytoken(value=request.path)
            canarydrop = Canarydrop(**get_canarydrop(canarytoken=token.value()))
            useragent = request.getHeader('User-Agent')
            src_ip    = request.getHeader('x-forwarded-for')

            #location and refere are for cloned sites
            location  = request.args.get('l', [None])[0]
            referer   = request.args.get('r', [None])[0]

            self.dispatch(canarydrop=canarydrop, src_ip=src_ip,
                          useragent=useragent, location=location,
                          referer=referer)

            accept = request.getHeader('Accept')
            if accept:
                if "text/html" in accept:
                    accept_html = True
                if "images/*" in accept:
                    accept_images = True

        except:
            log.err('No canarytoken seen in: {path}'.format(path=request.path))

        request.setHeader("Server",       "Apache")
        if accept_html and TOKEN_RETURN == 'fortune':
            try:
                fortune = subprocess.check_output('/usr/games/fortune')
                template = env.get_template('fortune.html')
                return template.render(fortune=fortune).encode('utf8')
            except Exception as e:
                log.err('Could not get a fortune: {e}'.format(e=e))

        request.setHeader("Content-Type", "image/gif")
        return self.GIF

    def render_POST(self, request):
        return self.render_GET(request)

    def format_additional_data(self, **kwargs):
        log.msg('%r' % kwargs)
        additional_report = ''
        if kwargs.has_key('src_ip') and kwargs['src_ip']:
            additional_report += 'Source IP: {ip}'.format(ip=kwargs['src_ip'])
        if kwargs.has_key('useragent') and kwargs['useragent']:
            additional_report += '\nUser-agent: {useragent}'.format(useragent=kwargs['useragent'])
        if kwargs.has_key('location') and kwargs['location']:
            additional_report += '\nCloned site is at: {location}'.format(location=kwargs['location'])
        if kwargs.has_key('referer') and kwargs['referer']:
            additional_report += '\nReferring site: {referer}'.format(referer=kwargs['referer'])
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
