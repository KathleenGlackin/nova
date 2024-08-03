# Nova

A python build script to help manage local WordPress development using the WP-CLI.

## Prerequisites

This script requires [Python](https://www.python.org/downloads/) and the [WP-CLI](https://wp-cli.org/) in order to run.

I would also recommend making an alias but do whatever floats your boat.

```python
alias nova="python3 ~/example_path/nova/nova.py"
```

## Installation

This script requires [Python](https://www.python.org/downloads/) and the [WP-CLI](https://wp-cli.org/) in order to run.

I would also recommend making an alias but do whatever floats your boat.

```python
alias nova="python3 ~/example_path/nova/nova.py"
```

## Usage

Fill out the variables in the config.ini file before using the script, here's a breakdown of what they are:

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
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)