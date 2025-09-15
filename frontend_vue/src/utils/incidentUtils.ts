import type { FormattedIncidentDetailsType } from '@/utils/IncidentTypes';
import { tokenServices } from './tokenServices';
import {
  TOKENS_TYPE,
  INCIDENT_CHANNEL_TYPE_LABELS,
  INCIDENT_DETAIL_CUSTOM_LABELS,
} from '@/components/constants';
import { formatKey } from '@/utils/utils';

/**
 * Checks if the token type exists in INCIDENT_CHANNEL_TYPE_LABELS
 * and returns the corresponding value.
 * If it doesn't exist in the list, it just returns the returned channel.
 */
export function hasChannelCustomLabel(channel: string, tokenType: string) {
  return INCIDENT_CHANNEL_TYPE_LABELS.hasOwnProperty(tokenType)
    ? INCIDENT_CHANNEL_TYPE_LABELS[
        tokenType as keyof typeof INCIDENT_CHANNEL_TYPE_LABELS
      ]
    : channel;
}

/**
 * Formats the incident details object by applying custom labels and formatting keys.
 */
export function formatLabels(
  incidentDetails: FormattedIncidentDetailsType | keyof FormattedIncidentDetailsType
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
            val as unknown as keyof FormattedIncidentDetailsType
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

export function parseGeoInfo(hitAlert: Record<string, any>) {
  if (hitAlert.geo_info == null) return null;
  if (!hitAlert.geo_info.bogon) {
    return {
      ...hitAlert.geo_info,
    };
  }
  return {
    ip: hitAlert.geo_info.ip,
    bogon: hitAlert.geo_info.bogon,
  };
}
