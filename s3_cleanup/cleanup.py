#!/usr/bin/env python3
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

import argparse
import boto3
import logging

logging.basicConfig(level=logging.INFO)


def get_args():
    """
    Get arguments from the command line.
    """
    parser = argparse.ArgumentParser(
        description="""
        Delete all deployment folders except the most recent X folders in an S3 bucket.
        Defaults to keeping the 5 most recent folders.
        """
    )
    parser.add_argument("--bucket", required=True, help="Bucket name")
    parser.add_argument(
        "--keep", type=int, default=5, help="Number of most recent folders to keep"
    )
    return parser.parse_args()


def cleanup(s3, bucket, keep_count):
    """
    Uses a paginator to fetch all folders from the given bucket,
    sorts them by last modified date, and deletes all but the most recent X.
    """

    # Create a paginator to fetch objects in chunks (reduces memory usage for large buckets)
    paginator = s3.get_paginator("list_objects_v2")
    folders = []
    for page in paginator.paginate(Bucket=bucket, Delimiter="/"):
        if "CommonPrefixes" in page:
            folders.extend([prefix["Prefix"] for prefix in page["CommonPrefixes"]])

    # Get the last modified date of the first object in each folder
    folder_dates = {}
    for folder in folders:
        objects = s3.list_objects(Bucket=bucket, Prefix=folder, MaxKeys=1)["Contents"]
        folder_dates[folder] = objects[0]["LastModified"]

    # Sort folders by last modified date
    sorted_folders = sorted(folder_dates, key=folder_dates.get, reverse=True)

    # Get the keys of the folders to delete (all but the most recent X)
    to_delete = sorted_folders[keep_count:]

    # Delete the folders and their contents
    for fold in to_delete:
        # List all objects in the "folder"
        objects_to_delete = s3.list_objects(Bucket=bucket, Prefix=fold)["Contents"]

        # Prepare the list of objects to delete
        delete_list = [{"Key": obj["Key"]} for obj in objects_to_delete]

        # Delete the objects
        s3.delete_objects(Bucket=bucket, Delete={"Objects": delete_list})

    logging.info(
        "Deleted all folders except the most recent {keep_count} folders in the bucket '{args.bucket}'."
    )


def main():
    """
    Main function that gets args, creates the S3 client, and calls the cleanup function.
    """
    args = get_args()
    try:
        s3 = boto3.client("s3")
        cleanup(s3, args.bucket, args.keep)
    except Exception as e:
        logging.error(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
