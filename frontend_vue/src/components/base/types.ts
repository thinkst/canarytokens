export interface BaseStateVariantType {
  danger: unknown;
  warning: unknown;
  info: unknown;
}

export interface BaseColorVariantType extends BaseStateVariantType {
  primary: unknown;
  secondary: unknown;
}

export interface BaseButtonVariantType extends BaseColorVariantType {
  text: unknown;
}

export type ButtonVariantType = keyof BaseButtonVariantType;
export type NotificationBoxVariantType = keyof BaseStateVariantType;
