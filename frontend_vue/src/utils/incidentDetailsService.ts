import { TOKENS_TYPE } from '@/components/constants';
import {
  hasChannelCustomLabel,
  formatTokenTypeLabel,
  parseGeoInfo,
} from '@/utils/incidentUtils';
import {
  convertUnixTimeStampToDate,
  convertISOtoLocalDate,
} from '@/utils/utils';
import type { HitsType, CoordsType } from '@/components/tokens/types.ts';

export default function incidentDetailsService(
  hitAlert: HitsType,
  tokenType: string
) {
  const sharedBasicInfo = {
    token_type: formatTokenTypeLabel(hitAlert.token_type),
    input_channel: hasChannelCustomLabel(
      hitAlert.input_channel,
      hitAlert.token_type
    ),
    src_data: hitAlert.src_data,
    useragent: hitAlert.useragent || null,
    last4: hitAlert.last4 || null,
    amount: hitAlert.amount || null,
    merchant: hitAlert.merchant || null,
    mail: hitAlert.mail || null,
    referer: hitAlert.referer || hitAlert.referrer || null,
    request_args: hitAlert?.request_args || null,
  };

  const sharedMainDetails = {
    time_of_hit: convertUnixTimeStampToDate(hitAlert.time_of_hit),
    src_ip: hitAlert.src_ip,
    geo_info: parseGeoInfo(hitAlert),
  };

  switch (tokenType) {
    case TOKENS_TYPE.AWS_KEYS:
      return {
        basic_info: {
          ...sharedBasicInfo,
          location: hitAlert.location ? hitAlert.location : null,
        },
        ...sharedMainDetails,
        is_tor_relay: hitAlert.is_tor_relay,
        additional_info: {
          ...hitAlert.additional_info,
          aws_key_log_data: hitAlert.additional_info.aws_key_log_data
            ? {
                last_used: hitAlert.additional_info.aws_key_log_data.last_used
                  ? convertISOtoLocalDate(
                      hitAlert.additional_info.aws_key_log_data.last_used
                    )
                  : null,
                service_used:
                  hitAlert.additional_info.aws_key_log_data.service_used,
                eventName:
                  hitAlert.additional_info.aws_key_log_data?.eventName ?? null,
              }
            : null,
        },
      };

    case TOKENS_TYPE.CREDIT_CARD_V2:
      return {
        basic_info: {
          ...sharedBasicInfo,
          location: hitAlert.location ? hitAlert.location : null,
        },
        ...sharedMainDetails,
        is_tor_relay: null,
        additional_info: {
          ...hitAlert.additional_info,
          aws_key_log_data: null,
        },
      };

    case TOKENS_TYPE.PWA:
      function locationInfo(
        location: string | GeolocationPosition | CoordsType
      ) {
        if (typeof location === 'string') {
          return location;
        } else if (location.coords !== null) {
          return location.coords;
        } else {
          return location;
        }
      }

      return {
        basic_info: {
          ...sharedBasicInfo,
          location: hitAlert.location ? locationInfo(hitAlert.location) : null,
        },
        ...sharedMainDetails,
        is_tor_relay: hitAlert.is_tor_relay,
        additional_info: {
          ...hitAlert.additional_info,
          aws_key_log_data: null,
        },
      };

    default:
      return {
        basic_info: {
          ...sharedBasicInfo,
          location: hitAlert.location ? hitAlert.location : null,
        },
        ...sharedMainDetails,
        is_tor_relay: hitAlert.is_tor_relay,
        additional_info: {
          ...hitAlert.additional_info,
          aws_key_log_data: null,
        },
      };
  }
}
