# Cypress Tests - README

This README file will guide you through the process of setting up and running Cypress tests in your project.

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

Headless Mode
To run Cypress tests in headless mode (useful for CI/CD pipelines), use:

```
npx cypress run
```

### 5. Writing Tests

Cypress tests are written in JavaScript and are placed in the `cypress/e2e` folder. Create a new file in this directory to start writing your tests:

```
touch cypress/e2e/sample_test_spec.cy.js
```

### 6. Cypress documentation

We have a workflow [here](https://github.com/thinkst/canarytokens/blob/sara/cypress/.github/workflows/cypress.yml) which will run in each PR.

### 7. Cypress documentation

https://docs.cypress.io/
