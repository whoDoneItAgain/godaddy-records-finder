import json
import logging
import time
from pathlib import Path

import requests

LOGGER = logging.getLogger("grf")


def get(
    api_key: str,
    api_limit: int,
    api_secret: str,
    domain_name: str,
    endpoint_url: str,
    interesting_records: str,
) -> dict:

    request_header: dict = {
        "Accept": "application/json",
        "Authorization": f"sso-key {api_key}:{api_secret}",
    }

    request_params: dict = {"limit": api_limit}
    LOGGER.debug(f"Request Parameters: {request_params}")

    api_path = f"/v1/domains/{domain_name}/records"

    domain_records_list: list = []
    more_response: bool = True

    LOGGER.info(f"Domain: {domain_name} - Getting Domain Records.")

    interesting_records_file = Path(interesting_records).absolute()

    with open(interesting_records_file) as ir:
        interesting_records_loads: dict = json.load(ir)

    interesting_records_types: list = list(interesting_records_loads.keys())

    i: int = 0
    while more_response:

        LOGGER.debug(f"Api Call Url: {endpoint_url}{api_path}")
        LOGGER.debug(f"Api Call Params: {request_params}")
        LOGGER.debug(f"Api Call Header: {request_header}")

        while True:

            try:

                api_response = requests.get(
                    f"{endpoint_url}{api_path}",
                    params=request_params,
                    headers=request_header,
                )

                response_data = api_response.json()

                if api_response.status_code == 429:
                    LOGGER.warning("Too many requests received within interval")
                    LOGGER.warning(
                        f"Retying After {response_data['retryAfterSec']} seconds"
                    )
                    time.sleep(response_data["retryAfterSec"])

                else:
                    break

            except Exception as e:
                LOGGER.debug(e)

        if i == 0 and len(response_data) < api_limit:
            LOGGER.debug(
                f"Domain: {domain_name} - Retrieved all {len(response_data)} records."
            )
        elif i == 0 and len(response_data) == api_limit:
            LOGGER.debug(
                f"Domain: {domain_name} - Retrieved first {api_limit} records."
            )
        elif len(response_data) == api_limit:
            LOGGER.debug(f"Domain: {domain_name} - Retrieved next {api_limit} records.")
        elif len(response_data) < api_limit:
            LOGGER.debug(
                f"Domain: {domain_name} - Retrieved last {len(response_data)} records."
            )
        i += 1

        if len(response_data) < api_limit:
            more_response = False
        else:
            request_params["offset"] = int(len(response_data))

        for record in response_data:
            LOGGER.info(
                f"Domain: {domain_name} - Type: {record['type']} - Name: {record['name']} - Data: {record['data']}"
            )

            if record["type"] not in interesting_records_types:
                LOGGER.info(f"Type: {record['type']} - Not Interested")
            else:
                interesting_records_names: list = list(
                    interesting_records_loads[record["type"]].keys()
                )
                LOGGER.info(
                    f"Type: {record['type']} - Interesting Record Names: {interesting_records_names}"
                )
                if record["name"] not in interesting_records_names:
                    LOGGER.info(
                        f"Type: {record['type']} - Name: {record['name']} - Not Interested"
                    )
                else:
                    match record["type"]:
                        case "A":
                            interesting_records_data: list = interesting_records_loads[
                                record["type"]
                            ][record["name"]]
                            LOGGER.info(
                                f"Type: {record['type']} - Name: {record['name']} - Interesting Record Data: {interesting_records_data}"
                            )

                            if len(interesting_records_data) == 0:
                                domain_records_list_entry: dict = {
                                    record["name"]: record["data"]
                                }
                                domain_records_list.append(domain_records_list_entry)
                            elif record["data"] in interesting_records_data:
                                domain_records_list_entry: dict = {
                                    record["name"]: record["data"]
                                }
                                domain_records_list.append(domain_records_list_entry)
                        case "CNAME":
                            search_methods: list = list(
                                interesting_records_loads[record["type"]][
                                    record["name"]
                                ].keys()
                            )
                            LOGGER.info(
                                f"Interesting Record Data Search Methods: {search_methods}"
                            )
                            for method in search_methods:
                                interesting_records_data_values = (
                                    interesting_records_loads[record["type"]][
                                        record["name"]
                                    ][method]
                                )
                                match str(method):
                                    case "endsWith":
                                        if (record["data"]).endswith(
                                            tuple(interesting_records_data_values)
                                        ):
                                            domain_records_list_entry: dict = {
                                                record["name"]: record["data"]
                                            }
                                            domain_records_list.append(
                                                domain_records_list_entry
                                            )
                                    case _:
                                        LOGGER.info(
                                            f"Domain: {domain_name} - Record Type: {record['type']} - Record Name: {record['name']} - Search Method: {method} - Unhandled Record Search Method"
                                        )
                        case _:
                            LOGGER.info(
                                f"Domain: {domain_name} - Record Type: {record['type']} - Unhandled Record Type"
                            )
                            LOGGER.debug(record)

    LOGGER.info(f"Domain: {domain_name} - Getting Domain Records. Complete.")

    interesting_domain_records: dict = {
        domain_name: domain_records_list,
    }

    return interesting_domain_records
