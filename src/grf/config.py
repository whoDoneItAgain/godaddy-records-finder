import argparse
import logging

LOGGER = logging.getLogger("grf")


def get_config_args():
    # Define the parser
    parser = argparse.ArgumentParser(description="GoDaddy Record Finder")
    parser.add_argument(
        "--debug-logging",
        action="store_true",
    )
    parser.add_argument(
        "--info-logging",
        action="store_true",
    )
    parser.add_argument(
        "--api-limit",
        action="store",
        default=50,
        type=int,
        choices=range(1, 501),
        help="Must be between 1 and 500. (default: %(default)s)",
    )
    parser.add_argument(
        "--endpoint",
        action="store",
        type=str,
        choices=["https://api.godaddy.com", "https://api.ote-godaddy.com"],
        required=True,
    )
    parser.add_argument("--key", action="store", type=str, required=True)
    parser.add_argument("--secret", action="store", type=str, required=True)
    parser.add_argument(
        "--interesting-records-file", action="store", type=str, required=True
    )
    parser.add_argument("--domain-status", action="store", type=str, default="ACTIVE")
    parser.add_argument(
        "--export-file",
        action="store",
        type=str,
        default="tmp/export.json",
    )

    parser.add_argument(
        "--record-count",
        action="store",
        type=int,
    )

    args = parser.parse_args()

    return args


def configure_logging(debug_logging: bool = False, info_logging: bool = False):
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    if debug_logging:
        LOGGER.setLevel(logging.DEBUG)
    elif info_logging:
        LOGGER.setLevel(logging.INFO)
    else:
        LOGGER.setLevel(logging.NOTSET)
    log_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    ch.setFormatter(log_formatter)

    # make sure all other log handlers are removed before adding it back
    for handler in LOGGER.handlers:
        LOGGER.removeHandler(handler)
    LOGGER.addHandler(ch)
