#!/usr/bin/env python
#
# Copyright 2024 Austin Orth
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import boto3
import logging
from datetime import date, timedelta
from collections import defaultdict

AWS_TAG = "Owner"
AWS_REGION = "us-east-1"

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)


def get_costs(client, start, end):
    """
    Fetches the monthly cost for each 'Owner' tag.
    """
    response = client.get_cost_and_usage(
        TimePeriod={"Start": start, "End": end},
        Granularity="MONTHLY",
        Metrics=["UnblendedCost"],
        GroupBy=[{"Type": "TAG", "Key": "Owner"}],
    )
    return response


def add_costs(response):
    """
    Adds the cost for each Owner. Accounts for when last 30 days crosses a month boundary.
    """
    costs = defaultdict(float)
    for result_by_time in response["ResultsByTime"]:
        for group in result_by_time["Groups"]:
            owner = group["Keys"][0].split("$")[1]
            cost = round(float(group["Metrics"]["UnblendedCost"]["Amount"]), 2)
            costs[owner] += cost
    return costs


def print_report(costs):
    """
    Prints a report showing the cost of each 'Owner' tag.
    """
    costs = sorted(costs.items(), key=lambda x: x[1], reverse=True)
    print(f'{"Owner":<20}{"Cost":>12}')
    print(f'{"="*20} {"="*12}')
    for owner, cost in costs:
        print(f"{owner:<20}| ${cost:>10.2f}")


def main():  # pragma: no cover
    """
    Calculates the start and end dates for the last 30 days, then runs the cost analysis.
    """
    end = date.today()
    start = end - timedelta(days=30)
    start = start.strftime("%Y-%m-%d")
    end = end.strftime("%Y-%m-%d")

    # Create Cost Explorer client
    client = boto3.client("ce", region_name=AWS_REGION)

    logging.info("Fetching costs...")
    response = get_costs(client, start, end)

    logging.info("Adding costs per owner...")
    results = add_costs(response)

    logging.info("Costs calculated. Printing results...")
    print_report(results)


if __name__ == "__main__":  # pragma: no cover
    main()
