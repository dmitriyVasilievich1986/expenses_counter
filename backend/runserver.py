#!/usr/bin/env python3
from django.core.management import execute_from_command_line
from django.db.utils import OperationalError
from argparse import ArgumentParser
from django.db import connections
from dotenv import load_dotenv
from os import environ
from time import sleep
from enum import Enum
import logging
import sys

logger = logging.getLogger(__name__)


class Modes(Enum):
    migration = "migration"
    runserver = "runserver"


def parse_args():
    parser = ArgumentParser(description="simple script to start django project")
    parser.add_argument(
        "--mode",
        "-M",
        help="mode in which project will start",
        choices=list(Modes.__members__),
        default="runserver",
    )
    return parser.parse_args()


def load_enviroments():
    load_dotenv()
    load_dotenv("config.env")


def execute_migrations(is_need_exit: bool):
    execute_from_command_line([__name__, "makemigrations"])
    execute_from_command_line([__name__, "migrate"])
    if is_need_exit:
        logger.info("Migrations executed. Exiting...")
        sys.exit(0)


def execute_runserver():
    HOST = environ.get("HOST", "0.0.0.0")
    PORT = environ.get("PORT", "3000")
    execute_from_command_line([__name__, "runserver", f"{HOST}:{PORT}"])


def runserver():
    for try_count in range(1, 6):
        try:
            connections["default"].cursor()
            logger.info(f"connected successfuly")
            return execute_runserver
        except OperationalError as e:
            x = connections["default"].settings_dict
            error = (
                f"{try_count} try: {e.args[1]} credentials - {x['USER']}:{x['PASSWORD']}"
                if len(e.args) > 1
                else e
            )
            logger.error(error)
        sleep(10)
    raise OperationalError


if __name__ == "__main__":
    namespace = parse_args()
    load_enviroments()
    app_run = runserver()
    execute_migrations(Modes[namespace.mode] is Modes.migration)
    app_run()
