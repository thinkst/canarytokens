import { AssetTypesEnum } from '@/components/tokens/aws_infra/constants.ts';
import type { AssetData } from '@/components/tokens/aws_infra/types.ts';

export const ASSET_CONFIG = {
  [AssetTypesEnum.S3BUCKET]: {
    label: 'S3 Bucket',
    nameKey: 'bucket_name',
    fieldsLabel: {
      bucket_name: 'S3 Bucket Name',
      objects: 'S3 Bucket Object Paths',
      off_inventory: 'Off Inventory',
    },
    fieldsWithIcons: ['objects'] as string[],
    fieldsAIgenerated: 'objects',
    defaultValues: {
      bucket_name: '',
      objects: [] as string[],
      off_inventory: false,
    },
  },
  [AssetTypesEnum.SQSQUEUE]: {
    label: 'SQS Queue',
    nameKey: 'sqs_queue_name',
    fieldsLabel: {
      sqs_queue_name: 'Queue Name',
      off_inventory: 'Off Inventory',
    },
    fieldsWithIcons: [] as string[],
    fieldsAIgenerated: '',
    defaultValues: {
      sqs_queue_name: '',
      off_inventory: false,
    },
  },
  [AssetTypesEnum.SSMPARAMETER]: {
    label: 'SSM Parameter',
    nameKey: 'ssm_parameter_name',
    fieldsLabel: {
      ssm_parameter_name: 'Parameter Name',
      off_inventory: 'Off Inventory',
    },
    fieldsWithIcons: [] as string[],
    fieldsAIgenerated: '',
    defaultValues: {
      ssm_parameter_name: '',
      off_inventory: false,
    },
  },
  [AssetTypesEnum.SECRETMANAGERSECRET]: {
    label: 'Secrets Manager Secret',
    nameKey: 'secret_name',
    fieldsLabel: {
      secret_name: 'Secret Name',
      off_inventory: 'Off Inventory',
    },
    fieldsWithIcons: [] as string[],
    fieldsAIgenerated: '',
    defaultValues: {
      secret_name: '',
      off_inventory: false,
    },
  },
  [AssetTypesEnum.DYNAMODBTABLE]: {
    label: 'Dynamo DB Table',
    nameKey: 'table_name',
    fieldsLabel: {
      table_name: 'Table Name',
      table_items: 'Table Items',
      off_inventory: 'Off Inventory',
    },
    fieldsWithIcons: ['table_items'] as string[],
    fieldsAIgenerated: 'table_items',
    defaultValues: {
      table_name: '',
      table_items: [] as string[],
      off_inventory: false,
    },
  },
};

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
    ASSET_CONFIG[assetType].fieldsLabel[fieldKey as keyof AssetData] || fieldKey
  );
}

export function getAssetDefaultValues(assetType: AssetTypesEnum): AssetData {
  return ASSET_CONFIG[assetType].defaultValues;
}

export function hasFieldIcon(
  assetType: AssetTypesEnum,
  fieldKey: keyof AssetData
): boolean {
  return ASSET_CONFIG[assetType]?.fieldsWithIcons?.includes(
    fieldKey as keyof AssetData
  );
}

// Fields that support AI generated naming
export function hasAiGeneratedField(assetType: AssetTypesEnum): string {
  return ASSET_CONFIG[assetType]?.fieldsAIgenerated;
}
