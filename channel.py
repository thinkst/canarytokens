""""
Base class for all canarydrop channels.
"""

import datetime

import settings
from exception import DuplicateChannel
from twisted.python import log

class Channel(object):
    CHANNEL = 'Base'

    def __init__(self, switchboard=None, name=None):
        self.switchboard = switchboard
        self.name = name or self.CHANNEL
        log.msg('Started channel {name}'.format(name=self.name))

class InputChannel(Channel):
    CHANNEL = 'InputChannel'

    def __init__(self, switchboard=None, name=None, unique_channel=False):
        super(InputChannel, self).__init__(switchboard=switchboard, 
                                            name=name)
        try:
            self.register_input_channel()
        except DuplicateChannel as e:
            if unique_channel:
                raise e

    def register_input_channel(self,):
        self.switchboard.add_input_channel(name=self.name, channel=self)

    def format_additional_data(self, **kwargs):
        return ''

    def format_canaryalert(self, canarydrop=None, protocol="http",
                          host="canarydrops.org", params=None, **kwargs):
        msg = {}
        if params.get('body_length', 999999999) <= 140:
            msg['body'] = """Canarydrop@{time} via {channel_name}: """\
                .format(channel_name=self.name, 
                        time=datetime.datetime.utcnow()\
                                  .strftime("%Y-%m-%d %H:%M:%S"))
            capacity = 140 - len(msg['body'])
            msg['body'] += canarydrop.memo[:capacity]
        else:
            msg['body'] = """

One of your canarydrops was triggered.

Channel: {channel_name}
Time   : {time}
Memo   : {memo}
{additional_data}

Manage your settings for this Canarydrop:
http://{host}/manage?token={token}&auth={auth}
"""         .format(channel_name=self.name,
                    time=datetime.datetime.utcnow(),
                    memo=canarydrop.memo,
                    additional_data=self.format_additional_data(**kwargs),
                    protocol=protocol,
                    host=host,
                    token=canarydrop['canarytoken'],
                    auth=canarydrop['auth']
                    )

        if params.get('subject_required', False):
            msg['subject'] = settings.ALERT_EMAIL_SUBJECT
        if params.get('from_display_required', False):
            msg['from_display'] = settings.ALERT_EMAIL_FROM_DISPLAY
        if params.get('from_address_required', False):
            msg['from_address'] = settings.ALERT_EMAIL_FROM_ADDRESS

        return msg

    def dispatch(self, **kwargs):
        self.switchboard.dispatch(input_channel=self.name, **kwargs)


class OutputChannel(Channel):
    CHANNEL = 'OutputChannel'

    def __init__(self, switchboard=None, name=None):
        super(OutputChannel, self).__init__(switchboard=switchboard, 
                                            name=name)
        self.register_output_channel()

    def register_output_channel(self,):
        self.switchboard.add_output_channel(name=self.name, channel=self)

    def send_alert(self, input_channel=None, canarydrop=None, **kwargs):
        if not input_channel:
            raise Exception('Cannot send an alert when the input_channel is None')

        if not canarydrop:
            raise Exception('Cannot send an alert when the canarydrop is None')

        self.do_send_alert(input_channel=input_channel,
                           canarydrop=canarydrop,
                           **kwargs)

    def do_send_alert(self, **kwargs):
        pass

