from twisted.internet import reactor, defer
from twisted.internet.task import deferLater
from twisted.names import dns, server, error
from twisted.logger import Logger
log = Logger()

from constants import INPUT_CHANNEL_DNS
from tokens import Canarytoken
from canarydrop import Canarydrop
from exception import NoCanarytokenPresent, NoCanarytokenFound, IncompleteRequest, DuplicateDNSRequest
from channel import InputChannel
from queries import get_canarydrop, get_all_canary_domains
from redismanager import db, KEY_CACHED_DNS_REQUEST

import settings
import math
import base64
import re
from exceptions import UnicodeDecodeError

class DNSServerFactory(server.DNSServerFactory, object):
    def handleQuery(self, message, protocol, address):
        if message.answer:
            return

        query = message.queries[0]
        if address:
            src_ip = address[0]
            if address[1] == 0:
                log.debug(('Dropping request from {src} because source port is 0').format(src=src_ip))
                return None
        else:
            src_ip = protocol.transport.socket.getpeername()[0]

        try:
            log.info('Query: {} sent {}'.format(src_ip, query))
        except UnicodeDecodeError:
            # Invalid query
            return None

        return self.resolver.query(query, src_ip).addCallback(
            self.gotResolverResponse, protocol, message, address
        ).addErrback(
            self.gotResolverError, protocol, message, address
        )

    def gotResolverError(self, failure, protocol, message, address):
        if failure.check(error.DNSQueryRefusedError):
            response = self._responseFromMessage(message=message, rCode=dns.EREFUSED)

            self.sendReply(protocol, response, address)
            self._verboseLog("Lookup failed")
        else:
            super(DNSServerFactory, self).gotResolverError(failure, protocol, message, address)



class ChannelDNS(InputChannel):
    CHANNEL = INPUT_CHANNEL_DNS

    def __init__(self, listen_domain='canary.thinknest.com', switchboard=None):
        super(ChannelDNS, self).__init__(switchboard=switchboard,
                                         name=self.CHANNEL)
        self.listen_domain = listen_domain
        self.canary_domains = get_all_canary_domains()

    def _do_ns_response(self, name=None):
        """
        Calculate the response to a query.
        """
        answer = dns.RRHeader(
            name=name,
            payload=dns.Record_NS(ttl=10, name='ns1.'+name),
            type=dns.NS,
            auth=True)
        additional = dns.RRHeader(
            name='ns1.'+name,
            payload=dns.Record_A(ttl=10, address=settings.PUBLIC_IP),
            type=dns.A,
            auth=True)
        answers = [answer]
        authority = []
        additional = [additional]
        return answers, authority, additional

    def _do_soa_response(self, name=None):
        """
        Ensure a standard response to a SOA query.
        """
        answer = dns.RRHeader(
            name=name,
            payload=dns.Record_SOA(mname=name.lower(),
                rname='info.'+name.lower(),
                serial=0, refresh=300, retry=300, expire=300, minimum=300,
                ttl=300),
            type=dns.SOA,
            auth=True)
        answers = [answer]
        authority = []
        additional = []

        return answers, authority, additional

    def _do_dynamic_response(self, name=None):
        """
        Calculate the response to a query.
        """
        payload = dns.Record_A(ttl=10, address=settings.PUBLIC_IP)
        answer = dns.RRHeader(
            name=name,
            payload=payload,
            type=dns.A,
            auth=True)
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
    
    def _cmd_data(self, computer_name=None, user_name=None):
        data = {}
        data['cmd_computer_name'] = 'Not Obtained'
        data['cmd_user_name'] = 'Not Obtained'
        if user_name and user_name != '':
            data['cmd_user_name'] = user_name[1:]
        if computer_name and computer_name != '':
            data['cmd_computer_name'] = computer_name[1:]
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

    def _generic(self, generic_data=None):
        data = {}
        generic_data = generic_data.replace('.', '').upper()
        #this channel doesn't have padding, add if needed
        generic_data += '='*int(
                            (
                             math.ceil(float(len(generic_data)) / 8) * 8
                                 - len(generic_data)
                            )
                        )
        try:
            data['generic_data'] = base64.b32decode(generic_data)
        except TypeError:
            data['generic_data'] = 'Unrecoverable data: {}'.format(generic_data)
        return data

    def _dtrace_process_data(self, uid=None, hostname=None, command=None):
        data = {}
        try:
            data['dtrace_uid'] = base64.b64decode(uid)
        except:
            log.error('Could not retrieve uid from dtrace '+\
                    'process alert: {uid}'.format(uid=uid))
        try:
            data['dtrace_hostname'] = base64.b64decode(hostname.replace('.', ''))
        except:
            log.error('Could not retrieve hostname from dtrace '+\
                    'process alert: {hostname}'.format(hostname=hostname))
        try:
            data['dtrace_command'] = base64.b64decode(command.replace('.', ''))
        except:
            log.error('Could not retrieve command from dtrace '+\
                    'process alert: {command}'.format(command=command))

        return data

    def _dtrace_file_open(self, uid=None, hostname=None, filename=None):
        data = {}
        try:
            data['dtrace_uid'] = base64.b64decode(uid)
        except:
            log.error('Could not retrieve uid from dtrace '+\
                    'file open alert: {uid}'.format(uid=uid))

        try:
            data['dtrace_hostname'] = base64.b64decode(hostname.replace('.', ''))
        except:
            log.error('Could not retrieve hostname from dtrace '+\
                    'process alert: {hostname}'.format(hostname=hostname))
        try:
            data['dtrace_filename'] = base64.b64decode(filename.replace('.', ''))
        except:
            log.error('Could not retrieve filename from dtrace '+\
                    'file open alert: {filename}'.format(filename=filename))

        return data

    def _desktop_ini_browsing(self, username=None, hostname=None, domain=None):
        data = {}
        data['windows_desktopini_access_username'] = username
        data['windows_desktopini_access_hostname'] = hostname
        data['windows_desktopini_access_domain'] = domain
        return data

    def _log4_shell(self, computer_name=None):
        data = {}
        if len(computer_name) <= 1:
            computer_name = 'Not Obtained'
        else:
            computer_name = computer_name[1:]
        data['log4_shell_computer_name'] = computer_name
        return data

    def look_for_source_data(self, token=None, value=None):
        try:
            value = value.lower()
            (haystack, domain) = value.split(token)
            sql_server_username  = re.compile('([A-Za-z0-9.-]*)\.[0-9]{2}\.', re.IGNORECASE)
            mysql_username       = re.compile('([A-Za-z0-9.-]*)\.M[0-9]{3}\.', re.IGNORECASE)
            linux_inotify        = re.compile('([A-Za-z0-9.-]*)\.L[0-9]{2}\.', re.IGNORECASE)
            generic              = re.compile('([A-Za-z0-9.-]*)\.G[0-9]{2}\.', re.IGNORECASE)
            dtrace_process       = re.compile('([0-9]+)\.([A-Za-z0-9-=]+)\.h\.([A-Za-z0-9.-=]+)\.c\.([A-Za-z0-9.-=]+)\.D1\.', re.IGNORECASE)
            dtrace_file_open     = re.compile('([0-9]+)\.([A-Za-z0-9-=]+)\.h\.([A-Za-z0-9.-=]+)\.f\.([A-Za-z0-9.-=]+)\.D2\.', re.IGNORECASE)
            desktop_ini_browsing = re.compile('([^\.]+)\.([^\.]+)\.?([^\.]*)\.ini\.', re.IGNORECASE)
            log4_shell           = re.compile('([A-Za-z0-9.-]*)\.L4J\.', re.IGNORECASE)
            cmd_computername     = re.compile('(.+)\.UN\.(.+)\.CMD\.', re.IGNORECASE)

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

            m = generic.match(value)
            if m:
                return self._generic(generic_data=m.group(1))

            m = dtrace_process.match(value)
            if m:
                return self._dtrace_process_data(uid=m.group(2), hostname=m.group(3), command=m.group(4))

            m = dtrace_file_open.match(value)
            if m:
                return self._dtrace_file_open(uid=m.group(2), hostname=m.group(3), filename=m.group(4))

            m = log4_shell.match(value)
            if m:
                return self._log4_shell(computer_name=m.group(1))
            
            m = cmd_computername.match(value)
            if m:
                return self._cmd_data(computer_name=m.group(1), user_name=m.group(2))

        except Exception as e:
            log.error(e)
        return {}

    def query(self, query, src_ip):
        """
        Check if the query should be answered dynamically, otherwise dispatch to
        the fallback resolver.
        """

        IS_NX_DOMAIN = True in [query.name.name.lower().endswith(d)
                                for d in settings.NXDOMAINS]

        if (not True in [query.name.name.lower().endswith(d) for d in self.canary_domains]
            and not IS_NX_DOMAIN):
            return defer.fail(error.DNSQueryRefusedError())

        if query.type == dns.NS:
            return defer.succeed(self._do_ns_response(name=query.name.name))

        if query.type == dns.SOA:
            return  defer.succeed(self._do_soa_response(name=query.name.name))

        if query.type != dns.A:
            return defer.succeed(self._do_no_response(query=query))

        try:
            token = Canarytoken(value=query.name.name)

            canarydrop = Canarydrop(**get_canarydrop(canarytoken=token.value()))

            if canarydrop._drop['type'] == 'cmd':
                query_cmp = query.name.name.lower()
                cmd_regex = re.compile('(.+)\.UN\.(.+)\.CMD\.', re.IGNORECASE)
                valid = cmd_regex.match(query_cmp)

                # Ignore incomplete sensitive cmd requests
                if not valid:
                    raise IncompleteRequest('Incomplete request for sensitive cmd token')

                # Ignore duplicate requests
                cached_key = KEY_CACHED_DNS_REQUEST + query_cmp
                if db.exists(cached_key):
                    log.debug('Ignoring duplicate DNS request')
                    raise DuplicateDNSRequest('Duplicate request for sensitive cmd token')
                db.setex(cached_key, settings.CACHED_DNS_REQUEST_PERIOD, True)

            src_data = self.look_for_source_data(token=token.value(), value=query.name.name)

            if canarydrop._drop['type'] == 'my_sql':
                d = deferLater(reactor, 10, self.dispatch, canarydrop=canarydrop, src_ip=src_ip, src_data=src_data)
                d.addErrback(self._handleMySqlErr)
            else:
                self.dispatch(canarydrop=canarydrop, src_ip=src_ip, src_data=src_data)

        except (NoCanarytokenPresent, NoCanarytokenFound, DuplicateDNSRequest, IncompleteRequest):
            # If we dont find a canarytoken, lets just continue. No need to log.
            pass
        except Exception as e:
            log.error(e)

        if IS_NX_DOMAIN:
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
        log.info(kwargs)
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

            if 'generic_data' in kwargs['src_data']:
                    additional_report += '\nGeneric data: {generic_data}'\
                    .format(generic_data=kwargs['src_data']['generic_data'])

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

            if 'log4_shell_computer_name' in kwargs['src_data']:
                additional_report += '\nComputer name from Log4J shell: {computer_name}'\
                    .format(computer_name=kwargs['src_data']['log4_shell_computer_name'])
            
            if 'cmd_computer_name' in kwargs['src_data'] and 'cmd_user_name' in kwargs['src_data']:
                additional_report += '\nCommand execution on {computer_name} by {user_name}'\
                    .format(computer_name=kwargs['src_data']['cmd_computer_name'], user_name=kwargs['src_data']['cmd_user_name'])

        return additional_report

    def _handleMySqlErr(self, result):
        log.error("Error dispatching MySQL alert: {}".format(result))