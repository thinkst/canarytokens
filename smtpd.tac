import re

from zope.interface import implements

from twisted.internet import defer
from twisted.mail import smtp
from twisted.cred.portal import IRealm
from twisted.cred.portal import Portal



class CanaryMessageDelivery:
    implements(smtp.IMessageDelivery)

    def __init__(self):
        print 'Created CanaryMessageDelivery()'

    def receivedHeader(self, hello, origin, recipients):
        return "Received: CanaryMessageDelivery"

    def validateFrom(self, hello, origin):
        return origin

    def validateTo(self, user):
        # Only messages directed to the "console" user are accepted.
        if user.dest.local == "console":
            return lambda: CanaryMessage()
        raise smtp.SMTPBadRcpt(user)



class CanaryMessage:
    implements(smtp.IMessage)

    def __init__(self):
        self.headers = []
        self.headers_finished = False
        self.attachments = []
        self.links = []
        self.links_re = re.compile('.*(http[s]?://[^\s\'"]+).*', re.I)
        self.mime_boundary = None
        self.mime_boundary_re = re.compile('.*boundary="([^"]*)"')
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
        print "\n".join(self.headers)
        print "\n".join(self.links)
        print '\n\n'.join([ '\n'.join(x) for x in self.attachments])
        self.lines = None
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

    def greeting(self,):
        try:
            return self.factory.responses['greeting']
        except KeyError:
            return smtp.ESMTP.greeting(self)

    def receivedHeader(self, hello, origin, recipients):
        return "Received: CanaryMessageDelivery"

    def validateFrom(self, hello, origin):
        return origin

    def validateTo(self, user):
        # Only messages directed to the "console" user are accepted.
        if user.dest.local == "console":
            return lambda: CanaryMessage()
        raise smtp.SMTPBadRcpt(user)


class CanarySMTPFactory(smtp.SMTPFactory):
    protocol = CanaryESMTP

    def __init__(self, *a, **kw):
        self.responses = kw.pop('responses')
        smtp.SMTPFactory.__init__(self, *a, **kw)
#        self.delivery = CanaryMessageDelivery()
    

    def buildProtocol(self, addr):
        p = smtp.SMTPFactory.buildProtocol(self, addr)
#        p.delivery = self.delivery
#        p.challengers = {"LOGIN": LOGINCredentials, "PLAIN": PLAINCredentials}
        return p



class SimpleRealm:
    implements(IRealm)

    def requestAvatar(self, avatarId, mind, *interfaces):

        if smtp.IMessageDelivery in interfaces:
            return smtp.IMessageDelivery, CanaryMessageDelivery(), lambda: None
        raise NotImplementedError()



def main():
    from twisted.application import internet
    from twisted.application import service    
    
    portal = Portal(SimpleRealm())
#    checker = InMemoryUsernamePasswordDatabaseDontUse()
#    checker.addUser("guest", "password")
#    portal.registerChecker(checker)
    
    responses = {'data_success': 'Finished', 'greeting': 'Hello there'}
    a = service.Application("Canary SMTP Server")
    internet.TCPServer(2500, CanarySMTPFactory(portal, responses=responses)).setServiceParent(a)
    
    return a

application = main()
