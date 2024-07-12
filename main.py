import os

import requests
import json
from packaging import version

API_BASE_URL = "https://rdb.altlinux.org/api/export/branch_binary_packages/"


def get_packages(branch):
    """
    Gets a list of binary packages for the specified branch.

    :param branch: Branch (e.g. 'sisyphus' or 'p10')
    :return: List of packages in JSON format
    """
    # Check if the local file exists
    filename = f"{branch}.json"
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            return json.load(file)

    # Fetch data from the API if the local file doesn't exist
    url = f"{API_BASE_URL}{branch}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        # Save data to local file for future use
        with open(filename, 'w') as file:
            json.dump(data, file, indent=4)
        return data
    else:
        raise Exception(f"Failed to fetch data from API. Status code: {response.status_code}")


def compare_versions(version1, version2):
    """
    Compares two versions of packages.

    :param version1: First version
    :param version2: Second version
    :return: True if the first version is greater than the second, otherwise False
     """
    return version.parse(version1) > version.parse(version2)


def compare_all_architectures():
    """
    Compares packages between p10 and sisyphus branches for all architectures.

    :return: Comparison results for each architecture in JSON format
    """
    branches = ['p10', 'sisyphus']
    p10_packages = get_packages(branches[0])
    sisyphus_packages = get_packages(branches[1])

    # Extract unique architectures
    architectures = set(pkg['arch'] for pkg in p10_packages + sisyphus_packages)

    for arch in architectures:
        # Filter packages by architecture
        p10_arch_pkgs = [pkg for pkg in p10_packages if pkg['arch'] == arch]
        sisyphus_arch_pkgs = [pkg for pkg in sisyphus_packages if pkg['arch'] == arch]
        print(p10_arch_pkgs, sisyphus_arch_pkgs)


if __name__ == "__main__":
    try:
        compare_all_architectures()
    except Exception as e:
        print(e)

