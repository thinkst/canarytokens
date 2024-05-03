import { convertUnixTimeStampToDate } from '@/utils/utils';
import type { HitsType, FormattedHitsType } from '@/components/tokens/types.ts';
import { tokenServices } from './tokenServices';
import {
  TOKENS_TYPE,
  INCIDENT_CHANNEL_TYPE_LABELS,
  INCIDENT_DETAIL_CUSTOM_LABELS,
} from '@/components/constants';

/**
 * Checks if the type exists in INCIDENT_CHANNEL_TYPE_LABELS and returns the corresponding value,
 * or 'HTTP' if not found.
 */
function hasChannelCustomLabel(type: string) {
  return INCIDENT_CHANNEL_TYPE_LABELS.hasOwnProperty(type)
    ? INCIDENT_CHANNEL_TYPE_LABELS[
        type as keyof typeof INCIDENT_CHANNEL_TYPE_LABELS
      ]
    : 'HTTP';
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
 * Removes keys and values from an object if the value is null, an empty object, an empty array,
 * or if all nested keys and values are removed.
 */
export function removeNullEmptyObjectsAndArrays(
  incidentDetails: FormattedHitsType
): FormattedHitsType {
  try {
    return Object.entries(incidentDetails).reduce((acc, [key, value]) => {
      if (
        value !== null &&
        value !== undefined &&
        !(typeof value === 'object' && Object.keys(value).length === 0) &&
        !(Array.isArray(value) && value.length === 0)
      ) {
        if (typeof value === 'object') {
          const nestedObj = removeNullEmptyObjectsAndArrays(
            value as FormattedHitsType
          );
          if (Object.keys(nestedObj).length > 0) {
            acc[key] = nestedObj as Record<string, string>;
          }
        } else {
          acc[key] = value;
        }
      }
      return acc;
    }, {} as FormattedHitsType);
  } catch (error) {
    console.error(`Error in remove Null, Empty Objects and Arrays: ${error}`);
    return incidentDetails;
  }
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
        input_channel: hasChannelCustomLabel(hitAlert.input_channel),
        src_data: hitAlert.src_data,
        useragent: hitAlert.useragent,
        last4: hitAlert.last4,
        amount: hitAlert.amount,
        merchant: hitAlert.merchant,
        mail: hitAlert.mail,
        referer: hitAlert.referer,
        location: hitAlert.location,
      },
      additional_info: {
        ...hitAlert.additional_info,
        aws_key_log_data:
          isAWStoken(hitAlert.token_type) &&
          hitAlert.additional_info.aws_key_log_data
            ? {
                last_used: hitAlert.additional_info.aws_key_log_data.last_used
                  ? new Date(
                      Number(
                        hitAlert.additional_info.aws_key_log_data.last_used
                      )
                    )
                  : null,
                service_used:
                  hitAlert.additional_info.aws_key_log_data.service_used,
              }
            : null,
      },
    };

    return incidentDetails;
  } catch (error) {
    console.error(`Error in building the Incident Details object: ${error}`);
    return hitAlert;
  }
}
