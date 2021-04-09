import simplejson
import twill

from twisted.application.internet import TimerService
from twisted.logger import Logger
log = Logger()

from canarydrop import Canarydrop
from channel import InputChannel
from queries import get_canarydrop, get_all_bitcoin_accounts,\
                    save_bitcoin_account, get_bitcoin_address_balance
from exception import BitcoinFailure
from constants import INPUT_CHANNEL_BITCOIN

class ChannelBitcoin(InputChannel):
    """Input channel that polls for payments from a Bitcoin address, and
       alerts when they climb."""
    CHANNEL = INPUT_CHANNEL_BITCOIN

    def __init__(self, min_delay=3600*24, switchboard=None):
        log.info('Started channel {name}'.format(name=self.CHANNEL))
        super(ChannelBitcoin, self).__init__(switchboard=switchboard,
                                            name=self.CHANNEL)
        self.min_delay = min_delay
        self.service = TimerService(self.min_delay, self.schedule_polling)

    def schedule_polling(self,):
        """A dummy method. For now, all balance polls are run immediately.
           In the future they'll be spread out over the interval."""
        try:
            for bitcoin_account in get_all_bitcoin_accounts():
                self.poll(bitcoin_account=bitcoin_account)
        except Exception as e:
            log.error('Bitcoin error: {error}'.format(error=e))

    def poll(self, bitcoin_account=None):
        try:
            current_balance = get_bitcoin_address_balance(
                                address=bitcoin_account['address'])
        except BitcoinFailure as e:
            log.error('Could not retrieve bitcoin balance: {error}'\
                    .format(error=e))
            return

        if current_balance> bitcoin_account['balance']:
            canarydrop = Canarydrop(**get_canarydrop(
                            canarytoken=bitcoin_account['canarytoken']))
            self.dispatch(canarydrop=canarydrop, new_balance=current_balance,
                          old_balance=bitcoin_account['balance'],
                          address=bitcoin_account['address'])
            bitcoin_account['balance'] = current_balance
            save_bitcoin_account(bitcoin_account=bitcoin_account)

    def format_additional_data(self, **kwargs):
        log.info(kwargs)
        additional_report = ''
        if kwargs.has_key('address') and kwargs['address']:
            additional_report += 'Bitcoin Address: {address}\r\n'.format(
                                                address=kwargs['address'])
        if kwargs.has_key('new_balance') and kwargs['new_balance'] and\
           kwargs.has_key('old_balance') and kwargs['old_balance']:
            additional_report += 'Balance Changed: from {old_balance} to {new_balance}\r\n'.format(
                                                old_balance=kwargs['old_balance'],
                                                new_balance=kwargs['new_balance'],
                                                )
        return additional_report
