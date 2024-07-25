# Cypress Tests - README

## Table of Contents

1. Prerequisites
2. Installation
3. Running Tests
5. Writing Tests
6. CI/CD
7. Cypress documentation

## 1. Prerequisites

Before you begin, ensure you have the following installed on your machine:

- [Node.js](https://nodejs.org/) (version 20 or higher)
- [npm](https://www.npmjs.com/)

## 2. Installation

To install Cypress, you need to add it as a dev dependency to your project:

```
npm i
```


### 3. Running Tests

You can run Cypress tests in two ways: in the interactive Test Runner or in the headless mode.

This will launch the Cypress GUI where you can select and run tests.

```
npx cypress open
```

<img width="1508" alt="Captura de ecrã 2024-06-07, às 18 14 25" src="https://github.com/thinkst/canarytokens/assets/29093946/fc8ed414-ecc5-48e1-a48f-c66d3ec04763">
<img width="1499" alt="Captura de ecrã 2024-06-07, às 18 14 13" src="https://github.com/thinkst/canarytokens/assets/29093946/c6ce7370-904d-406e-abfd-700f7fbdd1e8">
<img width="1187" alt="Captura de ecrã 2024-06-07, às 18 14 01" src="https://github.com/thinkst/canarytokens/assets/29093946/0d7ce8f2-15c7-46e3-ae24-76b11fa2cafa">

Headless Mode

To run Cypress tests in headless mode (useful for CI/CD pipelines), use:

```
npx cypress run
```

<img width="765" alt="Captura de ecrã 2024-06-07, às 18 15 21" src="https://github.com/thinkst/canarytokens/assets/29093946/080e0501-5372-459c-b5f5-4088f7fb7df8">


### 5. Writing Tests

Cypress tests are written in JavaScript and are placed in the `cypress/e2e` folder. Create a new file in this directory to start writing your tests:

```
touch cypress/e2e/sample_test_spec.cy.js
```

### 6. Cypress documentation

We have a workflow [here](https://github.com/thinkst/canarytokens/blob/sara/cypress/.github/workflows/cypress.yml) which will run in each PR.

### 7. Cypress documentation

https://docs.cypress.io/
