# Frontend app

## Recommended IDE Setup

[VSCode](https://code.visualstudio.com/) + [Volar](https://marketplace.visualstudio.com/items?itemName=Vue.volar) (and disable Vetur) + [TypeScript Vue Plugin (Volar)](https://marketplace.visualstudio.com/items?itemName=Vue.vscode-typescript-vue-plugin).


For the best experience with Tailwind and keeping the order in the list class, this VSCode plugins is recommended:

Name: Tailwind CSS IntelliSense
VS Marketplace Link: https://marketplace.visualstudio.com/items?itemName=bradlc.vscode-tailwindcss


## Customize configuration

See [Vite Configuration Reference](https://vitejs.dev/config/).

   - Create a `.env` file in the root of your project.

   - Define your local variables in the `.env` file. For example:
     ```
     VITE_GOOGLE_MAPS_API_KEY=your_local_api_key
     VITE_API_URL=your_server_url
     ```

   - Add the `.env` file to your `.gitignore` to prevent it from being committed.

## Project Setup

```sh
npm install
```

### Compile and Hot-Reload for Development

```sh
npm run dev
```

### Type-Check, Compile and Minify for Production

```sh
npm run build
```

### Lint with [ESLint](https://eslint.org/)

```sh
npm run lint
```

### Compile and Minify for Production without Type-check

```sh
npm run build-only
```

### Run unit tests

```sh
npm run test
```


### Format with prettier

```sh
npm run format
```



# Add a new token
For the component of the app to work together, every token name should be aligned with the backend.

i.e. the Cloned Site, will be always referenced as ```clonedsite```, as per backend documentation.

### Add a constant and token service
1. Define a constant in the TOKENS_TYPE list to reference the token name.

This constant will be used throughout the dynamic imports. For example, for the Cloned Site token, add the following constant:

```
export const TOKENS_TYPE = {
  ...,
  CLONED_SITE = 'clonedsite'
};
```

2. Add the UI elements in tokenServices.ts

   - Upload the icon for the token to the ```assets/token_icons``` directory.

   - Make sure the icon filename matches the backend-provided name.


i.e. for ClonedSite

```
  [TOKENS_TYPE.CLONED_SITE]: {
    label: 'Cloned Site Token',
    description: 'Add here description for the Home page',
    documentationLink: 'https://docs.canarytokens.org/link-here',
    icon: `${TOKENS_TYPE.CLONED_SITE}.png`,
    instruction: 'Add here short instruction that will be shown after the token is generated',
    carousel: ['add first slide info','add second slide info','add third slide info']
  },
```
---

### Token's folder

Add a folder inside components/tokens
> Name it as the backend provided token's name

#### The folder should contain the following files:

    clonedsite
    .
    ├── ActivatedToken.vue              # Shown in the modal after token is generated
    ├── GenerateTokenForm.vue           # Form to generate token
    ├── howToUse.ts                     # Array of suggestions
    ├── ManageToken                     # Component included in the ManageToken page
    ├── TokenDisplay                    # Displayer for token snippet/url/png/download/etc

#### ActivatedToken.vue
- Displays the `TokenDisplay` component along with additional instructions for the user if needed.

#### GenerateTokenForm.vue
- Contains the input fields for generating a token.
- The parent component is responsible for handling the form submission logic. You don't need to worry about it

#### HowToUse.ts
- An array of strings containing the instructions for using the token.

#### ManageToken.vue
- Displays the `TokenDisplay` component and provides additional space for adding instructions or functionalities if needed.

#### TokenDisplay.vue
- The core component that displays the token code snippet, download buttons, and any other necessary elements.

### Form validation

For each GenerateTokenForm component, you need to define a validation schema using the Yup validation library. The schema should be defined in the ```src/utils/formValidators.ts`` file as shown below:

i.e. Cloned site

```
  [TOKENS_TYPE.CLONED_SITE]: {
    schema: Yup.something....
  },
```

---


...that should be it.

That's all you need to do to add a new token. No further modifications are necessary.
