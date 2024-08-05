import {
  convertUnixTimeStampToDate,
  convertISOtoLocalDate,
} from '@/utils/utils';
import type { HitsType, FormattedHitsType } from '@/components/tokens/types.ts';
import { tokenServices } from './tokenServices';
import {
  TOKENS_TYPE,
  INCIDENT_CHANNEL_TYPE_LABELS,
  INCIDENT_DETAIL_CUSTOM_LABELS,
} from '@/components/constants';

/**
 * Checks if the token type exists in INCIDENT_CHANNEL_TYPE_LABELS
 * and returns the corresponding value.
 * If it doesn't exist in the list, it just returns the returned channel.
 */
function hasChannelCustomLabel(channel: string, tokenType: string) {
  return INCIDENT_CHANNEL_TYPE_LABELS.hasOwnProperty(tokenType)
    ? INCIDENT_CHANNEL_TYPE_LABELS[
        tokenType as keyof typeof INCIDENT_CHANNEL_TYPE_LABELS
      ]
    : channel;
}

/**
 * Formats a given string by replacing underscores with spaces and capitalizing the first letter.
 */
function formatKey(string: string) {
  const formattedString = string
    .replace(/_/g, ' ')
    .replace(/^(.)/, function (match, group) {
      return group.toUpperCase();
    });

  return formattedString;
}

/**
 * Formats the incident details object by applying custom labels and formatting keys.
 */
export function formatLabels(
  incidentDetails: FormattedHitsType | keyof FormattedHitsType
) {
  try {
    return Object.entries(incidentDetails).reduce(
      (acc: Record<string, unknown>, [key, val]) => {
        const formattedKey = INCIDENT_DETAIL_CUSTOM_LABELS.hasOwnProperty(key)
          ? INCIDENT_DETAIL_CUSTOM_LABELS[
              key as keyof typeof INCIDENT_DETAIL_CUSTOM_LABELS
            ]
          : formatKey(key);

        if (typeof val === 'object' && val !== null) {
          acc[formattedKey] = formatLabels(
            val as unknown as keyof FormattedHitsType
          );
        } else {
          acc[formattedKey] = val;
        }

        return acc;
      },
      {}
    );
  } catch (error) {
    console.error(`Error in formatting labels: ${error}`);
    return incidentDetails;
  }
}

/**
 * Formats the label of a token type based on the given token.
 */
export function formatTokenTypeLabel(token: string) {
  const token_const: string | undefined = Object.values(TOKENS_TYPE).find(
    (value) => value === token
  );
  return token_const ? tokenServices[token_const].label : token;
}

/**
 * Checks if a value is not empty and all its nested keys have a value
 */
export function isNotEmpty(
  value: number | string | null | string[] | undefined | Record<string, unknown>
) {
  if (typeof value === 'object' && value !== null) {
    if (Array.isArray(value)) {
      return value.length > 0;
    } else {
      return Object.values(value).some(
        (val) =>
          val !== null &&
          val !== undefined &&
          (typeof val !== 'object' || Object.keys(val).length > 0)
      );
    }
  }
  return value !== null && value !== undefined;
}

function isCreditCardtoken(token: string) {
  return token === TOKENS_TYPE.CREDIT_CARD;
}

function isAWStoken(token: string) {
  return token === TOKENS_TYPE.AWS_KEYS;
}

export function buildIncidentDetails(
  hitAlert: HitsType
): FormattedHitsType | HitsType {
  try {
    const incidentDetails = {
      time_of_hit: convertUnixTimeStampToDate(hitAlert.time_of_hit),
      src_ip: hitAlert.src_ip,
      geo_info: !hitAlert.geo_info.bogon
        ? {
            ...hitAlert.geo_info,
          }
        : {
            ip: hitAlert.geo_info.ip,
            bogon: hitAlert.geo_info.bogon,
          },
      is_tor_relay: !isCreditCardtoken(hitAlert.token_type)
        ? hitAlert.is_tor_relay
        : null,
      basic_info: {
        // TODO: add token memo
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
        referer: hitAlert.referer || null,
        // TODO make this typecheck; remove the ignore below at `return` after
        location: (hitAlert.token_type === TOKENS_TYPE.PWA ? (typeof hitAlert.location === 'string' ? hitAlert.location : hitAlert.location?.coords) : hitAlert.location) || null,
      },
      additional_info: {
        ...hitAlert.additional_info,
        aws_key_log_data:
          isAWStoken(hitAlert.token_type) &&
          hitAlert.additional_info.aws_key_log_data
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
    //@ts-ignore
    return incidentDetails;
  } catch (error) {
    console.error(`Error in building the Incident Details object: ${error}`);
    return hitAlert;
  }
}
