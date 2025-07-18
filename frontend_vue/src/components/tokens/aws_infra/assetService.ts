import { AssetTypesEnum } from '@/components/tokens/aws_infra/constants.ts';
import type {
  AssetData,
  S3ObjectData,
} from '@/components/tokens/aws_infra/types.ts';

export const ASSET_CONFIG = {
  [AssetTypesEnum.S3BUCKET]: {
    label: 'S3 Bucket',
    nameKey: 'bucket_name',
    fields: {
      bucket_name: 'S3 Bucket Name',
      objects: 'S3 Bucket Objects',
      object_path: 'Object Path',
      off_inventory: 'Off Inventory',
    },
    defaultValues: {
      bucket_name: '',
      objects: [] as S3ObjectData[],
      off_inventory: false,
    },
  },
  [AssetTypesEnum.SQSQUEUE]: {
    label: 'SQS Queue',
    nameKey: 'queue_name',
    fields: {
      queue_name: 'Queue Name',
      message_count: 'Message Count',
      off_inventory: 'Off Inventory',
    },
    defaultValues: {
      queue_name: '',
      message_count: 0,
      off_inventory: false,
    },
  },
  [AssetTypesEnum.SSMPARAMETER]: {
    label: 'SSM Parameter',
    nameKey: 'ssm_parameter_name',
    fields: {
      ssm_parameter_name: 'Parameter Name',
      ssm_parameter_value: 'Parameter Value',
      off_inventory: 'Off Inventory',
    },
    defaultValues: {
      ssm_parameter_name: '',
      ssm_parameter_value: '',
      off_inventory: false,
    },
  },
  [AssetTypesEnum.SECRETMANAGERSECRET]: {
    label: 'Secrets Manager Secret',
    nameKey: 'secretsmanager_secret_name',
    fields: {
      secretsmanager_secret_name: 'Secret Name',
      secretsmanager_secret_value: 'Secret Value',
      off_inventory: 'Off Inventory',
    },
    defaultValues: {
      secretsmanager_secret_name: '',
      secretsmanager_secret_value: '',
      off_inventory: false,
    },
  },
  [AssetTypesEnum.DYNAMODBTABLE]: {
    label: 'Dynamo DB Table',
    nameKey: 'dynamodb_name',
    fields: {
      dynamodb_name: 'Table Name',
      dynamodb_partition_key: 'Partition Key',
      dynamodb_row_count: 'Row Count',
      off_inventory: 'Off Inventory',
    },
    defaultValues: {
      dynamodb_name: '',
      dynamodb_partition_key: '',
      dynamodb_row_count: 0,
      off_inventory: false,
    },
  },
} as const;

export function getAssetLabel(assetType: AssetTypesEnum): string {
  return ASSET_CONFIG[assetType].label;
}

export function getAssetNameKey(assetType: AssetTypesEnum): string {
  return ASSET_CONFIG[assetType].nameKey;
}

export function getFieldLabel(
  assetType: AssetTypesEnum,
  fieldKey: string
): string {
  return (
    ASSET_CONFIG[assetType].fields[fieldKey as keyof AssetData] || fieldKey
  );
}

export function getAssetDefaultValues(assetType: AssetTypesEnum): AssetData {
  return ASSET_CONFIG[assetType].defaultValues;
}
