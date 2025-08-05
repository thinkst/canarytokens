import { ref } from 'vue';
import type { ProposedAWSInfraTokenPlanData, AssetData } from '../types';
import { AssetTypesEnum } from '@/components/tokens/aws_infra/constants.ts';

type AssetFieldsData = {
  assetType: AssetTypesEnum;
  assetData: AssetData;
  index: number;
};

export const tempAssetsData = ref<ProposedAWSInfraTokenPlanData>({
  S3Bucket: [],
  SQSQueue: [],
  SSMParameter: [],
  SecretsManagerSecret: [],
  DynamoDBTable: [],
});

export function setTempAssetsData(data: ProposedAWSInfraTokenPlanData) {
  tempAssetsData.value = data;
}

export function getTempAssetsData() {
  return tempAssetsData.value;
}

export function setTempAssetsFields(newValues: AssetFieldsData) {
  const { assetType, assetData, index } = newValues;
  if (!tempAssetsData.value[assetType]) {
    tempAssetsData.value[assetType] = [];
  }
  if (index === -1) {
    (tempAssetsData.value[assetType] as AssetData[])?.unshift(assetData);
  } else {
    tempAssetsData.value[assetType]![index] = assetData;
  }
}
