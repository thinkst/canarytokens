import simplejson
import cgi

from twisted.web import server, resource
from twisted.application import internet
from twisted.web.server import Site, GzipEncoderFactory
from twisted.web.resource import Resource, EncodingResourceWrapper, \
                                 ForbiddenResource, NoResource
from twisted.web.static import File, DirectoryLister

from twisted.web.util import Redirect
from twisted.python import log
from jinja2 import Environment, FileSystemLoader
import pyqrcode


from tokens import Canarytoken
from canarydrop import Canarydrop
from queries import save_canarydrop, save_imgur_token, get_canarydrop,\
                    create_linkedin_account, create_bitcoin_account,\
                    get_linkedin_account, get_bitcoin_account, \
                    save_clonedsite_token, get_all_canary_sites, get_canary_google_api_key,\
                    is_webhook_valid

from exception import NoCanarytokenPresent
from ziplib import make_canary_zip
from msword import make_canary_msword
from pdfgen import make_canary_pdf
from authenticode import make_canary_authenticode_binary
import settings
import datetime
import tempfile
import hashlib
import os

CLONED_SITE_JS = """
        if (document.domain != "CLONED_SITE_DOMAIN") {
            var l = location.href;
            var r = document.referrer;
            var m = new Image();
            m.src = "CANARYTOKEN_SITE/CANARYTOKEN.jpg?l=" + encodeURI(l) + "&amp;r=" + encodeURI(r);
        }
        """
env = Environment(loader=FileSystemLoader('templates'),
                  extensions=['jinja2.ext.loopcontrols'])
class GeneratorPage(resource.Resource):
    isLeaf = True

    def getChild(self, name, request):
        if name == '':
            return self
        return Resource.getChild(self, name, request)

    def render_GET(self, request):
        template = env.get_template('generate.html')
        sites_len = len(get_all_canary_sites())
        return template.render(settings=settings, sites_len=sites_len).encode('utf8')


    def render_POST(self, request):
        request.responseHeaders.addRawHeader(b"content-type", b"application/json")
        response = { 'Error': None,
                     'Url': "",
                     'Token': "",
                     'Email': "",
                     'Hostname': "",
                     'Auth': ''}
        try:
            try:
                email = request.args.get('email', None)[0]
                webhook = request.args.get('webhook', None)[0]
                if not email and not webhook:
                    response['Error'] = 1
                    raise Exception('No email/webhook supplied')
            except IndexError:
                response['Error'] = 1
                raise Exception('No email supplied')
            try:
                memo  = ''.join(request.args.get('memo', None))
                if not memo:
                    response['Error'] = 2
                    raise Exception('No memo supplied')
            except TypeError:
                response['Error'] = 2
                raise Exception('No memo supplied')

            if webhook and not is_webhook_valid(webhook):
                response['Error'] = 3
                raise Exception('Invalid webhook supplied')

            alert_email_enabled = False if not email else True
            alert_webhook_enabled = False if not webhook else True
            canarytoken = Canarytoken()

            try:
                browser_scanner = request.args['subtype'][0] == 'browserscanner'
            except:
                browser_scanner = False

            canarydrop = Canarydrop(generate=True,
                                  alert_email_enabled=alert_email_enabled,
                                  alert_email_recipient=email,
                                  alert_webhook_enabled=alert_webhook_enabled,
                                  alert_webhook_url=webhook,
                                  canarytoken=canarytoken.value(),
                                  memo=memo,
                                  browser_scanner_enabled=browser_scanner)

            if settings.TWILIO_ENABLED:
                try:
                    if not request.args['mobile'][0]:
                        raise KeyError

                    canarydrop['alert_sms_recipient'] = request.args['mobile'][0]
                    canarydrop['alert_sms_enabled'] = True
                except KeyError:
                    canarydrop['alert_sms_recipient'] = ''
                    canarydrop['alert_sms_enabled'] = False

            save_canarydrop(canarydrop)

            response['Token'] = canarytoken.value()
            response['Url'] = canarydrop.get_url()
            response['Hostname'] = canarydrop.get_hostname()
            response['Auth'] = canarydrop['auth']
            response['Email'] = email

            try:
                clonedsite = request.args['clonedsite'][0]
                if not clonedsite:
                    raise KeyError

                cloned_token = {'clonedsite': clonedsite,
                               'canarytoken': canarytoken.value()}
                canarydrop.clonedsite_token = save_clonedsite_token(cloned_token)
                save_canarydrop(canarydrop)
                response['clonedsite_js'] =  CLONED_SITE_JS\
                                    .replace('CLONED_SITE_DOMAIN', clonedsite)\
                                    .replace('CANARYTOKEN_SITE', canarydrop.get_random_site())\
                                    .replace('CANARYTOKEN', response['Token'])
                response['clonedsite'] =  clonedsite
            except (IndexError, KeyError):
                pass

            try:
                imgur_id = request.args['imgur'][0]
                if not imgur_id:
                    raise KeyError

                imgur_token = {'id': imgur_id,
                               'canarytoken': canarytoken.value()}
                canarydrop.imgur_token = save_imgur_token(imgur_token)
                save_canarydrop(canarydrop)
                response['imgur_count'] = imgur_token['count']
                response['imgur_id'] =  imgur_id
            except (IndexError, KeyError):
                pass

            try:
                linkedin_user = request.args['linkedin_user'][0]
                linkedin_password = request.args['linkedin_password'][0]
                if not linkedin_user and not linkedin_password:
                    raise KeyError

                create_linkedin_account(username=linkedin_user,
                                        password=linkedin_password,
                                        canarydrop=canarydrop)

                response['linkedin_account'] = linkedin_user
                response['linkedin_account_views'] = \
                          get_linkedin_account(username=linkedin_user)['count']
            except (IndexError, KeyError):
                pass

            try:

                bitcoin_address = request.args['bitcoin_address'][0]
                if not bitcoin_address:
                    raise KeyError

                create_bitcoin_account(address=bitcoin_address)

                btc = get_bitcoin_account(address=bitcoin_address)

                response['bitcoin_address'] = bitcoin_address
                response['bitcoin_balance'] = btc['balance']
            except (IndexError, KeyError):
                pass

            try:
                qrcode = pyqrcode.create(canarydrop.get_url()).png_as_base64_str(scale=5)
                response['qrcode_png'] = "data:image/png;base64,{qrcode}".format(qrcode=qrcode)
            except:
                pass

        except Exception as e:
            if response['Error'] is None:
                response['Error'] = 255
                log.err('Unexpected error: {err}'.format(err=e))

        return simplejson.dumps(response)

class DownloadPage(resource.Resource):
    isLeaf = True

    def getChild(self, name, request):
        if name == '':
            return self
        return Resource.getChild(self, name, request)

    def render_GET(self, request):
        try:
            token  = request.args.get('token', None)[0]
            fmt    = request.args.get('fmt', None)[0]

            canarydrop = Canarydrop(**get_canarydrop(canarytoken=token))
            if not canarydrop:
                raise NoCanarytokenPresent()

            if fmt == 'zip':
                request.setHeader("Content-Type", "application/zip")
                request.setHeader("Content-Disposition",
                                  'attachment; filename={token}.zip'\
                                  .format(token=token))
                return make_canary_zip(hostname=
                            canarydrop.get_hostname(with_random=False))
            elif fmt == 'msword':
                request.setHeader("Content-Type",
                                  "application/vnd.openxmlformats-officedocument"+\
                                                      ".wordprocessingml.document")
                request.setHeader("Content-Disposition",
                                  'attachment; filename={token}.docx'\
                                  .format(token=token))
                return make_canary_msword(url=canarydrop.get_url())
            elif fmt == 'pdf':
                request.setHeader("Content-Type", "application/pdf")
                request.setHeader("Content-Disposition",
                                  'attachment; filename={token}.pdf'\
                                  .format(token=token))
                return make_canary_pdf(hostname=canarydrop.get_hostname(nxdomain=True, with_random=False))
        except Exception as e:
            log.err('Unexpected error in download: {err}'.format(err=e))


        return NoResource().render(request)

    def render_POST(self, request):
        try:
            fields = cgi.FieldStorage(
                fp = request.content,
                headers = request.getAllHeaders(),
                environ = {'REQUEST_METHOD':'POST',
                'CONTENT_TYPE': request.getAllHeaders()['content-type'],
                }
            )#hacky way to parse out file contents and filenames

            token  = request.args.get('token', None)[0]
            fmt    = request.args.get('fmt', None)[0]
            if fmt not in ['authenticode']:
                raise Exception('Unsupported token type for POST.')

            canarydrop = Canarydrop(**get_canarydrop(canarytoken=token))
            if not canarydrop:
                raise NoCanarytokenPresent()

            if fmt == 'authenticode':
                filename = fields['file_for_signing'].filename
                filebody = fields['file_for_signing'].value
                if len(filebody) > settings.MAX_UPLOAD_SIZE:
                    raise Exception('File too large')

                if not filename.lower().endswith(('exe','dll')):
                    raise Exception('Uploaded authenticode file must be an exe or dll')
                signed_contents = make_canary_authenticode_binary(hostname=
                            canarydrop.get_hostname(with_random=False, as_url=True),
                            filebody=filebody)
                request.setHeader("Content-Type", "octet/stream")
                request.setHeader("Content-Disposition",
                                  'attachment; filename={filename}.signed'\
                                  .format(filename=filename))
                return signed_contents


        except Exception as e:
            log.err('Unexpected error in POST download: {err}'.format(err=e))
            template = env.get_template('error.html')
            return template.render(error=e.message).encode('utf8')

        return NoResource().render(request)

class ManagePage(resource.Resource):
    isLeaf = True

    def getChild(self, name, request):
        if name == '':
            return self
        return Resource.getChild(self, name, request)

    def render_GET(self, request):

        try:
            token = request.args.get('token', None)[0]
            auth  = request.args.get('auth', None)[0]
            canarydrop = Canarydrop(**get_canarydrop(canarytoken=token))
            if not canarydrop['auth'] or canarydrop['auth'] != auth:
                raise NoCanarytokenPresent()
            if canarydrop.get('triggered_list', None):
                for timestamp in canarydrop['triggered_list'].keys():
                    formatted_timestamp = datetime.datetime.fromtimestamp(
                                float(timestamp)).strftime('%Y %b %d %H:%M:%S')
                    canarydrop['triggered_list'][formatted_timestamp] = canarydrop['triggered_list'].pop(timestamp)

        except (TypeError, NoCanarytokenPresent):
            return NoResource().render(request)
        g_api_key = get_canary_google_api_key()
        template = env.get_template('manage.html')
        return template.render(canarydrop=canarydrop, API_KEY=g_api_key).encode('utf8')

    def render_POST(self, request):
        try:
            try:
                token = request.args.get('token', None)[0]
                auth  = request.args.get('auth',  None)[0]

                canarydrop = Canarydrop(**get_canarydrop(canarytoken=token))
                if not canarydrop['auth'] or canarydrop['auth'] != auth:
                    raise NoCanarytokenPresent()

            except (IndexError, NoCanarytokenPresent):
                return NoResource().render(request)

            try:
                email_enable_status = request.args.get('email_enable', None)[0] == "on"
            except (TypeError, IndexError):
                email_enable_status = False

            try:
                webhook_enable_status = request.args.get('webhook_enable', None)[0] == "on"
            except (TypeError, IndexError):
                webhook_enable_status = False

            try:
                sms_enable_status = request.args.get('sms_enable', None)[0] == "on"
            except (TypeError, IndexError):
                sms_enable_status = False

            try:
                web_image_status = request.args.get('web_image_enable', None)[0] == "on"
            except (TypeError, IndexError):
                web_image_status = False

            try:
                token_fmt = request.args.get('fmt', None)[0]
            except (TypeError, IndexError):
                token_fmt = ''

            canarydrop['alert_email_enabled'] = email_enable_status
            canarydrop['alert_webhook_enabled'] = webhook_enable_status
            canarydrop['alert_sms_enabled']   = sms_enable_status
            canarydrop['web_image_enabled']   = web_image_status

            if token_fmt == 'web_image':
                if not settings.WEB_IMAGE_UPLOAD_PATH:
                    raise Exception("Image upload not supported, set CANARY_WEB_IMAGE_UPLOAD_PATH in frontend.env.")

                fields = cgi.FieldStorage(
                    fp = request.content,
                    headers = request.getAllHeaders(),
                    environ = {'REQUEST_METHOD':'POST',
                    'CONTENT_TYPE': request.getAllHeaders()['content-type'],
                    }
                )

                filename = fields['web_image'].filename
                filebody = fields['web_image'].value

                if len(filebody) > settings.MAX_UPLOAD_SIZE:
                    raise Exception('File too large')

                if not filename.lower().endswith(('.png','.gif','.jpg')):
                    raise Exception('Uploaded image must be a PNG, GIF or JPG')
                ext = filename.lower()[-4:]

                #create a random local filename
                r = hashlib.md5(os.urandom(32)).hexdigest()
                filepath = os.path.join(settings.WEB_IMAGE_UPLOAD_PATH,
                                    r[:2],
                                    r[2:])+ext
                if not os.path.exists(os.path.dirname(filepath)):
                    try:
                        os.makedirs(os.path.dirname(filepath))
                    except OSError as exc: # Guard against race condition
                        if exc.errno != errno.EEXIST:
                            raise

                with open(filepath, "w") as f:
                    f.write(filebody)

                canarydrop['web_image_enabled'] = True
                canarydrop['web_image_path'] = filepath
            save_canarydrop(canarydrop=canarydrop)
            g_api_key = get_canary_google_api_key()
            template = env.get_template('manage.html')
            return template.render(canarydrop=canarydrop, saved=True,
                                        settings=settings, API_KEY=g_api_key).encode('utf8')

        except Exception as e:
            import traceback
            log.err('Exception in manage.html: {e}, {stack}'.format(e=e, stack=traceback.format_exc()))
            template = env.get_template('manage.html')
            return template.render(canarydrop=canarydrop, error=e,
                                        settings=settings).encode('utf8')


class LimitedFile(File):
    def directoryListing(self):
        dl = DirectoryLister(self.path,
                               [],
                               self.contentTypes,
                               self.contentEncodings,
                               self.defaultType)
        dl.template = ""
        return dl

class CanarytokensHttpd():
    def __init__(self, port=80):
        self.port = port

        root = Resource()
        root.putChild("", Redirect("generate"))
        root.putChild("generate", GeneratorPage())
        root.putChild("manage", ManagePage())
        root.putChild("download", DownloadPage())
        root.putChild("resources", LimitedFile("/srv/templates/static"))

        wrapped = EncodingResourceWrapper(root, [GzipEncoderFactory()])
        site = server.Site(wrapped)
        self.service = internet.TCPServer(self.port, site)
        return None
