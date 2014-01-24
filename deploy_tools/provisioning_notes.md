Provisioning a new site
=======================

## Required packages:

*nginx
*Python 3
*Git
*pip
*virtualenv

eg, on Ubuntu

	sudo apt-get install nginx git python3 python-pip python-dev
	sudo pip install virtualenv

## Nginx Virtual Host config

*see nginx.template.conf
*replace SITENAME with, eg, staging.mydomain.com

## Upstart job

*see gunicorn-upstart.template.conf
*replace SITENAME with, eg, staging.mydomain.com

# Directory structure:
Assume we have a user account at /home/username

/home/username
			/sites
				/SITENAME
						/database
						/source
						/static
						/virtualenv
