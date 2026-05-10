# pylint: disable=locally-disabled, multiple-statements, fixme, line-too-long, missing-module-docstring, missing-function-docstring, used-before-assignment, no-value-for-parameter

import glob
import os
import shutil
import sys
import argparse
from datetime import datetime
import configparser
import subprocess
import logging

PATH = os.getcwd()
SEPARATOR = "-" * 80


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
    config.read(os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.ini"))
    return {
        "root_path": config.get("General", "root_path"),
        "proj_url": config.get("General", "proj_url"),
        "admin_email": config.get("General", "admin_email"),
        "default_plugins": config.get("General", "default_plugins").split(", "),
        "db_host": config.get("Database", "db_host"),
    }


def require_wp_installed(action):
    try:
        subprocess.check_output(
            "wp core is-installed", shell=True, stderr=subprocess.DEVNULL
        )
    except subprocess.CalledProcessError:
        print("It looks like you aren't in a project folder, process failed")
        logging.error(
            "Tried %s and failed. WordPress is not installed in %s and does not seem to be a project folder",
            action,
            PATH,
        )
        sys.exit(1)


def initial():
    slug = input("Enter project slug: ")
    title = input("Site title: ")

    print("Starting WordPress setup...")
    os.chdir(config_data["root_path"])
    print(f"Creating {slug} folder...")
    os.mkdir(slug)
    os.chdir(os.path.join(config_data["root_path"], slug))

    print(SEPARATOR)
    print("Installing WordPress...")
    os.system("wp core download")

    print(SEPARATOR)
    print("Generating wp-config...")
    os.system(
        f"wp config create --dbname={slug} --dbuser=root --dbpass=root --dbhost={config_data['db_host']}"
    )

    print(SEPARATOR)
    print("Creating database...")
    os.system("wp db create")

    print(SEPARATOR)
    print("WP core install...")
    os.system(
        f'wp core install --url="{config_data["proj_url"]}/{slug}" --title="{title}" --admin_user="root" --admin_password="root" --admin_email="{config_data["admin_email"]}"'
    )

    print(SEPARATOR)
    print("Removing default plugins...")
    os.system("wp plugin delete akismet hello")

    print(SEPARATOR)
    if "none" in config_data["default_plugins"]:
        print("No default plugins specified, skipping to next step...")
    else:
        print("Adding plugins specified in config.ini...")
        os.system("wp plugin install " + " ".join(config_data["default_plugins"]))

    print(SEPARATOR)
    os.system("git init")

    print(SEPARATOR)
    print("Adding gitignore...")
    shutil.copy(
        os.path.join(os.path.dirname(__file__), "files", ".gitignore"),
        os.path.join(config_data["root_path"], slug),
    )

    print(SEPARATOR)
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

    backup_path = os.path.join(PATH, "db-backup")
    if not os.path.exists(backup_path):
        print("It doesn't so creating one...")
        os.makedirs(backup_path)
    else:
        print("It does so just backing up the db...")

    dt_string = datetime.now().strftime("%m-%d-%Y-%H%M%S")
    os.chdir(backup_path)
    os.system(f"wp db export {dt_string}.sql")


def importdb(db_name):
    backup_path = os.path.join(PATH, "db-backup")
    if not os.path.exists(backup_path):
        print("The db-backup folder does not exist, import failed. Try backing up a db first")
        logging.error("The db-backup folder does not exist, database import failed")
        return

    sql_files = glob.glob(os.path.join(backup_path, "*.sql"))
    if not sql_files:
        print("No SQL files found in db-backup folder, import failed. Try backing up a db first")
        logging.error("No SQL files found in db-backup folder, database import failed")
        return

    if db_name:
        print(f"Searching for specified {db_name} file...")
        target = os.path.join(backup_path, db_name)
        if os.path.isfile(target):
            os.system(f"wp db import {target}")
        else:
            print(f"{db_name} file not found, import failed")
            logging.error(
                "%s was not found in the db-backup folder, database import failed",
                db_name,
            )
    else:
        print("Finding the latest backup since a specific one was not provided...")
        latest_file = max(sql_files, key=os.path.getmtime)
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
        return


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
        require_wp_installed("updating core")
        updatecore()
    elif args.update_plugins:
        require_wp_installed("updating plugins")
        updateplugins()
    elif args.backup_db:
        require_wp_installed("backing up database")
        backup()
    elif args.import_db:
        require_wp_installed("importing database")
        importdb(args.import_db)
    elif args.search_db:
        require_wp_installed("searching database")
        searchdb(args.search_db)


if __name__ == "__main__":
    os.makedirs(os.path.join(os.path.dirname(__file__), "logs"), exist_ok=True)

    logging.basicConfig(
        filename=f"{os.path.dirname(__file__)}/logs/nova.log",
        filemode="a",
        format="%(asctime)s - %(levelname)s - %(message)s",
        style="%",
        datefmt="%Y-%m-%d %H:%M",
    )

    config_data = read_config()

    main()
