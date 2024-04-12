export interface BaseStateVariantType {
  danger: string;
  warning: string;
  info: string;
}

export interface BaseColorVariantType extends BaseStateVariantType {
  primary: string;
  secondary: string;
}

export interface BaseButtonVariantType extends BaseColorVariantType {
  text: string;
  'text-light': string;
}

export type ButtonVariantType = keyof BaseButtonVariantType;
export type NotificationBoxVariantType = keyof BaseStateVariantType;
