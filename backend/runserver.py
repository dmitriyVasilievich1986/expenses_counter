#!/usr/bin/env python3
from django.core.management import execute_from_command_line
from argparse import ArgumentParser, Namespace
from django.db.utils import OperationalError
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


def parse_args(*args, **kwargs) -> Namespace:
    parser = ArgumentParser(description="simple script to start django project")
    parser.add_argument(
        "--mode",
        "-M",
        help="mode in which project will start",
        choices=list(Modes.__members__),
        default="runserver",
    )
    return parser.parse_args()


def load_enviroments(*args, **kwargs) -> None:
    load_dotenv()
    load_dotenv("config.env")


def execute_migrations(*args, **kwargs) -> None:
    execute_from_command_line([__name__, "makemigrations"])
    execute_from_command_line([__name__, "migrate"])


def execute_runserver(*args, **kwargs) -> None:
    execute_migrations()
    HOST = environ.get("HOST", "0.0.0.0")
    PORT = environ.get("PORT", "3000")
    execute_from_command_line([__name__, "runserver", f"{HOST}:{PORT}"])


def check_connection(*args, **kwargs) -> None:
    for try_count in range(1, 6):
        try:
            connections["default"].cursor()
            logger.info(f"connected successfuly")
            return
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
    namespace: Namespace = parse_args()

    load_enviroments()
    check_connection()

    if Modes[namespace.mode] is Modes.migration:
        execute_migrations()
    elif Modes[namespace.mode] is Modes.runserver:
        execute_runserver()
