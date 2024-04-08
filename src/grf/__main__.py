import json
import logging
from pathlib import Path

from .config import configure_logging, get_config_args
from .request_handlers import domain_records, domains

LOGGER = logging.getLogger("grf")


def main():

    config_args = get_config_args()
    print(config_args)
    configure_logging(
        debug_logging=config_args.debug_logging, info_logging=config_args.info_logging
    )

    gd_domain_list, external_domain_list, skipped_domain_list = domains.get(
        api_key=config_args.key,
        api_limit=config_args.api_limit,
        api_secret=config_args.secret,
        domain_status=config_args.domain_status,
        endpoint_url=config_args.endpoint,
        record_count=config_args.record_count,
    )

    export_file = Path(config_args.export_file).absolute()

    with open(export_file, "w") as ef:
        domain_list_dict: dict = {
            "Domain Names": gd_domain_list,
            "External Domain Names": external_domain_list,
            "Skipped Domain Names": skipped_domain_list,
        }

        json.dump(domain_list_dict, ef, indent=2)

    for d in gd_domain_list:
        domain_records_list = domain_records.get(
            api_key=config_args.key,
            api_limit=config_args.api_limit,
            api_secret=config_args.secret,
            domain_name=d,
            endpoint_url=config_args.endpoint,
            interesting_records=config_args.interesting_records_file,
        )

        LOGGER.debug(f"Domain Record List: {domain_records_list}")

        with open(export_file, "r") as ef:
            export_list: dict = json.load(ef)

        export_list.update(domain_records_list)
        with open(export_file, "w") as ef:
            json.dump(export_list, ef, indent=2)


if __name__ == "__main__":
    main()
