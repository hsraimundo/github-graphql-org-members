# GitHub GraphQL Tool for Listing Users

The objective of this tool is to create a list of the github users in a github organization paired with their SSO linked account email.

This outputs to a `output.csv` file with the format `SSO Email, GitHub User`.

## Using this script

> This script was only tested using Python 2.7.*

To execute run `python github_traverse.py GITHUB_AUTH_TOKEN GITHUB_ORGANIZATION_USER`