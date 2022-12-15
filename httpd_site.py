import base64
import simplejson
import cgi

from twisted.web import server, resource
from twisted.application import internet
from twisted.web.server import Site, GzipEncoderFactory
import twisted.web.resource
from twisted.web.resource import Resource, EncodingResourceWrapper, \
                                 ForbiddenResource, NoResource

from twisted.web.static import File, DirectoryLister, Data

from twisted.web.util import Redirect
from twisted.logger import Logger
log = Logger()
from jinja2 import Environment, FileSystemLoader
import pyqrcode


from tokens import Canarytoken
from canarydrop import Canarydrop
from queries import is_valid_email, save_canarydrop, save_imgur_token, get_canarydrop,\
                    create_linkedin_account, create_bitcoin_account,\
                    get_linkedin_account, get_bitcoin_account, \
                    save_clonedsite_token, get_all_canary_sites, get_canary_google_api_key,\
                    is_webhook_valid, get_aws_keys, get_all_canary_domains, is_email_blocked

from exception import NoCanarytokenPresent
from ziplib import make_canary_zip
from msword import make_canary_msword
from pdfgen import make_canary_pdf
from msexcel import make_canary_msexcel
from kubeconfig import get_kubeconfig
from mysql import make_canary_mysql_dump
from authenticode import make_canary_authenticode_binary
from msreg import make_canary_msreg
import settings
import datetime
import tempfile
import hashlib
import os
from cStringIO import StringIO
import csv
import wireguard as wg

env = Environment(loader=FileSystemLoader('templates'),
                  extensions=['jinja2.ext.loopcontrols'])

with open('/srv/templates/error_http.html', 'r') as f:
    twisted.web.resource.ErrorPage.template = f.read()

class GeneratorPage(resource.Resource):
    isLeaf = True

    def getChild(self, name, request):
        if name == '':
            return self
        return Resource.getChild(self, name, request)

    def render_GET(self, request):
        template = env.get_template('generate_new.html')
        sites_len = len(get_all_canary_sites())
        now = datetime.datetime.now()
        return template.render(settings=settings, sites_len=sites_len, now=now).encode('utf8')


    def render_POST(self, request):
        request.responseHeaders.addRawHeader(b"content-type", b"application/json")
        response = { 'Error': None,
                     'Error_Message': None,
                     'Url': "",
                     'Url_components': None,
                     'Token': "",
                     'Email': "",
                     'Hostname': "",
                     'Auth': ''}

        try:
            try:
                token_type = request.args.get('type', None)[0]
                if token_type not in ['web',
                                      'dns',
                                      'cmd',
                                      'web_image',
                                      'ms_word',
                                      'ms_excel',
                                      'adobe_pdf',
                                      'wireguard',
                                      'windows_dir',
                                      'clonedsite',
                                      'qr_code',
                                      'svn',
                                      'smtp',
                                      'sql_server',
                                      'my_sql',
                                      'aws_keys',
                                      'signed_exe',
                                      'fast_redirect',
                                      'slow_redirect',
                                      'kubeconfig',
                                      'log4shell']:
                    raise Exception()
            except:
                raise Exception('Unknown type')

            try:
                email = request.args.get('email', None)[0]
                webhook = request.args.get('webhook', None)[0]
                if not email and not webhook:
                    response['Error'] = 1
                    response['Error_Message'] = 'No email/webhook supplied'
                    raise Exception('No email/webhook supplied')
            except IndexError:
                response['Error'] = 1
                response['Error_Message'] = 'No email supplied'
                raise Exception('No email supplied')
            try:
                memo  = ''.join(request.args.get('memo', None))
                if not memo:
                    response['Error'] = 2
                    response['Error_Message'] = 'No memo supplied'
                    raise Exception('No memo supplied')
            except TypeError:
                response['Error'] = 2
                response['Error_Message'] = 'No memo supplied'
                raise Exception('No memo supplied')

            if webhook and not is_webhook_valid(webhook):
                response['Error'] = 3
                response['Error_Message'] = 'Invalid webhook supplied. Confirm you can POST to this URL.'
                raise Exception('Invalid webhook supplied. Confirm you can POST to this URL.')

            if email:
                if not is_valid_email(email):
                    response['Error'] = 5
                    response['Error_Message'] = 'Invalid email supplied'
                    raise Exception('Invalid email supplied')
                if is_email_blocked(email):
                    response['Error'] = 6
                    response['Error_Message'] = 'Blocked email supplied. Please see our Acceptable Use Policy at https://canarytokens.org/legal'
                    raise Exception('Blocked email supplied. Please see our Acceptable Use Policy at https://canarytokens.org/legal')

            alert_email_enabled = False if not email else True
            alert_webhook_enabled = False if not webhook else True

            if token_type != 'kubeconfig':
                canarytoken = Canarytoken()
            else:
                kubeconfig = get_kubeconfig()
                if kubeconfig is not None:
                    canarytoken = Canarytoken(value=kubeconfig[0])
                else:
                    raise Exception('Kubeconfig was not generated.')

            if token_type == "web":
                #always enable the browser scanner by default
                browser_scanner = True
            else:
                browser_scanner = False

            canarydrop = Canarydrop(type=token_type,generate=True,
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

            if token_type != "kubeconfig":
                response['Url'] = canarydrop.get_url()
                response['Hostname'] = canarydrop.get_hostname()
                response['Url_components'] = list(canarydrop.get_url_components())

            response['Token'] = canarytoken.value()
            response['Auth'] = canarydrop['auth']
            response['Email'] = email
            save_canarydrop(canarydrop)


            try:
                clonedsite = request.args['clonedsite'][0]
                if not clonedsite:
                    raise KeyError

                cloned_token = {'clonedsite': clonedsite,
                               'canarytoken': canarytoken.value()}
                canarydrop.clonedsite_token = save_clonedsite_token(cloned_token)
                canarydrop['clonedsite'] = clonedsite
                save_canarydrop(canarydrop)
                response['clonedsite_js'] =  canarydrop.get_cloned_site_javascript()
                response['clonedsite'] =  clonedsite
            except (IndexError, KeyError):
                pass

            try:
                procname = request.args['cmd_process'][0]
                if not procname:
                    raise KeyError
                
                canarydrop['cmd_process'] = procname
                canarydrop['memo'] += "\r\n\r\n(This token was created to monitor the execution of: " + procname + ")"
                save_canarydrop(canarydrop)
            except (IndexError, KeyError):
                pass


            try:
                if not request.args.get('type', None)[0] == 'qr_code':
                    raise Exception()
                response['qrcode_png'] = canarydrop.get_qrcode_data_uri_png()
            except:
                pass

            try:
                if not request.args.get('type', None)[0] == 'aws_keys':
                    raise Exception()
                keys = get_aws_keys(token=canarytoken.value(), server=get_all_canary_domains()[0])
                if not keys:
                    response['Error'] = 4
                    response['Error_Message'] = 'Failed to retrieve AWS API keys. Please contact support@thinkst.com.'
                    raise Exception()
                response['aws_access_key_id'] = keys[0]
                response['aws_secret_access_key'] = keys[1]
                response['region'] = keys[2]
                response['output'] = keys[3]
                canarydrop['aws_access_key_id'] = keys[0]
                canarydrop['aws_secret_access_key'] = keys[1]
                canarydrop['region'] = keys[2]
                canarydrop['output'] = keys[3]
                save_canarydrop(canarydrop)
            except:
                pass

            try:
                if not request.args.get('type', None)[0] == 'kubeconfig':
                    raise Exception()
                if kubeconfig is None:
                    response['Error'] = 4
                    response['Error_Message'] = 'Failed to retrieve the kubeconfig. Please contact support@thinkst.com.'
                    raise Exception()
                response['kubeconfig'] = kubeconfig[1]
                canarydrop['kubeconfig'] = kubeconfig[1]
                canarydrop['generate'] = False
                save_canarydrop(canarydrop)
            except:
                pass

            try:
                if not request.args.get('type', None)[0] == 'web_image':
                    raise Exception()

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

                if not filename.lower().endswith(('.png','.gif','.jpg')):
                    response['Error'] = 4
                    response['Message'] = 'Uploaded image must be a PNG, GIF or JPG.'
                    raise Exception('Uploaded image must be a PNG, GIF or JPG')
                ext = filename.lower()[-4:]

                if len(filebody) > int(settings.MAX_UPLOAD_SIZE):
                    response['Error'] = 4
                    response['Message'] = 'File too large. File size must be < ' + str(int(settings.MAX_UPLOAD_SIZE)/(1024*1024)) + 'MB.'
                    raise Exception('File too large')

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
                save_canarydrop(canarydrop)
            except:
                pass

            try:
                if request.args.get('type', None)[0] != 'signed_exe':
                    raise Exception()

                fields = cgi.FieldStorage(
                    fp = request.content,
                    headers = request.getAllHeaders(),
                    environ = {'REQUEST_METHOD':'POST',
                    'CONTENT_TYPE': request.getAllHeaders()['content-type'],
                    }
                )#hacky way to parse out file contents and filenames
                filename = fields['signed_exe'].filename
                filebody = fields['signed_exe'].value

                if not filename.lower().endswith(('exe','dll')):
                    response['Error'] = 4
                    response['Message'] = 'Uploaded authenticode file must be an exe or dll.'
                    raise Exception('Uploaded authenticode file must be an exe or dll')

                if len(filebody) > int(settings.MAX_UPLOAD_SIZE):
                    response['Error'] = 4
                    response['Message'] = 'File too large. File size must be < ' + str(int(settings.MAX_UPLOAD_SIZE/(1024*1024))) + 'MB.'
                    raise Exception('File too large')

                signed_contents = make_canary_authenticode_binary(hostname=
                            canarydrop.get_hostname(with_random=False, as_url=True),
                            filebody=filebody)
                response['file_name'] = filename
                response['file_contents'] = "data:octet/stream;base64,"+base64.b64encode(signed_contents)
            except:
                pass

            try:
                if request.args.get('type', None)[0] != 'fast_redirect':
                    raise Exception()

                if not request.args['redirect_url'][0]:
                    raise Exception()

                canarydrop['redirect_url'] = request.args['redirect_url'][0]
                save_canarydrop(canarydrop)
            except:
                pass

            try:
                if request.args.get('type', None)[0] != 'slow_redirect':
                    raise Exception()

                if not request.args['redirect_url'][0]:
                    raise Exception()

                canarydrop['redirect_url'] = request.args['redirect_url'][0]
                save_canarydrop(canarydrop)
            except:
                pass

            if token_type == 'wireguard':
                canarydrop['wg_key'] = wg.generateCanarytokenPrivateKey(canarydrop["canarytoken"])
                save_canarydrop(canarydrop)
                response['wg_conf'] = canarydrop.get_wg_conf()
                response['qr_code'] = canarydrop.get_wg_qrcode()

        except Exception as e:
            if response['Error'] is None:
                response['Error'] = 255
                log.error('Unexpected error: {err}'.format(err=e))

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
            auth   = request.args.get('auth', None)[0]
            canarydrop = Canarydrop(**get_canarydrop(canarytoken=token))
            if not canarydrop:
                raise NoCanarytokenPresent()
            if not canarydrop['auth'] or canarydrop['auth'] != auth:
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
            elif fmt == 'msexcel':
                request.setHeader("Content-Type",
                                  "application/vnd.openxmlformats-officedocument"+\
                                                      ".spreadsheetml.sheet")
                request.setHeader("Content-Disposition",
                                  'attachment; filename={token}.xlsx'\
                                  .format(token=token))
                return make_canary_msexcel(url=canarydrop.get_url())
            elif fmt == 'cmd':
                request.setHeader("Content-Type", "text/plain")
                request.setHeader("Content-Disposition", 'attachment; filename={token}.reg'.format(token=token))
                return make_canary_msreg(url=canarydrop.get_hostname(), process_name=canarydrop['cmd_process'])
            elif fmt == 'pdf':
                request.setHeader("Content-Type", "application/pdf")
                request.setHeader("Content-Disposition",
                                  'attachment; filename={token}.pdf'\
                                  .format(token=token))
                return make_canary_pdf(hostname=canarydrop.get_hostname(nxdomain=True, with_random=False))
            elif fmt == 'awskeys':
                request.setHeader("Content-Type", "text/plain")
                request.setHeader("Content-Disposition",
                                  'attachment; filename=credentials')
                text="[default]\naws_access_key={id}\naws_secret_access_key={k}\nregion={r}\noutput={o}"\
                        .format(id=canarydrop['aws_access_key_id'], k=canarydrop['aws_secret_access_key'], r=canarydrop['region'], o=canarydrop['output'])
                return text
            elif fmt == 'kubeconfig':
                request.setHeader("Content-Type", "text/plain")
                request.setHeader("Content-Disposition",
                                  'attachment; filename=kubeconfig')
                return base64.b64decode(canarydrop['kubeconfig']).encode('utf-8')
            elif fmt == 'slackapi':
                request.setHeader("Content-Type", "text/plain")
                request.setHeader("Content-Disposition",
                                  'attachment; filename=slack_creds')
                text="# Slack API key\nslack_api_key = {key}".format(key=canarydrop['slack_api_key'])
                return text
            elif fmt == 'incidentlist_json':
                request.setHeader("Content-Type", "text/plain")
                request.setHeader("Content-Disposition",
                                  'attachment; filename={token}_history.json'\
                                  .format(token=token))
                return simplejson.dumps(canarydrop['triggered_list'], indent=4)
            elif fmt == 'incidentlist_csv':
                request.setHeader("Content-Type", "text/plain")
                request.setHeader("Content-Disposition",
                                  'attachment; filename={token}_history.csv'\
                                  .format(token=token))
                csvOutput = StringIO()
                incident_list = canarydrop['triggered_list']

                writer = csv.writer(csvOutput)

                details = set()
                for key in incident_list:
                    for element in incident_list[key].keys():
                        details.add(element)
                details = list(details)

                headers = ["Timestamp"] + details
                writer.writerow(headers)

                for key in incident_list:
                    items = []
                    for item in details:
                        items.append(incident_list[key].get(item, 'N/A'))
                    data = [datetime.datetime.fromtimestamp(float(key)).strftime('%Y-%m-%d %H:%M:%S.%s')] + items
                    writer.writerow(data)

                return csvOutput.getvalue()
            elif fmt == "my_sql":
                encoded   = request.args.get('encoded', "true")[0] == "true"

                request.setHeader("Content-Type", "application/zip")
                request.setHeader("Content-Disposition",
                                  'attachment; filename={token}_mysql_dump.sql.gz'\
                                  .format(token=token))
                return make_canary_mysql_dump(canarydrop=canarydrop, encoded=encoded)

        except Exception as e:
            log.error('Unexpected error in download: {err}'.format(err=e))

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
                if len(filebody) > int(settings.MAX_UPLOAD_SIZE):
                    response['Error'] = 4
                    response['Message'] = 'File too large. File size must be < ' + str(int(settings.MAX_UPLOAD_SIZE)/(1024*1024)) + 'MB.'
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
            log.error('Unexpected error in POST download: {err}'.format(err=e))
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
                                float(timestamp)).strftime('%Y %b %d %H:%M:%S (UTC)')
                    canarydrop['triggered_list'][formatted_timestamp] = canarydrop['triggered_list'].pop(timestamp)

        except (TypeError, NoCanarytokenPresent):
            return NoResource().render(request)
        g_api_key = get_canary_google_api_key()
        now = datetime.datetime.now()
        try:
            canarydrop['type']
            template = env.get_template('manage_new.html')
        except KeyError:
            template = env.get_template('manage.html')
        return template.render(canarydrop=canarydrop, API_KEY=g_api_key, now=now).encode('utf8')

    def render_POST(self, request):
        try:
            try:
                token = request.args.get('token', None)[0]
                auth  = request.args.get('auth',  None)[0]

                canarydrop = Canarydrop(**get_canarydrop(canarytoken=token))
                if not canarydrop['auth'] or canarydrop['auth'] != auth:
                    raise NoCanarytokenPresent()

            except (IndexError, TypeError, NoCanarytokenPresent):
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

            save_canarydrop(canarydrop=canarydrop)

            g_api_key = get_canary_google_api_key()
            template = env.get_template('manage.html')
            return template.render(canarydrop=canarydrop, saved=True,
                                        settings=settings, API_KEY=g_api_key).encode('utf8')

        except Exception as e:
            import traceback
            log.error('Exception in manage.html: {e}, {stack}'.format(e=e, stack=traceback.format_exc()))
            template = env.get_template('manage.html')
            return template.render(canarydrop=canarydrop, error=e,
                                        settings=settings).encode('utf8')

class HistoryPage(resource.Resource):
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
                                float(timestamp)).strftime('%Y %b %d %H:%M:%S.%f (UTC)')
                    canarydrop['triggered_list'][formatted_timestamp] = canarydrop['triggered_list'].pop(timestamp)

            if canarydrop.get('memo'):
                canarydrop['memo'] = unicode(canarydrop['memo'], "utf8")

        except (TypeError, NoCanarytokenPresent):
            return NoResource().render(request)
        g_api_key = get_canary_google_api_key()
        now = datetime.datetime.now()
        template = env.get_template('history.html')
        return template.render(canarydrop=canarydrop, API_KEY=g_api_key, now=now).encode('utf8')


class LimitedFile(File):
    def directoryListing(self):
        dl = DirectoryLister(self.path,
                               [],
                               self.contentTypes,
                               self.contentEncodings,
                               self.defaultType)
        dl.template = ""
        return dl

class SettingsPage(resource.Resource):
    isLeaf = True

    def getChild(self, name, request):
        if name == '':
            return self
        return Resource.getChild(self, name, request)

    def render_POST(self, request):
        request.responseHeaders.addRawHeader(b"content-type", b"application/json")
        response = { }
        try:
            token = request.args.get('token', None)[0]
            auth  = request.args.get('auth',  None)[0]
            setting = request.args.get('setting',  None)[0]

            canarydrop = Canarydrop(**get_canarydrop(canarytoken=token))
            if not canarydrop['auth'] or canarydrop['auth'] != auth:
                raise NoCanarytokenPresent()

            if setting not in ['clonedsite', 'email_enable', 'webhook_enable',
                               'sms_enable', 'browser_scanner_enable', 'web_image_enable']:
                raise NoCanarytokenPresent()

        except (IndexError, TypeError, NoCanarytokenPresent):
            return NoResource().render(request)

        if setting == 'clonedsite':
            try:
                clonedsite = request.args['clonedsite'][0]
                if not clonedsite:
                    raise KeyError

                cloned_token = {'clonedsite': clonedsite,
                               'canarytoken': token}
                canarydrop.clonedsite_token = save_clonedsite_token(cloned_token)
                save_canarydrop(canarydrop)
                response['clonedsite_js'] =  canarydrop.get_cloned_site_javascript()
                response['clonedsite'] =  clonedsite
            except (IndexError, KeyError):
                return NoResource().render(request)
        elif setting == "email_enable":
            canarydrop['alert_email_enabled'] = request.args['value'][0] == "on"
        elif setting == "webhook_enable":
            canarydrop['alert_webhook_enabled'] = request.args['value'][0] == "on"
        elif setting == "sms_enable":
            canarydrop['alert_sms_enabled'] = request.args['value'][0] == "on"
        elif setting == "browser_scanner_enable":
            canarydrop['browser_scanner_enabled'] = request.args['value'][0] == "on"
        elif setting == "web_image_enable":
            canarydrop['web_image_enabled'] = request.args['value'][0] == "on"

        save_canarydrop(canarydrop=canarydrop)
        response['result'] = 'success'

        return simplejson.dumps(response)

class AUP(resource.Resource):
    isLeaf = True

    def getChild(self, name, request):
        if name == '':
            return self
        return Resource.getChild(self, name, request)

    def render_GET(self, request):
        now = datetime.datetime.now()
        template = env.get_template('legal.html')
        return template.render(now=now).encode('utf8')

class CanarytokensHttpd():
    def __init__(self, port=80):
        self.port = port

        root = Resource()
        root.putChild("", Redirect("generate"))
        root.putChild("generate", GeneratorPage())
        root.putChild("manage", ManagePage())
        root.putChild("download", DownloadPage())
        root.putChild("settings", SettingsPage())
        root.putChild("history", HistoryPage())
        root.putChild("resources", LimitedFile("/srv/templates/static"))
        root.putChild("legal", AUP())

        with open('/srv/templates/robots.txt', 'r') as f:
            root.putChild("robots.txt", Data(f.read(), "text/plain"))

        wrapped = EncodingResourceWrapper(root, [GzipEncoderFactory()])
        site = server.Site(wrapped)
        if settings.DEBUG:
            site.displayTracebacks = settings.DEBUG
        else:
            site.displayTracebacks = False
        self.service = internet.TCPServer(self.port, site)
        return None
