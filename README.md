# Nova

A python build script to help manage local WordPress development using the WP-CLI.

## Prerequisites

This script requires [Python](https://www.python.org/downloads/) and the [WP-CLI](https://wp-cli.org/) in order to run.

I would also recommend making an alias but do whatever floats your boat.

```python
alias nova="python3 ~/example_path/nova/nova.py"
```

*I have only tested this with MAMP so far and make no promises on it working flawlessly using any other dev environment yet*

## Installation

Clone the repo
```python
git clone https://github.com/KathleenGlackin/nova.git
```

Fill out the variables in the config.ini file before using the script, here's a breakdown of what they are:

```python
[General]
# the root folder that contains your WordPress installations
root_path = /example/path/w

# the base URL for your projects
proj_url = http://localhost:8888

# the email you would like set as the admin in the WordPress backend by default
admin_email = admin@email.com

# any default plugins you would like added, if you don't want any added by default then leave this blank
default_plugins = wordpress-seo, blocks-kit

[Database]
# the database host URL
db_host = 127.0.0.1:8889
```

## Usage

```python
# initializes a WordPress project
nova --initial

# Updates WordPress core
nova --update-core

# Updates all WordPress plugins
nova --update-plugins

# Updates specific WordPress plugins (Yoast SEO in this example)
nova --update-plugins wordpress-seo

# Backs up the database to a db-backup folder in the project root
nova --backup-db

# Imports the latest database from the db-backup folder
nova --import-db

# Imports a specified database in the db-backup folder
nova --import-db test.sql

# Searches through the database using the first parameter provided and replaces it with the second parameter. A backup of the database is automatically done before this is run.
nova --search-db http://localhost https://www.example.com
```