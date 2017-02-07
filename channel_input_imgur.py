import simplejson

from twisted.application.internet import TimerService
from twisted.internet.task import deferLater
from twisted.internet import reactor
from twisted.python import log
from twisted.web.client import getPage

from canarydrop import Canarydrop
from channel import InputChannel
from queries import get_canarydrop, get_all_imgur_tokens, save_imgur_token,\
                    get_imgur_count
from constants import INPUT_CHANNEL_IMGUR

class ChannelImgur(InputChannel):
    """Input channel that polls imgur for changes to the view count, and
       alerts when they climb."""
    CHANNEL = INPUT_CHANNEL_IMGUR

    def __init__(self, min_delay=3600, switchboard=None):
        super(ChannelImgur, self).__init__(switchboard=switchboard,
                                            name=self.CHANNEL)
        self.min_delay = min_delay
        self.service = TimerService(self.min_delay, self.schedule_polling)

    def schedule_polling(self,):
        """A dummy method. For now, all view count polls are run immediately.
           In the future they'll be spread out over the interval."""
        delay = 0
        for imgur_token in get_all_imgur_tokens():
            self.schedule_poll(imgur_token=imgur_token, delay=delay)
            delay+=5

#        for imgur_token in get_all_imgur_tokens():
#            self.poll(imgur_token=imgur_token)

    def poll(self, imgur_token=None):
        try:
            count = get_imgur_count(imgur_id=imgur_token['id'])
            if count > imgur_token['count']:
                canarydrop = Canarydrop(**get_canarydrop(
                                canarytoken=imgur_token['canarytoken']))
                self.dispatch(canarydrop=canarydrop, count=count,
                              imgur_id=imgur_token['id'])
                imgur_token['count'] = count
                save_imgur_token(imgur_token=imgur_token)
        except Exception as e:
            log.err('Imgur error: {error}'.format(error=e))

    def schedule_poll(self, imgur_token=None, delay=None):
        d = deferLater(reactor, delay, self.request_imgur_count, imgur_token)

    def request_imgur_count(self, imgur_token):
        d = getPage(
            'http://imgur.com/ajax/views?images={imgur_id}'\
                                .format(imgur_id=imgur_token['id']),
            agent='Canarytokens Imgur Check')
        d.addCallback(self.received_imgur_count, imgur_token)
        return d

    def received_imgur_count(self, body, imgur_token):
        try:
            body = simplejson.loads(body)
            count = int(body['data'][imgur_token['id']])
            log.msg('Count for imgur token '+imgur_token['id']+ ' was '+str(count))
            if count > imgur_token['count']:
                canarydrop = Canarydrop(**get_canarydrop(
                                canarytoken=imgur_token['canarytoken']))
                self.dispatch(canarydrop=canarydrop, count=count,
                              imgur_id=imgur_token['id'])
                imgur_token['count'] = count
                save_imgur_token(imgur_token=imgur_token)
        except Exception as e:
            log.err('Imgur error: {error}'.format(error=e))

    def format_additional_data(self, **kwargs):
        log.msg('%r' % kwargs)
        additional_report = ''
        if kwargs.has_key('count') and kwargs['count']:
            additional_report += 'View Count: {count}\r\n'.format(
                                                count=kwargs['count'])
        if kwargs.has_key('imgur_id') and kwargs['imgur_id']:
            additional_report += 'Link: http://imgur.com/{imgur_id}\r\n'.format(
                                                imgur_id=kwargs['imgur_id'])
        return additional_report
