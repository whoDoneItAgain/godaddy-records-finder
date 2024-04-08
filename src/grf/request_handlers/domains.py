import logging
import time

import requests

LOGGER = logging.getLogger("grf")


def get(
    api_key: str,
    api_limit: int,
    api_secret: str,
    domain_status: str,
    endpoint_url: str,
    record_count: int | None,
) -> tuple[list[str], list[str], list[str]]:

    request_header: dict = {
        "Accept": "application/json",
        "Authorization": f"sso-key {api_key}:{api_secret}",
    }

    request_params: dict = {
        "limit": api_limit,
        "statuses": [domain_status],
    }
    LOGGER.debug(f"Request Parameters: {request_params}")

    api_path = "/v1/domains"

    gd_domain_list: list = []
    external_domain_list: list = []
    skipped_domain_list: list = []
    more_domains: bool = True

    LOGGER.debug("Getting Domain Names")

    i: int = 0
    while more_domains:

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
            LOGGER.debug(f"Retrieved all {len(response_data)} Domain Names.")
        elif i == 0 and len(response_data) == api_limit:
            LOGGER.debug(f"Retrieved first {api_limit} Domain Names.")
        elif len(response_data) == api_limit:
            LOGGER.debug(f"Retrieved next {api_limit} Domain Names.")
        elif len(response_data) < api_limit:
            LOGGER.debug(f"Retrieved last {len(response_data)} Domain Names.")

        i += 1

        if len(response_data) < api_limit:
            more_domains = False
        else:
            request_params["marker"] = response_data[-1]["domain"]

        for rdd in response_data:
            break_it: bool = False
            if rdd["nameServers"] is None:
                LOGGER.info(f"Domain Name - {rdd['domain']} - Confirming nameservers.")
                nameservers = get_domain_nameservers(
                    api_key=api_key,
                    api_secret=api_secret,
                    domain_name=rdd["domain"],
                    endpoint_url=endpoint_url,
                )
                if nameservers is None:
                    LOGGER.info(
                        f"Domain Name - {rdd['domain']} - Cannot confirm nameservers. Skipping"
                    )
                    skipped_domain_list.append(rdd["domain"])
                elif any("domaincontrol.com" in s for s in nameservers):
                    LOGGER.info(f"Domain Name - {rdd['domain']} - GoDaddy nameservers.")
                    gd_domain_list.append(rdd["domain"])
                else:
                    LOGGER.info(
                        f"Domain Name - {rdd['domain']} - External nameservers."
                    )
                    external_domain_list.append(rdd["domain"])

            elif any("domaincontrol.com" in s for s in rdd["nameServers"]):
                LOGGER.info(f"Domain Name - {rdd['domain']} - GoDaddy nameservers.")
                gd_domain_list.append(rdd["domain"])
            else:
                LOGGER.info(f"Domain Name - {rdd['domain']} - Skipping")
                skipped_domain_list.append(rdd["domain"])

            total_domains_count = (
                len(gd_domain_list)
                + len(external_domain_list)
                + len(skipped_domain_list)
            )
            LOGGER.info(
                f"Record Count: {record_count} - Total Domain Count: {total_domains_count}"
            )
            if record_count != 0 and total_domains_count == record_count:
                break_it: bool = True
                break

        if break_it:
            break

    LOGGER.info("Getting Domain Names. Complete.")

    return gd_domain_list, external_domain_list, skipped_domain_list


def get_domain_nameservers(
    api_key: str,
    api_secret: str,
    domain_name: str,
    endpoint_url: str,
) -> list[str] | None:

    request_header: dict = {
        "Accept": "application/json",
        "Authorization": f"sso-key {api_key}:{api_secret}",
    }

    request_params: dict = {}
    LOGGER.debug(f"Request Parameters: {request_params}")

    api_path = f"/v1/domains/{domain_name}"

    LOGGER.debug(f"Getting Domain Name - {domain_name}")

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

    LOGGER.debug(f"Getting Domain Name - {domain_name}. Complete")

    return response_data["nameServers"]
