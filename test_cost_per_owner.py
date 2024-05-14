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

import unittest
from unittest.mock import patch, call, MagicMock
from cost_per_owner import get_costs, add_costs, print_report


class TestCostPerOwner(unittest.TestCase):
    @patch("boto3.client")
    def test_get_costs(self, mock_client):
        """
        Mocks the boto3 clent and tests that the get_costs function is called with the correct parameters.
        """
        mock_client = MagicMock()
        mock_client.return_value = mock_client
        mock_client.get_cost_and_usage.return_value = "mock_response"
        start = "2024-01-01"
        end = "2024-01-30"

        result = get_costs(mock_client, start, end)

        mock_client.get_cost_and_usage.assert_called_once_with(
            TimePeriod={"Start": start, "End": end},
            Granularity="MONTHLY",
            Metrics=["UnblendedCost"],
            GroupBy=[{"Type": "TAG", "Key": "Owner"}],
        )
        self.assertEqual(result, "mock_response")

    def test_add_costs(self):
        """
        Tests that costs are properly added when there are duplicate owners.
        """
        response = {
            "ResultsByTime": [
                {
                    "Groups": [
                        {
                            "Keys": ["Owner$test"],
                            "Metrics": {"UnblendedCost": {"Amount": "100.00"}},
                        },
                        {
                            "Keys": ["Owner$test"],
                            "Metrics": {"UnblendedCost": {"Amount": "100.00"}},
                        },
                    ]
                }
            ]
        }

        result = add_costs(response)
        self.assertEqual(result, {"test": 200.00})

    @patch("builtins.print")
    def test_print_report(self, mock_print):
        """
        Tests that the report is formatted as expected.
        """
        costs = {"test": 100.00}
        print_report(costs)
        calls = [
            call("Owner                       Cost"),
            call("==================== ============"),
            call("test                | $    100.00"),
        ]
        mock_print.assert_has_calls(calls, any_order=False)
