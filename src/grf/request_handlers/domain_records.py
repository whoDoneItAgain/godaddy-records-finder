import json
import logging
import time
from pathlib import Path

import requests

from .exceptions import StatusCodeException

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

    LOGGER.debug(f"Domain: {domain_name} - Getting Domain Records.")

    interesting_records_file = Path(interesting_records).absolute()

    with open(interesting_records_file) as ir:
        interesting_records_loads: dict = json.load(ir)

    interesting_records_types: list = list(interesting_records_loads.keys())

    i: int = 0
    while more_response:
        try:
            LOGGER.debug(f"Api Call Url: {endpoint_url}{api_path}")
            LOGGER.debug(f"Api Call Params: {request_params}")
            LOGGER.debug(f"Api Call Header: {request_header}")
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
            if api_response.status_code != 200:
                raise StatusCodeException(api_response)

            if i == 0 and len(response_data) < api_limit:
                LOGGER.debug(
                    f"Domain: {domain_name} - Retrieved all {len(response_data)} records."
                )
            elif i == 0 and len(response_data) == api_limit:
                LOGGER.debug(
                    f"Domain: {domain_name} - Retrieved first {api_limit} records."
                )
            elif len(response_data) == api_limit:
                LOGGER.debug(
                    f"Domain: {domain_name} - Retrieved next {api_limit} records."
                )
            elif len(response_data) < api_limit:
                LOGGER.debug(
                    f"Domain: {domain_name} - Retrieved last {len(response_data)} records."
                )
            i += 1

        except StatusCodeException as e:
            match e.api_response.status_code:
                case 400:
                    raise Exception("Malformed Request")
                case 401:
                    raise Exception("Authentication info not sent or invalid")
                case 403:
                    raise Exception("Authenticated user is not allowed access")
                case 404:
                    raise Exception("Resource Not Found")
                case 422:
                    raise Exception("Record does not fulfill the schema")
                case 429:
                    pass
                case 500:
                    raise Exception("Internal Server Error")
                case 504:
                    raise Exception("Gateway Timeout")
                case _:
                    raise Exception(
                        f"Unknown Exception. Status Code: {e.api_response.status_code}"
                    )

        if len(response_data) < api_limit:
            more_response = False
        else:
            request_params["offset"] = int(len(response_data))

        for record in response_data:
            LOGGER.debug(f"Domain: {domain_name} - Records")
            LOGGER.debug(record)
            if record["type"] in interesting_records_types:
                LOGGER.debug(f"Domain: {domain_name} - Contains {record['type']}")
                match record["type"]:
                    case "A":
                        interesting_records_names: list = list(
                            interesting_records_loads[record["type"]].keys()
                        )
                        LOGGER.debug(
                            f"Interesting Record Names: {interesting_records_names}"
                        )
                        if record["name"] in interesting_records_names:
                            interesting_records_data: list = interesting_records_loads[
                                record["type"]
                            ][record["name"]]
                            LOGGER.debug(
                                f"Interesting Record Data: {interesting_records_data}"
                            )
                            if len(interesting_records_data) == 0:
                                domain_records_list_entry: dict = {
                                    record["type"]: "asdf"
                                }
                                domain_records_list.append(domain_records_list_entry)
                            elif record["data"] in interesting_records_data:
                                domain_records_list_entry: dict = {
                                    record["type"]: "asdf"
                                }
                                domain_records_list.append(domain_records_list_entry)
                    case _:
                        LOGGER.debug(
                            f"Domain: {domain_name} - Record Type: {record['type']} - Unhandled Record Type"
                        )
                        LOGGER.debug(record)

    LOGGER.debug(f"Domain: {domain_name} - Getting Domain Records. Complete.")

    interesting_domain_records: dict = {
        domain_name: domain_records_list,
    }

    return interesting_domain_records
