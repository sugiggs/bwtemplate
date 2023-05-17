### bwtemplate

This repository contains the necessary instructions to set up and configure `bwtemplate` for the Bitwarden Password Manager.
### Customizing Email Templates

Currently, the customization options are limited to the invitation email and welcome email. To modify the content of these emails, follow the steps below:

1. Locate the `invitation.html` and `welcome.html` files.
2. Edit these files to customize the HTML content of the outgoing emails.
3. Save your changes.

The modified `invitation.html` and `welcome.html` files will be used as the new email templates, replacing the default content in the outgoing emails.

#### Directory Setup

Create the following directories:

```bash
cd /opt/bitwarden/bwdata/
mkdir bwtemplate
mkdir logs/bwtemplate
```

#### File Download

Download the necessary files and extract them into the `bwdata/bwtemplate/` directory.

#### Rename File

Rename the file `bwtemplate.override.env.example` to `bwtemplate.override.env`.

```bash
mv bwtemplate.override.env.example bwtemplate.override.env
```

#### SMTP Configuration

Modify the following SMTP details in `bwtemplate.override.env`:

```bash
bwtemplate__mail__smtp__host=smtp.example.com
bwtemplate__mail__smtp__port=587
bwtemplate__mail__smtp__username=SMTP_username
bwtemplate__mail__smtp__password=SMTP_password
bwtemplate__from=IT Dept <it@example.com>
bwtemplate__subject_invitation=[IT Dept] Invitation: Bitwarden Password Manager
bwtemplate__subject_welcome=[IT Dept] Welcome: Bitwarden Password Manager
```

#### Docker Configuration

Change to the `bwdata/docker/` directory:

```bash
cd ../docker/
```

Modify or create `docker-compose.override.yml` and add the following lines:

```yaml
services:
  bwtemplate:
    image: sugiggs/bwtemplate:latest
    container_name: bwtemplate
    restart: always
    volumes:
      - ../bwtemplate:/etc/bitwarden
      - ../logs/bwtemplate:/etc/bitwarden/logs
    env_file:
      - ../env/uid.env
      - ../bwtemplate/bwtemplate.override.env
    networks:
      - default
      - public
```

#### Global SMTP Settings

Modify the SMTP settings in `bwdata/env/global.override.env` as follows:

```bash
globalSettings__mail__smtp__host=bwtemplate
globalSettings__mail__smtp__port=25
globalSettings__mail__smtp__ssl=false
globalSettings__mail__smtp__username=
globalSettings__mail__smtp__password=
```

#### Email Template Keywords

The following keywords will be replaced in the email template:

- `{ORG_NAME}`: Will be replaced with the organization name.
- `{EXPIRY_DATE}`: Will be replaced with the invitation expiry date.
- `{JOIN_LINK}`: Will be replaced with the URL of the invitation link.
