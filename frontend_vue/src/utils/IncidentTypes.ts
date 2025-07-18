export type CoordsType = {
  coords: GeolocationPosition | null;
};

type BasicInfo = {
  token_type: string;
  input_channel: string;
  src_data: string | null;
  useragent: string | null;
  last4: string | null;
  amount: string | null;
  merchant: string | null;
  mail: string | null;
  referer: string | null;
  request_args: any | null;
  location:
    | string
    | GeolocationPosition
    | CoordsType
    | GeolocationCoordinates
    | null;
};

type MainDetails = {
  time_of_hit: string;
  src_ip: string;
  geo_info: any;
};

// AWS Keys specific types
type AWSKeyLogData = {
  last_used: string | null;
  service_used: string;
  eventName: string[] | null;
};

type AWSKeysIncidentDetails = {
  basic_info: BasicInfo;
  time_of_hit: string;
  src_ip: string | null;
  geo_info: any;
  is_tor_relay: boolean | null;
  additional_info: {
    aws_key_log_data: AWSKeyLogData | null;
    [key: string]: any;
  };
};

// Credit Card types
type CreditCardV2IncidentDetails = {
  basic_info: BasicInfo;
  time_of_hit: string;
  is_tor_relay: null;
  additional_info: {
    aws_key_log_data: null;
    [key: string]: any;
  };
};

// PWA types
type PWAIncidentDetails = {
  basic_info: BasicInfo;
  time_of_hit: string;
  src_ip: string;
  geo_info: any;
  is_tor_relay: boolean | null;
  additional_info: {
    aws_key_log_data: null;
    [key: string]: any;
  };
};

// AWS Infra types
type AWSInfraEvent = {
  eventName: string | null;
  eventTime: string | undefined;
  accountAndRegion: string | undefined;
};

type AWSInfraDecoyResource = {
  asset_type: string | null;
  request_parameters: string | null;
};

type AWSInfraIdentity = {
  userIdentity: string | null;
  userAgent: string | null;
};

type AWSInfraMetadata = {
  eventId: string | null;
  readOnlyEvent: boolean | null;
  eventCategory: string | null;
  classification: string | null;
};

type AWSInfraIncidentDetails = {
  basic_info: BasicInfo;
  time_of_hit: string;
  src_ip: string | null;
  geo_info: any;
  is_tor_relay: null;
  event: AWSInfraEvent;
  decoy_resource: AWSInfraDecoyResource;
  identity: AWSInfraIdentity;
  metadata: AWSInfraMetadata;
};

type DefaultIncidentDetails = {
  basic_info: BasicInfo;
  time_of_hit: string;
  src_ip: string;
  geo_info: any;
  is_tor_relay: boolean | null;
  additional_info: {
    aws_key_log_data: {
      last_used: string | null;
      service_used: string;
      eventName: string[] | null;
    } | null;
    [key: string]: any;
  };
};

type FormattedIncidentDetailsType =
  | AWSKeysIncidentDetails
  | CreditCardV2IncidentDetails
  | PWAIncidentDetails
  | AWSInfraIncidentDetails
  | DefaultIncidentDetails;

export type {
  BasicInfo,
  MainDetails,
  AWSKeyLogData,
  AWSKeysIncidentDetails,
  CreditCardV2IncidentDetails,
  PWAIncidentDetails,
  AWSInfraEvent,
  AWSInfraDecoyResource,
  AWSInfraIdentity,
  AWSInfraMetadata,
  AWSInfraIncidentDetails,
  DefaultIncidentDetails,
  FormattedIncidentDetailsType,
};
