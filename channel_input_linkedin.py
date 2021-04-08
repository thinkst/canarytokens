import simplejson
import twill

from twisted.application.internet import TimerService
from twisted.logger import Logger
log = Logger()

from canarydrop import Canarydrop
from channel import InputChannel
from queries import get_canarydrop, get_all_imgur_tokens, save_imgur_token,\
                    get_imgur_count, get_all_linkedin_accounts,\
                    save_linkedin_account, get_linkedin_viewer_count
from exception import LinkedInFailure
from constants import INPUT_CHANNEL_LINKEDIN


#create_linkedin_account(username='blah@blah.com', password='mooo')
#ht = get_canarydrop(canarytoken=get_linkedin_account(username='blah@blah.com')['canarytoken'])
#ht['alert_email_enabled'] = True
#ht['alert_email_recipient'] = 'foo@foo.com'
#save_canarydrop(ht)


class ChannelLinkedIn(InputChannel):
    """Input channel that polls LinkedIn for changes to the profile view count, and
       alerts when they climb."""
    CHANNEL = INPUT_CHANNEL_LINKEDIN

    def __init__(self, min_delay=3600*24, switchboard=None):
        log.info('Started channel {name}'.format(name=self.CHANNEL))
        super(ChannelLinkedIn, self).__init__(switchboard=switchboard,
                                            name=self.CHANNEL)
        self.min_delay = min_delay
        self.service = TimerService(self.min_delay, self.schedule_polling)

    def schedule_polling(self,):
        """A dummy method. For now, all view count polls are run immediately.
           In the future they'll be spread out over the interval."""
        try:
            for linkedin_account in get_all_linkedin_accounts():
                self.poll(linkedin_account=linkedin_account)
        except Exception as e:
            log.error('LinkedIn error: {error}'.format(error=e))

    def poll(self, linkedin_account=None):
        try:
            current_count = get_linkedin_viewer_count(
                                username=linkedin_account['username'],
                                password=linkedin_account['password'])
        except LinkedInFailure as e:
            log.error('Could not retrieve linkedin view count: {error}'\
                    .format(error=e))
            return

        if current_count > linkedin_account['count']:
            canarydrop = Canarydrop(**get_canarydrop(
                            canarytoken=linkedin_account['canarytoken']))
            self.dispatch(canarydrop=canarydrop, count=current_count,
                          linkedin_username=linkedin_account['username'])
            linkedin_account['count'] = current_count
            save_linkedin_account(linkedin_account=linkedin_account)

    def format_additional_data(self, **kwargs):
        log.info('%r' % kwargs)
        additional_report = ''
        if kwargs.has_key('count') and kwargs['count']:
            additional_report += 'View Count: {count}\r\n'.format(
                                                count=kwargs['count'])
        if kwargs.has_key('linkedin_username') and kwargs['linkedin_username']:
            additional_report += 'LinkedIn User: {username}\r\n'.format(
                                                username=kwargs['linkedin_username'])
        return additional_report
