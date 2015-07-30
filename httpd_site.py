import simplejson

from twisted.web import server, resource
from twisted.application import internet
from twisted.web.server import Site, GzipEncoderFactory
from twisted.web.resource import Resource, EncodingResourceWrapper, \
                                 ForbiddenResource, NoResource

from twisted.web.util import Redirect
from twisted.python import log
from jinja2 import Environment, FileSystemLoader

from tokens import Canarytoken
from canarydrop import Canarydrop
from queries import save_canarydrop, save_imgur_token, get_canarydrop,\
                    create_linkedin_account, create_bitcoin_account,\
                    get_linkedin_account, get_bitcoin_account
from exception import NoCanarytokenPresent
from ziplib import make_canary_zip
from msword import make_canary_msword
from pdfgen import make_canary_pdf
import settings

env = Environment(loader=FileSystemLoader('templates'))
class GeneratorPage(resource.Resource):
    isLeaf = True

    def getChild(self, name, request):
        if name == '':
            return self
        return Resource.getChild(self, name, request)

    def render_GET(self, request):
        template = env.get_template('generate.html')
        return template.render(settings=settings).encode('utf8')


    def render_POST(self, request):
        request.responseHeaders.addRawHeader(b"content-type", b"application/json")
        response = { 'Error': None, 
                     'Url': "",
                     'Token': "",
                     'Email': "",
                     'Hostname': ""}

        try:
            try:
                email = request.args.get('email', None)[0]
            except IndexError:
                response['Error'] = 1
                raise Exception('No email supplied')
            try:
                memo  = ''.join(request.args.get('memo', None))
            except TypeError:
                response['Error'] = 2
                raise Exception('No memo supplied')

            canarytoken = Canarytoken()
            canarydrop = Canarydrop(generate=True,
                                  alert_email_enabled=True,
                                  alert_email_recipient=email,
                                  canarytoken=canarytoken.value(),
                                  memo=memo)

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
            response['Email'] = email

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
                        canarydrop.generate_random_hostname(with_random=False))
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
            return make_canary_pdf(hostname=canarydrop.get_hostname())


        return NoResource().render(request)

    def render_POST(self, request):
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

        except (TypeError, NoCanarytokenPresent):
            return NoResource().render(request)

        template = env.get_template('manage.html')
        return template.render(canarydrop=canarydrop).encode('utf8')

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
                sms_enable_status = request.args.get('sms_enable', None)[0] == "on"
            except (TypeError, IndexError):
                sms_enable_status = False

            canarydrop['alert_email_enabled'] = email_enable_status
            canarydrop['alert_sms_enabled']   = sms_enable_status

            save_canarydrop(canarydrop=canarydrop)

            template = env.get_template('manage.html')
            return template.render(canarydrop=canarydrop, saved=True,
                                        settings=settings).encode('utf8')

        except Exception as e:
            template = env.get_template('manage.html')
            return template.render(canarydrop=canarydrop, error=e, 
                                        settings=settings).encode('utf8')


class CanarytokensHttpd():
    def __init__(self, port=80):
        self.port = port

        root = Resource()
        root.putChild("", Redirect("generate"))
        root.putChild("generate", GeneratorPage())
        root.putChild("manage", ManagePage())
        root.putChild("download", DownloadPage())

        wrapped = EncodingResourceWrapper(root, [GzipEncoderFactory()])
        site = server.Site(wrapped)
        self.service = internet.TCPServer(self.port, site)
        return None
