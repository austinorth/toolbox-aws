# s3_cleanup
This folder contains a submission I made for a coding exercise as part of
the [Sure](https://www.sureapp.com/) interview process in May 2024.

I used a Python virtual environment for this on MacOS Sonoma. To set up the
environment, run the following commands:

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

I have not tested the script on Windows or Linux.

You can use the `-h` or `--help` flag to view the command line options,
description, and usage for the script.

## Questions
1. Where should we run this script?

You should run this script from a host that has proper AWS authentication to
reach the given S3 bucket. If you want the cleanup to be run regularly, you
could consider a CronJob hosted in AWS Lambda or perhaps running as a Kubernetes
CronJob. The latter would require building a Docker image with this script as an
Entrypoint, then deploying to Kubernetes.

2. How should we test the script before running it production?

I have included some basic unit tests with the script that show 87% pytest test
coverage using moto to mock an S3 bucket. I am assuming valid AWS credentials
and user input in the tests, so I haven't covered the Exceptions, but those
could easily be covered in the future should that be required. This was merely
to demonstrate how one might test the main functions of the script (taking user
input and deleting the deployment folders from S3) in the case of valid user
input and valid AWS credentials. I've also included a GitHub Action in this repo
that automatically runs the Ruff linter and pytest to ensure that the script is
tested upon git push. You can run the tests locally by simply invoking `pytest`
after installing `pytest` in your venv.

3. If we want to add an additional requirement of deleting deploys older than X
days but we must maintain at least Y number of deploys. What additional changes
would you need to make in the script?

I would add functionality that checked the `LastModified` attribute of the folders
and if it was older than X days, the folder would be deleted, excluding the
number of folders specified by an additional flag that allowed the user to pass
in Y number of deploys.
