import os
import rpm_vercmp
import requests
import json
from tabulate import tabulate

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
    Compares two versions of packages using rpm_vercmp.

    :param version1: First version
    :param version2: Second version
    :return: True if the first version is greater than the second, otherwise False
    """
    result = rpm_vercmp.vercmp(version1, version2)
    return result > 0


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
    results = {}

    for arch in architectures:
        # Filter packages by architecture
        p10_arch_pkgs = [pkg for pkg in p10_packages if pkg['arch'] == arch]
        sisyphus_arch_pkgs = [pkg for pkg in sisyphus_packages if pkg['arch'] == arch]
        results[arch] = compare_packages(p10_arch_pkgs, sisyphus_arch_pkgs)

    return results


def compare_packages(p10_packages, sisyphus_packages):
    """
    Compares package lists between two branches.

    :param p10_packages: List of packages for p10 branch
    :param sisyphus_packages: List of packages for sisyphus branch
    :return: Comparison results in JSON format
    """
    p10_dict = {pkg['name']: pkg for pkg in p10_packages}
    sisyphus_dict = {pkg['name']: pkg for pkg in sisyphus_packages}

    result = {
        'p10_only': [],
        'sisyphus_only': [],
        'sisyphus_newer': []
    }

    for pkg_name, pkg in p10_dict.items():
        if pkg_name not in sisyphus_dict:
            result['p10_only'].append(pkg)
        else:
            sisyphus_pkg = sisyphus_dict[pkg_name]
            if compare_versions(
                    f"{sisyphus_pkg['version']}-{sisyphus_pkg['release']}",
                    f"{pkg['version']}-{pkg['release']}"
            ):
                result['sisyphus_newer'].append(sisyphus_pkg)

    for pkg_name, pkg in sisyphus_dict.items():
        if pkg_name not in p10_dict:
            result['sisyphus_only'].append(pkg)

    return result


def print_comparison_results(results):
    """
    Prints the comparison results in a formatted table.

    :param results: Comparison results for each architecture
    """
    for arch, data in results.items():
        print(f"\nArchitecture: {arch}")

        if data['p10_only']:
            print("\nPackages only in p10:")
            print(tabulate([[pkg['name'], pkg['version'], pkg['release']] for pkg in data['p10_only']],
                           headers=["Name", "Version", "Release"]))

        if data['sisyphus_only']:
            print("\nPackages only in sisyphus:")
            print(tabulate([[pkg['name'], pkg['version'], pkg['release']] for pkg in data['sisyphus_only']],
                           headers=["Name", "Version", "Release"]))

        if data['sisyphus_newer']:
            print("\nPackages with newer versions in sisyphus:")
            print(tabulate([[pkg['name'], pkg['version'], pkg['release']] for pkg in data['sisyphus_newer']],
                           headers=["Name", "Version", "Release"]))


if __name__ == "__main__":
    try:
        comparison_results = compare_all_architectures()
        print_comparison_results(comparison_results)
    except Exception as e:
        print(e)
