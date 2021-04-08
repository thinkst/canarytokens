import re

from zope.interface import implements

from twisted.internet import defer
from twisted.mail import smtp
from twisted.cred.portal import IRealm
from twisted.cred.portal import Portal
from twisted.logger import Logger
log = Logger()
from twisted.application import internet
from twisted.application import service

from constants import INPUT_CHANNEL_SMTP
from tokens import Canarytoken
from canarydrop import Canarydrop
from exception import NoCanarytokenPresent, NoCanarytokenFound
from channel import InputChannel
from queries import get_canarydrop



class CanaryMessageDelivery:
    implements(smtp.IMessageDelivery)

    def __init__(self):
        print 'Created CanaryMessageDelivery()'

    def receivedHeader(self, helo, origin, recipients):
        return "Received: CanaryMessageDelivery"

    def validateFrom(self, helo, origin):
        return origin

    def validateTo(self, user):
        # Only messages directed to the "console" user are accepted.
        if user.dest.local == "console":
            return lambda: CanaryMessage()
        raise smtp.SMTPBadRcpt(user)



class CanaryMessage:
    implements(smtp.IMessage)

    def __init__(self, esmtp=None):
        self.esmtp = esmtp
        self.headers = []
        self.headers_finished = False
        self.attachments = []
        self.links = []
        self.links_re = re.compile('(http[s]?://[^\s\'"]+)', re.I)
        self.mime_boundary = None
        self.mime_boundary_re = re.compile('.*boundary[ ]*=[" ]?([^" ]+)')
        self.in_mime_header = True
        self.lines = []
        self.stored_byte_count = 0

    def lineReceived(self, line):
        if line == '' and not self.headers_finished:
            self.headers_finished = True

        if not self.headers_finished:
            self.headers.append(line)
            m = self.mime_boundary_re.match(line)
            if m:
                self.mime_boundary = m.group(1)
        else:
            if self.mime_boundary:
                if self.in_mime_header:
                    if line == '':
                        self.in_mime_header = False
                    else:
                        self.attachments[-1].append(line)

                if self.mime_boundary in line:
                    self.in_mime_header = True
                    self.attachments.append([])

            if self.stored_byte_count < 5*2**20: #5MB limit
                self.lines.append(line)
                self.stored_byte_count ++ len(line)

    def eomReceived(self):
        print "New message received:"
        self.esmtp.mail['headers'] = self.headers
        print "\n".join(self.headers)
        self.esmtp.mail['links'] = self.links_re.findall(
                                   '\r\n'.join(self.lines))
        print "\n".join(self.links)
        self.esmtp.mail['attachments'] = [ '\n'.join(x) for x in self.attachments]
        print '\n\n'.join([ '\n'.join(x) for x in self.attachments])
        self.lines = None
        self.esmtp.dispatch()
        #return defer.succeed(None)
        d = defer.Deferred()
        d.callback("Success")
        return d

    def connectionLost(self):
        # There was an error, throw away the stored lines
        self.lines = None


class CanaryESMTP(smtp.ESMTP):
    def __init__(self, **kwargs):
        smtp.ESMTP.__init__(self, **kwargs)
        self.mail = {'recipients': [],
                     'sender': '',
                     'helo': {},
                     'headers': [],
                     'links': [],
                     'attachments': []}

    def greeting(self,):
        self.src_ip = self.transport.getPeer().host
        try:
            return self.factory.responses['greeting']
        except KeyError:
            return smtp.ESMTP.greeting(self)

    def receivedHeader(self, helo, origin, recipients):
        self.mail['helo']['client_name'] = helo[0]
        self.mail['helo']['client_ip'] = helo[1]
        self.mail['sender'] = str(origin)
        for r in recipients:
            address = r.dest.addrstr
            self.mail['recipients'].append(address)

    def validateFrom(self, helo, origin):
        return origin

    def validateTo(self, user):
        # Only messages directed to the "console" user are accepted.
        try:
            token = Canarytoken(value=user.dest.local)
            self.canarydrop = Canarydrop(**get_canarydrop(canarytoken=token.value()))
            return lambda: CanaryMessage(esmtp=self)
        except (NoCanarytokenPresent, NoCanarytokenFound):
            log.warn('No token in recipient address: {address}'\
                     .format(address=user.dest.local))
        except Exception as e:
            log.error(e)

        raise smtp.SMTPBadRcpt(user)

    def dispatch(self,):
        self.factory.dispatch(canarydrop=self.canarydrop, src_ip=self.src_ip,
                      mail=self.mail)

class CanarySMTPFactory(smtp.SMTPFactory, InputChannel):
    protocol = CanaryESMTP
    CHANNEL = INPUT_CHANNEL_SMTP

    def __init__(self, *a, **kw):
        self.responses = {'data_success': 'Finished', 'greeting': 'Hello there'}
        self.switchboard = kw.pop('switchboard')
        smtp.SMTPFactory.__init__(self, *a, **kw)
        InputChannel.__init__(self, switchboard=self.switchboard,
                              name=self.CHANNEL,
                              unique_channel=False)

    def buildProtocol(self, addr):
        p = smtp.SMTPFactory.buildProtocol(self, addr)
#        p.delivery = self.delivery
#        p.challengers = {"LOGIN": LOGINCredentials, "PLAIN": PLAINCredentials}
        return p

    def format_additional_data(self, **kwargs):
        log.info('%r' % kwargs)
        if kwargs.has_key('src_ip') and kwargs['src_ip']:
            additional_report = 'Source IP : {ip}'.format(ip=kwargs['src_ip'])
        if kwargs.has_key('mail') and kwargs['mail']:
            mail = kwargs['mail']
            additional_report += """
Client Name : {client_name}
Client IP   : {client_ip}
Sender      : {sender}
Recipients  : {recipients}
Links       : {links}
Attachments :
{attachments}


Headers     :
{headers}""".format(
                recipients = ', '.join(mail['recipients']),
                sender = mail['sender'],
                client_ip= mail['helo']['client_ip'],
                client_name = mail['helo']['client_name'],
                links = ', '.join(mail['links']),
                attachments = '\n\n'.join(mail['attachments']),
                headers = '\n'.join(mail['headers']))

        return additional_report


class ChannelSMTP():
    def __init__(self, port=25, switchboard=None):
        self.service = internet.TCPServer(port, CanarySMTPFactory(None, switchboard=switchboard))
