# pylint: disable=locally-disabled, multiple-statements, fixme, line-too-long, missing-module-docstring, missing-function-docstring, used-before-assignment, no-value-for-parameter

import glob
import os
import sys
import argparse
from datetime import datetime
import configparser
import subprocess
import logging

PATH = os.getcwd()


def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
            It must be "yes" (the default), "no" or None (meaning
            an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == "":
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' " "(or 'y' or 'n').\n")


def read_config():
    config = configparser.ConfigParser()

    # get path to current script
    script_directory = os.path.dirname(os.path.abspath(__file__))

    config_file_path = os.path.join(script_directory, "config.ini")

    config.read(config_file_path)

    # Access values from the configuration file
    root_path = config.get("General", "root_path")
    proj_url = config.get("General", "proj_url")
    admin_email = config.get("General", "admin_email")
    default_plugins = config.get("General", "default_plugins").split(", ")

    db_host = config.get("Database", "db_host")

    config_values = {
        "root_path": root_path,
        "proj_url": proj_url,
        "admin_email": admin_email,
        "default_plugins": default_plugins,
        "db_host": db_host,
    }

    return config_values


def initial():
    slug = input("Enter project slug: ")
    title = input("Site title: ")

    print("Starting WordPress setup...")
    os.chdir(config_data["root_path"])
    print("Creating " + slug + " folder...")
    os.mkdir(f"{slug}")
    os.chdir(f"{config_data['root_path']}/{slug}")

    print(
        "--------------------------------------------------------------------------------"
    )
    print("Installing WordPress...")
    os.system("wp core download")

    print(
        "--------------------------------------------------------------------------------"
    )
    print("Generating wp-config...")
    os.system(
        f"wp config create --dbname={slug} --dbuser=root --dbpass=root --dbhost={config_data['db_host']}"
    )

    print(
        "--------------------------------------------------------------------------------"
    )
    print("Creating database...")
    os.system("wp db create")

    print(
        "--------------------------------------------------------------------------------"
    )
    print("WP core install...")
    os.system(
        f'wp core install --url="{config_data["proj_url"]}/{slug}" --title="{title}" --admin_user="root" --admin_password="root" --admin_email="{config_data["admin_email"]}"'
    )

    print(
        "--------------------------------------------------------------------------------"
    )
    print("Removing default plugins...")
    os.system("wp plugin delete akismet")
    os.system("wp plugin delete hello")

    print(
        "--------------------------------------------------------------------------------"
    )
    if "none" in config_data["default_plugins"]:
        print("No default plugins specified, skipping to next step...")
    else:
        print("Adding plugins specified in config.ini...")

        for i in config_data["default_plugins"]:
            os.system(f"wp plugin install {i}")

    print(
        "--------------------------------------------------------------------------------"
    )
    os.system("git init")

    print(
        "--------------------------------------------------------------------------------"
    )
    print("Adding gitignore...")
    #if using Windows then use copy since cp won't work
    cmd = f'cp {os.path.dirname(__file__)}/files/.gitignore {config_data["root_path"]}/{slug}'
    if os.name == 'nt':
        cmd = f'copy {os.path.dirname(__file__)}\\files\\.gitignore {config_data["root_path"]}\\{slug}'

    os.system(cmd)

    print(
        "--------------------------------------------------------------------------------"
    )
    print(
        f"Installation complete! Site can be found at {config_data['proj_url']}/{slug}"
    )


def updatecore():
    print("Updating core...")
    os.system("wp core update")


def updateplugins():
    print("Updating plugins...")
    os.system("wp plugin update --all")


def backup():
    print("Checking if backup folder exists...")

    backup_path = f"{PATH}/db-backup"
    if not os.path.exists(backup_path):
        print("It doesn't so creating one...")
        os.chdir(f"{PATH}")
        os.makedirs(backup_path)
    else:
        print("It does so just backing up the db...")

    now = datetime.now()
    dt_string = now.strftime("%m-%d-%Y-%H%M%S")
    os.chdir(f"{backup_path}")
    os.system(f"wp db export {dt_string}.sql")


def importdb(db_name):
    backup_path = f"{PATH}/db-backup"
    if not os.path.exists(backup_path):
        print(
            "The db-backup folder does not exist, import failed. Try backing up a db first"
        )
        logging.error("The db-backup folder does not exist, database import failed")
    else:
        if not glob.glob(f"{backup_path}/*.sql"):
            print(
                "No SQL files found in db-backup folder, import failed. Try backing up a db first"
            )
            logging.error(
                "No SQL files found in db-backup folder, database import failed"
            )
            sys.exit(0)
        else:
            if db_name:
                print(f"Searching for specified {db_name} file...")
                if glob.glob(f"{backup_path}/{db_name}"):
                    os.system(f"wp db import {backup_path}/{db_name}")
                else:
                    print(f"{db_name} file not found, import failed")
                    logging.error(
                        "%s was not found in the db-backup folder, database import failed",
                        db_name,
                    )
            else:
                print(
                    "Finding the latest backup since a specific one was not provided..."
                )
                backups = glob.glob(f"{backup_path}/*")
                latest_file = max(backups, key=os.path.getmtime)
                os.system(f"wp db import {latest_file}")


def searchdb(search):
    # backup db
    backup()

    print("Searching through database...")
    os.system(f"wp search-replace {search[0]} {search[1]} --dry-run")

    if query_yes_no("Do you want to run the search & replace for real?"):
        os.system(f"wp search-replace {search[0]} {search[1]}")
    else:
        print('Cancelling search & replace...')
        sys.exit(0)


def main():
    parser = argparse.ArgumentParser(
        description="This tool helps manage WordPress locally"
    )

    parser.add_argument(
        "-i",
        "--initial",
        action="store_true",
        help="Create WordPress site on machine, removes default native plugins (akismet and hello), adds default plugins specified in files/config.ini, and initializes git in the root of the project",
    )
    parser.add_argument("-uc", "--update-core", action="store_true", help="Update core")
    parser.add_argument(
        "-up", "--update-plugins", action="store_true", help="Update all plugins"
    )
    parser.add_argument(
        "-bd",
        "--backup-db",
        action="store_true",
        help="Back up the database to the db-backup folder",
    )
    parser.add_argument(
        "-id",
        "--import-db",
        nargs="?",
        const="",
        help="Imports a local database from the db-backup folder, defaults to the latest file if a specific one isn't provided",
    )

    parser.add_argument(
        "-sr",
        "--search-db",
        nargs="*",
        help="Searches through the database for the first parameter and replaces it with the second parameter. A backup of the db is automatically done before this is run.",
    )

    args = parser.parse_args()

    if args.initial:
        initial()
    elif args.update_core:
        # checking if we're in a WP installation to run the command
        try:
            subprocess.check_output(
                "wp core is-installed", shell=True, stderr=subprocess.DEVNULL
            )

            # if installed then update core
            updatecore()
        except subprocess.CalledProcessError:
            print("It looks like you aren't in a project folder, process failed")
            logging.error(
                "Tried updating core and failed. WordPress is not installed in %s and does not seem to be a project folder",
                PATH,
            )
            sys.exit(0)
    elif args.update_plugins:
        # checking if we're in a WP installation to run the command
        try:
            subprocess.check_output(
                "wp core is-installed", shell=True, stderr=subprocess.DEVNULL
            )

            # if installed then update plugins
            updateplugins()
        except subprocess.CalledProcessError:
            print("It looks like you aren't in a project folder, process failed")
            logging.error(
                "Tried updating plugins and failed. WordPress is not installed in %s and does not seem to be a project folder",
                PATH,
            )
            sys.exit(0)
    elif args.backup_db:
        # checking if we're in a WP installation to run the command
        try:
            subprocess.check_output(
                "wp core is-installed", shell=True, stderr=subprocess.DEVNULL
            )

            # if installed then run backup function
            backup()
        except subprocess.CalledProcessError:
            print("It looks like you aren't in a project folder, process failed")
            logging.error(
                "Tried backing up database and failed. WordPress is not installed in %s and does not seem to be a project folder",
                PATH,
            )
            sys.exit(0)
    elif args.import_db:
        # checking if we're in a WP installation to run the command
        try:
            subprocess.check_output(
                "wp core is-installed", shell=True, stderr=subprocess.DEVNULL
            )

            # if installed then run import function
            if not args.import_db:
                importdb()
            else:
                importdb(args.import_db)
        except subprocess.CalledProcessError:
            print("It looks like you aren't in a project folder, process failed")
            logging.error(
                "Tried importing database and failed. WordPress is not installed in %s and does not seem to be a project folder",
                PATH,
            )
            sys.exit(0)
    elif args.search_db:
        # checking if we're in a WP installation to run the command
        try:
            subprocess.check_output(
                "wp core is-installed", shell=True, stderr=subprocess.DEVNULL
            )

            searchdb(args.search_db)
        except subprocess.CalledProcessError:
            print("It looks like you aren't in a project folder, process failed")
            logging.error(
                "Tried searching database and failed. WordPress is not installed in %s and does not seem to be a project folder",
                PATH,
            )
            sys.exit(0)


if __name__ == "__main__":
    # create a folder for logs if one doesn't already exist
    if not os.path.exists(f"{os.path.dirname(__file__)}/logs"):
        os.mkdir(f"{os.path.dirname(__file__)}/logs")

    logging.basicConfig(
        filename=f"{os.path.dirname(__file__)}/logs/nova.log",
        filemode="a",
        format="%(asctime)s - %(levelname)s - %(message)s",
        style="%",
        datefmt="%Y-%m-%d %H:%M",
    )

    config_data = read_config()

    main()
