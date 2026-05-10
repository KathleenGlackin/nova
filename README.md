# Nova

A Python build script to help manage local WordPress development using the WP-CLI.

## Prerequisites

This script requires [Python](https://www.python.org/downloads/), [Git](https://git-scm.com/), and the [WP-CLI](https://wp-cli.org/) in order to run.

*I have only tested this with MAMP so far and make no promises on it working flawlessly using any other dev environment yet*

## Installation

Clone the repo
```bash
git clone https://github.com/KathleenGlackin/nova.git
```

Make an alias to the script for ease of use:

```bash
alias nova="python3 ~/example_path/nova/nova.py"
```

Fill out the variables in the config.ini file before using the script, here's a breakdown of what they are:

```ini
[General]
# the root folder that contains your WordPress installations
root_path = /example/path/w

# the base URL for your projects
proj_url = http://localhost:8888

# the email you would like set as the admin in the WordPress backend by default
admin_email = admin@email.com

# any default plugins you would like added by default
# to skip adding plugins, set this to: none
default_plugins = wordpress-seo, blocks-kit

[Database]
# the database host URL
db_host = 127.0.0.1:8889
```

## Usage

```bash
# Initializes a WordPress project
nova -i / --initial

# Updates WordPress core
nova -uc / --update-core

# Updates all WordPress plugins
nova -up / --update-plugins

# Backs up the database to a db-backup folder in the project root
nova -bd / --backup-db

# Imports the latest database from the db-backup folder
nova -id / --import-db

# Imports a specified database from the db-backup folder
nova -id / --import-db test.sql

# Searches through the database using the first parameter provided and replaces it with the
# second parameter. A backup of the database is automatically done before this is run.
nova -sr / --search-db http://localhost https://www.example.com
```

## Roadmap
- reconfigure search & replace command to also work with multiple search terms/replacements
- improve the logging
- add more functionality from the WP CLI