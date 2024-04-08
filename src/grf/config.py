import argparse
import logging

LOGGER = logging.getLogger("grf")

API_LIMIT_RANGE = range(1, 501)


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
        default=500,
        type=int,
        help=f"Must be between {API_LIMIT_RANGE[0]} - {API_LIMIT_RANGE[-1]}. (default: %(default)s)",
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

    if args.api_limit not in API_LIMIT_RANGE:
        LOGGER.error(
            f"Api Limit not within range of {API_LIMIT_RANGE[0]} - {API_LIMIT_RANGE[-1]}"
        )
        quit(1)

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
