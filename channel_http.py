import simplejson
import datetime
import os
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
from queries import get_canarydrop, add_additional_info_to_hit
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
        #A GET request to a token URL can trigger one of a few responses:
        # 1. Check if link has been clicked on (rather than loaded from an
        #    <img>) by looking at the Accept header, then:
        #  1a. If browser security if enabled, serve that page and stop.
        #  1b. If fortune in enabled, serve a fortune and stop.
        # 2. Otherwise we'll serve an image:
        #  2a. If a custom image is attached to the canarydrop, serve that and stop.
        #  2b. Serve our default 1x1 gif

        request.setHeader("Server", "Apache")

        try:
            token = Canarytoken(value=request.path)
            canarydrop = Canarydrop(**get_canarydrop(canarytoken=token.value()))
            canarydrop._drop['hit_time'] = datetime.datetime.utcnow().strftime("%s.%f")
            useragent = request.getHeader('User-Agent')
            src_ip    = request.getHeader('x-forwarded-for')

            #location and refere are for cloned sites
            location  = request.args.get('l', [None])[0]
            referer   = request.args.get('r', [None])[0]
            self.dispatch(canarydrop=canarydrop, src_ip=src_ip,
                          useragent=useragent, location=location,
                          referer=referer)

            if "text/html" in request.getHeader('Accept'):
                if canarydrop['browser_scanner_enabled']:
                    template = env.get_template('browser_scanner.html')
                    return template.render(key=canarydrop._drop['hit_time'],
                                           canarytoken=token.value()).encode('utf8')

                elif TOKEN_RETURN == 'fortune':
                    try:
                        fortune = subprocess.check_output('/usr/games/fortune')
                        template = env.get_template('fortune.html')
                        return template.render(fortune=fortune).encode('utf8')
                    except Exception as e:
                        log.err('Could not get a fortune: {e}'.format(e=e))

            if canarydrop['web_image_enabled'] and os.path.exists(canarydrop['web_image_path']):
                mimetype = "image/"+canarydrop['web_image_path'][-3:]
                with open(canarydrop['web_image_path'], "r") as f:
                    contents = f.read()
                request.setHeader("Content-Type", mimetype)
                return contents

        except Exception as e:
            log.err('Error in render GET: {error}'.format(error=e))

        request.setHeader("Content-Type", "image/gif")
        return self.GIF

    def render_POST(self, request):
        try:
            key = request.args['key'][0]
            token = Canarytoken(value=request.path)
            #if key and token args are present, we are either:
            #    -posting browser info
            #    -getting an aws trigger (key == aws_s3)
            #store the info and don't re-render
            if key and token:
                if key == 'aws_s3':
                    try:
                        canarydrop = Canarydrop(**get_canarydrop(canarytoken=token.value()))
                        canarydrop._drop['hit_time'] = datetime.datetime.utcnow().strftime("%s.%f")
                        src_ip    = request.args['RemoteIP'][0]
                        additional_info = {k:v for k,v in request.args.iteritems() if k not in ['key','src_ip']}
                        self.dispatch(canarydrop=canarydrop, src_ip=src_ip,
                                      additional_info=additional_info)
                    except Exception as e:
                        log.err('Error in s3 post: {error}'.format(error=e))
                else:
                    additional_info = {k:v for k,v in request.args.iteritems() if k not in ['key','canarytoken','name']}
                    add_additional_info_to_hit(token.value(),key,{request.args['name'][0]:additional_info})
                return 'success'
            else:
                return self.render_GET(request)
        except:
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
