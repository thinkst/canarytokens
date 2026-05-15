<img src="http://canarytokens.org/resources/logo.png" width="200" />

# Canarytokens

by Thinkst Applied Research

## Overview

Canarytokens help track activity and actions on your network.

If you have any issues please check out our FAQ over [here](https://github.com/thinkst/canarytokens/wiki#), or create an issue and we'll try to get back to you as soon as possible.

## Table of Contents
  - [Code of Conduct](#code-of-conduct)
  - [Deprecations](#deprecations)
  - [Installation](#installation)
  - [Configuration](#configuration)
  - [AWS ID infrastructure](#aws-id-infrastructure)
  - [Configuration of Outgoing SMTP](#configuration-of-outgoing-smtp)
  - [Alert throttling](#alert-throttling)
  - [Webhook failure limiting](#webhook-failure-limiting)
  - [FAQ](#faq)
  - [Contributing](#contributing)

## Code of Conduct

This project and everyone participating in it is governed by the
[Code of Conduct](https://github.com/thinkst/.github/blob/master/CODE_OF_CONDUCT.md).
By participating, you are expected to uphold this code. Please report unacceptable behavior
to github@thinkst.com.

## Deprecations

* The Slack API Token is deprecated and it's no longer possible to create new ones. Old tokens will still work.

## Installation

We recommend [the Docker image installation process](https://github.com/thinkst/canarytokens-docker).

## Configuration


The Canarytokens server can use many different settings configurations. You can find them in `settings.py`. There are two
main settings files: `frontend.env` and `switchboard.env`.

The `frontend.env` contains the frontend process settings such as:
- CANARY_DOMAINS=mytesttokensdomain.com
- CANARY_NXDOMAINS=pdf.demo.canarytokens.net
- CANARY_AWSID_URL=<custom awsid url>
- CANARY_AWSID_AUTH=<shared awsid auth token>
- CANARY_WEB_IMAGE_UPLOAD_PATH=/uploads
- CANARY_GOOGLE_API_KEY=<custom google maps api key>
- LOG_FILE=frontend.log

The `switchboard.env` contains the switchboard process settings such as:

| Variable Name                   | Value                                           |
|---------------------------------|--------------------------------------------------|
| CANARY_MAILGUN_DOMAIN_NAME      | <mailgun domain>                                 |
| CANARY_MAILGUN_API_KEY          |                                                  |
| CANARY_MANDRILL_API_KEY         |                                                  |
| CANARY_SENDGRID_API_KEY         |                                                  |
| CANARY_PUBLIC_IP                | <instead of using a domain>                      |
| CANARY_PUBLIC_DOMAIN            | <instead of using an IP>                         |
| CANARY_ALERT_EMAIL_FROM_ADDRESS | noreply@yourdomain.com                           |
| CANARY_ALERT_EMAIL_FROM_DISPLAY | "Canarytoken Mailer"                             |
| CANARY_ALERT_EMAIL_SUBJECT      | "Alert"                                          |
| CANARY_MAX_ALERTS_PER_MINUTE    | 1000                                             |
| CANARY_SMTP_USERNAME            | <smtp username>                                  |
| CANARY_SMTP_PASSWORD            | <smtp password>                                  |
| CANARY_SMTP_SERVER              | smtp.gmail.com                                   |
| CANARY_IPINFO_API_KEY           | <ipinfo.io api key>                              |
| CANARY_SMTP_PORT                | 587                                              |
| CANARY_WEB_IMAGE_UPLOAD_PATH    | /uploads                                         |
| LOG_FILE                        | switchboard.log                                  |
| ERROR_LOG_WEBHOOK               | <URI of a webhook you want Error Logs posted to> |
| CANARY_FORCE_HTTPS              | force `https` protocol scheme for Canarytokens   |
| CANARY_LAMBDA_AWS_CRED_REPORT_AUTH | <shared credential report checker auth token> |

Please note that when choosing which email provider you would like to use, you **MUST** only provide
information related to that provider. E.g. if you have `CANARY_MAILGUN_API_KEY` then you must remove the others such as
`CANARY_SENDGRID_API_KEY` and `CANARY_MANDRILL_API_KEY`.

If you are using Mailgun's European infrastructure for your Canarytokens Server, you will need to add `CANARY_MAILGUN_BASE_URL=https://api.eu.mailgun.net` to your `switchboard.env`. If you do not specify that,
we will use the regular URL as 'https://api.mailgun.net' as the default.

### AWS ID infrastructure

AWS API key Canarytokens use AWS-side infrastructure to allocate IAM users and run safety-net checks. That infrastructure has moved to a private repo.

This repo still owns the Canarytokens-facing integration points:

* `CANARY_AWSID_URL` in `frontend.env` is the API Gateway/Lambda URL for the `LinkAWSIDTokenUserToCanaryConsole` endpoint managed from the private repo.
* `CANARY_AWSID_AUTH` in `frontend.env` must match the auth token in the AWS ID secret. The frontend sends `domain`, `token`, and `auth` when creating an AWS key token.
* If either `CANARY_AWSID_URL` or `CANARY_AWSID_AUTH` is unset, AWS key token creation is disabled for this Canarytokens instance.
* `CANARY_LAMBDA_AWS_CRED_REPORT_AUTH` in `switchboard.env` enables the `/a/cr` callback used by the AWS ID credential report checker.

### Configuration of Outgoing SMTP

When configuring outgoing SMTP please consider the following:

Restrictions:
* no other provider like Mailgun or Sendgrid must be configured for this to work
* For AWS SES `CANARY_ALERT_EMAIL_FROM_DISPLAY` should be in the format: `CANARY_ALERT_EMAIL_FROM_DISPLAY=CanaryAlert <canaryalert@my-email-domain.here>`

The following settings have to be configured in `switchboard.env` for SMTP to work:
* CANARY_SMTP_SERVER: the SMTP server
* CANARY_SMTP_PORT: the port number of the SMTP server (must be a StartTLS enabled port!)
* CANARY_SMTP_USERNAME: Username for the SMTP server (no anonymous SMTP supported right now)
* CANARY_SMTP_PASSWORD: the password that corresponds to the username

A complete example config in `switchboard.env` then looks like this:
```
CANARY_SMTP_SERVER=smtp.yourserver.com
CANARY_SMTP_PORT=587
CANARY_SMTP_USERNAME=<your smtp username>
CANARY_SMTP_PASSWORD=<your smtp password>
CANARY_ALERT_EMAIL_FROM_ADDRESS=canary@yourdomain.com
CANARY_ALERT_EMAIL_SUBJECT="Canary Alert via SMTP"
```

## Alert throttling
By default, unless running in DEBUG mode, no more than 1 alert per unique calling IP per
minute is permitted.  Activity will still be recorded in the database, and visible in
the token management console, but alerts will not be generated (email and/or webhook).

This is tunable with the switchboard ENV variable `CANARY_MAX_ALERTS_PER_MINUTE`.

## Webhook failure limiting
After a webhook returns an error 5 times in a row, it is disabled. This behaviour can be
tuned with `MAX_ALERT_FAILURES`.

## FAQ

We have a FAQ over [here](https://github.com/thinkst/canarytokens/wiki)

## Contributing

Please check out our [Code of Conduct](https://github.com/thinkst/.github/blob/master/CODE_OF_CONDUCT.md) and [Contributing](https://github.com/thinkst/.github/blob/master/CONTRIBUTING.md) documents before submitting a pull request.

We look forward to your valuable contributions.
