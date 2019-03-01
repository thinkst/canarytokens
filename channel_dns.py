from twisted.internet import reactor, defer
from twisted.names import dns, server, error
from twisted.python import log

from constants import INPUT_CHANNEL_DNS
from tokens import Canarytoken
from canarydrop import Canarydrop
from exception import NoCanarytokenPresent, NoCanarytokenFound
from channel import InputChannel
from queries import get_canarydrop

import settings
import math
import base64
import re

class DNSServerFactory(server.DNSServerFactory):
    def handleQuery(self, message, protocol, address):
        if message.answer:
            return

        query = message.queries[0]
        src_ip = address[0]

        print 'query=%r,src_ip=%r' % (query, src_ip)
        return self.resolver.query(query, src_ip).addCallback(
            self.gotResolverResponse, protocol, message, address
        ).addErrback(
            self.gotResolverError, protocol, message, address
        )


class ChannelDNS(InputChannel):
    CHANNEL = INPUT_CHANNEL_DNS

    def __init__(self, listen_domain='canary.thinknest.com', switchboard=None):
        super(ChannelDNS, self).__init__(switchboard=switchboard,
                                         name=self.CHANNEL)
        self.logfile = open('output.txt', 'wb+')
        self.listen_domain = listen_domain

    def _do_ns_response(self, name=None):
        """
        Calculate the response to a query.
        """
        answer = dns.RRHeader(
            name=name,
            payload=dns.Record_NS(ttl=10, name='ns1.'+name),
            type=dns.NS)
        additional = dns.RRHeader(
            name='ns1.'+name,
            payload=dns.Record_A(ttl=10, address=settings.PUBLIC_IP),
            type=dns.A)
        answers = [answer]
        authority = []
        additional = [additional]
        return answers, authority, additional

    def _do_dynamic_response(self, name=None):
        """
        Calculate the response to a query.
        """
        payload = dns.Record_A(ttl=10, address=settings.PUBLIC_IP)
        answer = dns.RRHeader(
            name=name,
            payload=payload,
            type=dns.A)
        answers = [answer]
        authority = []
        additional = []
        return answers, authority, additional

    def _do_no_response(self, query=None):
        """
        Calculate the response to a query.
        """
        answers = []
        authority = []
        additional = []
        return answers, authority, additional

    def _sql_server_data(self, username=None):
        data = {}
        data['sql_username'] = base64.b64decode(username.replace('.','').replace('-','='))
        return data

    def _mysql_data(self, username=None):
        data = {}
        data['mysql_username'] = base64.b32decode(username.replace('.','').replace('-','=').upper())
        return data

    def _linux_inotify_data(self, filename=None):
        data = {}
        filename = filename.replace('.', '').upper()
        #this channel doesn't have padding, add if needed
        filename += '='*int(
                            (
                             math.ceil(float(len(filename)) / 8) * 8 
                                 - len(filename)
                            )
                        )
        data['linux_inotify_filename_access'] = base64.b32decode(filename)
        return data

    def _dtrace_process_data(self, uid=None, hostname=None, command=None):
        data = {}
        try:
            data['dtrace_uid'] = base64.b64decode(uid)
        except:
            log.err('Could not retrieve uid from dtrace '+\
                    'process alert: {uid}'.format(uid=uid))
        try:
            data['dtrace_hostname'] = base64.b64decode(hostname.replace('.', ''))
        except:
            log.err('Could not retrieve hostname from dtrace '+\
                    'process alert: {hostname}'.format(hostname=hostname))
        try:
            data['dtrace_command'] = base64.b64decode(command.replace('.', ''))
        except:
            log.err('Could not retrieve command from dtrace '+\
                    'process alert: {command}'.format(command=command))

        return data

    def _dtrace_file_open(self, uid=None, hostname=None, filename=None):
        data = {}
        try:
            data['dtrace_uid'] = base64.b64decode(uid)
        except:
            log.err('Could not retrieve uid from dtrace '+\
                    'file open alert: {uid}'.format(uid=uid))

        try:
            data['dtrace_hostname'] = base64.b64decode(hostname.replace('.', ''))
        except:
            log.err('Could not retrieve hostname from dtrace '+\
                    'process alert: {hostname}'.format(hostname=hostname))
        try:
            data['dtrace_filename'] = base64.b64decode(filename.replace('.', ''))
        except:
            log.err('Could not retrieve filename from dtrace '+\
                    'file open alert: {filename}'.format(filename=filename))

        return data

    def _desktop_ini_browsing(self, username=None, hostname=None, domain=None):
        data = {}
        data['windows_desktopini_access_username'] = username
        data['windows_desktopini_access_hostname'] = hostname
        data['windows_desktopini_access_domain'] = domain
        return data
    
    def _aws_keys_event(self, srcip=None, agent=None):
        data = {}
        data['aws_keys_event_source_ip'] = base64.b32decode(srcip.replace('8','=').upper())
        data['aws_keys_event_user_agent'] = base64.b32decode(agent.replace('.','').replace('8','=').upper())
        return data

    def look_for_source_data(self, token=None, value=None):
        try:
            value = value.lower()
            (haystack, domain) = value.split(token)
            sql_server_username  = re.compile('([A-Za-z0-9.-]*)\.[0-9]{2}\.', re.IGNORECASE)
            mysql_username       = re.compile('([A-Za-z0-9.-]*)\.M[0-9]{3}\.', re.IGNORECASE)
            linux_inotify        = re.compile('([A-Za-z0-9.-]*)\.L[0-9]{2}\.', re.IGNORECASE)
            dtrace_process       = re.compile('([0-9]+)\.([A-Za-z0-9-=]+)\.h\.([A-Za-z0-9.-=]+)\.c\.([A-Za-z0-9.-=]+)\.D1\.', re.IGNORECASE)
            dtrace_file_open     = re.compile('([0-9]+)\.([A-Za-z0-9-=]+)\.h\.([A-Za-z0-9.-=]+)\.f\.([A-Za-z0-9.-=]+)\.D2\.', re.IGNORECASE)
            desktop_ini_browsing = re.compile('([^\.]+)\.([^\.]+)\.?([^\.]*)\.ini\.', re.IGNORECASE)
            aws_keys_event       = re.compile('([A-Za-z0-9-]*)\.([A-Za-z0-9.-]*)\.A[0-9]{3}\.', re.IGNORECASE)

            m = desktop_ini_browsing.match(value)
            if m:
                if m.group(3):
                    return self._desktop_ini_browsing(username=m.group(1), hostname=m.group(2), domain=m.group(3))
                else:
                    return self._desktop_ini_browsing(username=m.group(1), domain=m.group(2))

            m = sql_server_username.match(value)
            if m:
                return self._sql_server_data(username=m.group(1))

            m = mysql_username.match(value)
            if m:
                return self._mysql_data(username=m.group(1))

            m = linux_inotify.match(value)
            if m:
                return self._linux_inotify_data(filename=m.group(1))

            m = dtrace_process.match(value)
            if m:
                return self._dtrace_process_data(uid=m.group(2), hostname=m.group(3), command=m.group(4))

            m = dtrace_file_open.match(value)
            if m:
                return self._dtrace_file_open(uid=m.group(2), hostname=m.group(3), filename=m.group(4))

            m = aws_keys_event.match(value)
            if m:
                return self._aws_keys_event(srcip=m.group(1), agent=m.group(2))

        except Exception as e:
            log.err(e)
        return {}

    def query(self, query, src_ip):
        """
        Check if the query should be answered dynamically, otherwise dispatch to
        the fallback resolver.
        """
        self.logfile.write('%r\n' % query)
        self.logfile.flush()

        if query.type == dns.NS:
            return defer.succeed(self._do_ns_response(name=query.name.name))

        if query.type != dns.A:
            return defer.succeed(self._do_no_response(query=query))
            #return defer.fail(error.DomainError())

        try:
            token = Canarytoken(value=query.name.name)

            canarydrop = Canarydrop(**get_canarydrop(canarytoken=token.value()))

            src_data = self.look_for_source_data(token=token.value(), value=query.name.name)

            self.dispatch(canarydrop=canarydrop, src_ip=src_ip, src_data=src_data)

#            return defer.succeed(
#                            self._do_dynamic_response(name=query.name.name,
#                                                      response=response))
        except (NoCanarytokenPresent, NoCanarytokenFound):
            # If we dont find a canarytoken, lets just continue. No need to log.
            pass
        except Exception as e:
            log.err(e)

        if query.name.name in settings.NXDOMAINS:
            return defer.fail(error.DomainError())

        return defer.succeed(self._do_dynamic_response(name=query.name.name))
        #return defer.fail(error.DomainError())

    def lookupCAA(self, name, timeout):
        """Respond with NXdomain to a -t CAA lookup."""
        return defer.fail(error.DomainError())

    def lookupAllRecords(self, name, timeout):
        """Respond with error to a -t ANY lookup."""
        return defer.fail(error.DomainError())

    def format_additional_data(self, **kwargs):
        log.msg('%r' % kwargs)
        additional_report = 'Source IP : {ip}'.format(ip=kwargs['src_ip'])

        if 'src_data' in kwargs:

            if 'sql_username' in kwargs['src_data']:
                additional_report += '\nSQL Server User: {username}'\
                   .format(username=kwargs['src_data']['sql_username'])

            if 'mysql_username' in kwargs['src_data']:
                additional_report += '\nMySQL User: {username}'\
                   .format(username=kwargs['src_data']['mysql_username'])

            if 'linux_inotify_filename_access' in kwargs['src_data']:
                additional_report += '\nLinux File Access: {filename}'\
                    .format(filename=kwargs['src_data']['linux_inotify_filename_access'])

            if 'dtrace_uid' in kwargs['src_data']:
                additional_report += '\nDTrace UID: {uid}'\
                    .format(uid=kwargs['src_data']['dtrace_uid'])

            if 'dtrace_hostname' in kwargs['src_data']:
                additional_report += '\nDTrace hostname: {hostname}'\
                    .format(hostname=kwargs['src_data']['dtrace_hostname'])

            if 'dtrace_command' in kwargs['src_data']:
                additional_report += '\nDTrace command: {command}'\
                    .format(command=kwargs['src_data']['dtrace_command'])

            if 'dtrace_filename' in kwargs['src_data']:
                additional_report += '\nDTrace filename: {filename}'\
                    .format(filename=kwargs['src_data']['dtrace_filename'])

            if 'windows_desktopini_access_username' in kwargs['src_data']\
                and 'windows_desktopini_access_domain' in kwargs['src_data']:
                if 'windows_desktopini_access_hostname' in kwargs['src_data']:
                    additional_report += '\nWindows Directory Browsing By: {domain}\{username} from {hostname}'\
                    .format(username=kwargs['src_data']['windows_desktopini_access_username'],
                            domain=kwargs['src_data']['windows_desktopini_access_domain'],
                            hostname=kwargs['src_data']['windows_desktopini_access_hostname'])
                else:
                    additional_report += '\nWindows Directory Browsing By: {domain}\{username}'\
                    .format(username=kwargs['src_data']['windows_desktopini_access_username'],
                        domain=kwargs['src_data']['windows_desktopini_access_domain'])
            
            if 'aws_keys_event_source_ip' in kwargs['src_data']:
                additional_report += '\nAWS Keys used by: {ip}'\
                    .format(ip=kwargs['src_data']['aws_keys_event_source_ip'])

        return additional_report

