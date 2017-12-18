import simplejson
import datetime
import os
import hashlib
import cgi

from twisted.web import server, resource
from twisted.application import internet
from twisted.web.server import Site, GzipEncoderFactory
from twisted.web.resource import Resource, EncodingResourceWrapper, ForbiddenResource
from twisted.web.util import Redirect, redirectTo
from twisted.python import log
from jinja2 import Environment, FileSystemLoader
import subprocess

from tokens import Canarytoken
from canarydrop import Canarydrop
from channel import InputChannel
from queries import get_canarydrop, add_canarydrop_hit, add_additional_info_to_hit
from constants import INPUT_CHANNEL_HTTP
from settings import TOKEN_RETURN, MAX_UPLOAD_SIZE, WEB_IMAGE_UPLOAD_PATH

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
            if request.args.get('ts_key',[None])[0]:
                canarydrop._drop['hit_time'] = request.args.get('ts_key', [None])[0]
            else:
                canarydrop._drop['hit_time'] = datetime.datetime.utcnow().strftime("%s.%f")
            useragent = request.getHeader('User-Agent')
            src_ip    = request.getHeader('x-forwarded-for')

            #location and refere are for cloned sites
            location  = request.args.get('l', [None])[0]
            referer   = request.args.get('r', [None])[0]
            self.dispatch(canarydrop=canarydrop, src_ip=src_ip,
                          useragent=useragent, location=location,
                          referer=referer)
            
            print dir(canarydrop)
            print vars(canarydrop)
            if 'redirect_url' in canarydrop._drop and canarydrop._drop['redirect_url']:
                # if fast redirect
                if canarydrop._drop['type'] == 'fast_redirect':
                    return redirectTo(canarydrop._drop['redirect_url'], request)
                    #template = env.get_template('browser_scanner.html')
                    #return template.render(key=canarydrop._drop['hit_time'],
                    #                       canarytoken=token.value()).encode('utf8')
                elif canarydrop._drop['type'] == 'slow_redirect':
                    template = env.get_template('browser_scanner.html')
                    return template.render(key=canarydrop._drop['hit_time'],
                                           canarytoken=token.value(),
                                           redirect_url=canarydrop._drop['redirect_url']).encode('utf8')

            if request.getHeader('Accept') and "text/html" in request.getHeader('Accept'):
                if canarydrop['browser_scanner_enabled']:
                    template = env.get_template('browser_scanner.html')
                    return template.render(key=canarydrop._drop['hit_time'],
                                           canarytoken=token.value(),
                                           redirect_url='').encode('utf8')

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
            canarydrop = Canarydrop(**get_canarydrop(canarytoken=token.value()))
            #if key and token args are present, we are either:
            #    -posting browser info
            #    -getting an aws trigger (key == aws_s3)
            #store the info and don't re-render
            if key and token:
                if key == 'aws_s3':
                    try:
                        canarydrop._drop['hit_time'] = datetime.datetime.utcnow().strftime("%s.%f")
                        src_ip    = request.args['RemoteIP'][0]
                        additional_info = {'AWS Log Data': {k:v for k,v in request.args.iteritems() if k not in ['key','src_ip']}}
                        self.dispatch(canarydrop=canarydrop, src_ip=src_ip,
                                      additional_info=additional_info)
                    except Exception as e:
                        log.err('Error in s3 post: {error}'.format(error=e))
                elif 'secretkeeper_photo' in request.args:
                    log.err('Saving secretkeeper_photo')
                    try:
                        fields = cgi.FieldStorage(
                            fp = request.content,
                            headers = request.getAllHeaders(),
                            environ = {'REQUEST_METHOD':'POST',
                            'CONTENT_TYPE': request.getAllHeaders()['content-type'],
                            }
                        )#hacky way to parse out file contents and filenames
                        filename = fields['secretkeeper_photo'].filename
                        filebody = fields['secretkeeper_photo'].value

                        if len(filebody) > MAX_UPLOAD_SIZE:
                            raise Exception('File too large')

                        r = hashlib.md5(os.urandom(32)).hexdigest()
                        filepath = os.path.join(WEB_IMAGE_UPLOAD_PATH,
                                            r[:2],
                                            r[2:])+'.png'
                        if not os.path.exists(os.path.dirname(filepath)):
                            try:
                                os.makedirs(os.path.dirname(filepath))
                            except OSError as exc: # Guard against race condition
                                if exc.errno != errno.EEXIST:
                                    raise

                        with open(filepath, "w") as f:
                            f.write(filebody)

                        canarydrop.add_additional_info_to_hit(hit_time=key, additional_info={'secretkeeper_photo':filepath})
                    except Exception as e:
                        log.err('Error in secretkeeper_photo post: {error}'.format(error=e))
                else:
                    additional_info = {k:v for k,v in request.args.iteritems() if k not in ['key','canarytoken','name']}
                    canarydrop.add_additional_info_to_hit(hit_time=key,additional_info={request.args['name'][0]:additional_info})
                return 'success'
            else:
                return self.render_GET(request)
        except Exception as e:
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
