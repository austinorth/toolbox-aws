import boto3
import cleanup
from moto import mock_aws


def test_get_args(mocker):
    """
    Tests that user input is correctly parsed into arguments.
    """
    test_args = ["--bucket", "test-bucket", "--keep", "5"]
    mocker.patch("sys.argv", ["prog_name"] + test_args)
    args = cleanup.get_args()
    assert args.bucket == "test-bucket"
    assert args.keep == 5


@mock_aws
def test_cleanup():
    """
    Tests that the cleanup function deletes all but the most recent X folders in an S3 bucket.
    """

    # Create a bucket and add 50 folders to it
    s3 = boto3.client("s3", region_name="us-east-1")
    bucket_name = "test-bucket"
    s3.create_bucket(Bucket=bucket_name)

    for i in range(50):
        s3.put_object(Bucket=bucket_name, Key=f"folder{i}/index.html", Body=b"Test")
        s3.put_object(Bucket=bucket_name, Key=f"folder{i}/css/font.css", Body=b"Test")
        s3.put_object(Bucket=bucket_name, Key=f"folder{i}/images/hey.png", Body=b"Test")

    # Run the cleanup function
    cleanup.cleanup(s3, bucket_name, 5)

    # Check that the correct number of folders were deleted
    paginator = s3.get_paginator("list_objects_v2")
    remaining_folders = []
    for page in paginator.paginate(Bucket=bucket_name, Delimiter="/"):
        if "CommonPrefixes" in page:
            remaining_folders.extend(page["CommonPrefixes"])
    assert len(remaining_folders) == 5

    # Delete all objects in the bucket, then delete the bucket
    s3_objects = s3.list_objects(Bucket=bucket_name).get("Contents", [])
    for obj in s3_objects:
        s3.delete_object(Bucket=bucket_name, Key=obj["Key"])
    s3.delete_bucket(Bucket=bucket_name)
