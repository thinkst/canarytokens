Canarytokens
=============
by Thinkst Applied Research

Overview
--------
Canarytokens helps track activity and actions on your network.

Installation
------------
We recommend [the Docker image installation process](https://github.com/thinkst/canarytokens-docker).

Configuration
-------------

The Canarytokens server can use many different settings configurations. You can find them in `settings.py`. There are two
main settings files: `frontend.env` and `switchboard.env`. 

The `frontend.env` contains the frontend process settings such as:
- CANARY_DOMAINS=mytesttokensdomain.com
- CANARY_NXDOMAINS=pdf.demo.canarytokens.net
- CANARY_AWSID_URL=<custom awsid url>
- CANARY_WEB_IMAGE_UPLOAD_PATH=/uploads
- CANARY_GOOGLE_API_KEY=<custom google maps api key>
- LOG_FILE=frontend.log

The `switchboard.env` contains the switchboard process settings such as:
- CANARY_MAILGUN_DOMAIN_NAME=<mailgun domain>
- CANARY_MAILGUN_API_KEY=
- CANARY_MANDRILL_API_KEY=
- CANARY_SENDGRID_API_KEY=
- CANARY_PUBLIC_IP=<instead of using a domain>
- CANARY_PUBLIC_DOMAIN=<instead of using an IP>
- CANARY_ALERT_EMAIL_FROM_ADDRESS=noreply@yourdomain.com
- CANARY_ALERT_EMAIL_FROM_DISPLAY="Canarytoken Mailer"
- CANARY_ALERT_EMAIL_SUBJECT="Alert"
- CANARY_SMTP_USERNAME=
- CANARY_SMTP_PASSWORD=
- CANARY_SMTP_SERVER=smtp.gmail.com
- CANARY_SMTP_PORT=587
- CANARY_WEB_IMAGE_UPLOAD_PATH=/uploads
- LOG_FILE=switchboard.log

Please note that when choosing which email provider you would like to use, you **MUST** only provide
information related to that provider. E.g. if you have `CANARY_MAILGUN_API_KEY` then you must remove the others such as
`CANARY_SENDGRID_API_KEY` and `CANARY_MANDRILL_API_KEY`. 

Lastly, we have added the ability to specify your own AWSID lambda so that you may host your own. The setting is placed in
`frontend.env` under `CANARY_AWSID_URL`. If this value is not specified, it will use our default hosted lambda. 

