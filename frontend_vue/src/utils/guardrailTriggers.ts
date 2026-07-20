import { getDefaultGuardrailTriggers } from '@/api/main';

export const prompts: string[] = [];

let promptsPromise: Promise<string[]> | null = null;

export async function loadDefaultGuardrailTriggers() {
  if (!promptsPromise) {
    promptsPromise = getDefaultGuardrailTriggers().then((defaultPrompts) => {
      prompts.splice(0, prompts.length, ...defaultPrompts);
      return prompts;
    }).catch(() => prompts);
  }

  return promptsPromise;
}
