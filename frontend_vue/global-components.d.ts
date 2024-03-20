// this file is needed for type checking on global registered components
import BaseLinkDocumentation from './src/components/base/_BaseLinkDocumentation.vue'
import BaseButton from './src/components/base/_BaseButton.vue'
import BaseSwitch from './src/components/base/_BaseSwitch.vue'

declare module 'vue' {
  export interface GlobalComponents {
    BaseLinkDocumentation: typeof BaseLinkDocumentation,
    BaseButton: typeof BaseButton,
    BaseSwitch: typeof BaseSwitch,
  }
}