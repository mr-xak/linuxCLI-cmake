import rpm_vercmp
import requests
import json
from tabulate import tabulate
import argparse
from tqdm import tqdm

API_BASE_URL = "https://rdb.altlinux.org/api/export/branch_binary_packages/"


def get_packages(branch):
    """
    Gets a list of binary packages for the specified branch.

    :param branch: Branch (e.g. 'sisyphus' or 'p10')
    :return: List of packages in JSON format
    """
    print(f"Fetching packages for branch: {branch}")

    # Fetch data from the API
    url = f"{API_BASE_URL}{branch}"
    response = requests.get(url, stream=True)

    total_size = int(response.headers.get('content-length', 0))
    block_size = 1024
    t = tqdm(total=total_size, unit='iB', unit_scale=True)

    data = b""
    for chunk in response.iter_content(block_size):
        t.update(len(chunk))
        data += chunk
    t.close()

    if response.status_code == 200:
        data = json.loads(data)
        # Ensure we return the list of packages
        return data['packages']
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


def save_results_to_json(results):
    """
    Saves the comparison results to a JSON file.

    :param results: Comparison results for each architecture
    """
    with open('comparison_results.json', 'w') as f:
        json.dump(results, f, indent=4)
    print("\nResults have been saved to comparison_results.json")


def save_results_to_text(results):
    """
    Saves the comparison results to a text file.

    :param results: Comparison results for each architecture
    """
    with open('comparison_results.txt', 'w') as f:
        for arch, data in results.items():
            if data['p10_only']:
                f.write("\nPackages only in p10:\n")
                f.write(tabulate([[pkg['name'], pkg['version'], pkg['release']] for pkg in data['p10_only']],
                                 headers=["Name", "Version", "Release"]))
            if data['sisyphus_only']:
                f.write("\nPackages only in sisyphus:\n")
                f.write(tabulate([[pkg['name'], pkg['version'], pkg['release']] for pkg in data['sisyphus_only']],
                                 headers=["Name", "Version", "Release"]))
            if data['sisyphus_newer']:
                f.write("\nPackages with newer versions in sisyphus:\n")
                f.write(tabulate([[pkg['name'], pkg['version'], pkg['release']] for pkg in data['sisyphus_newer']],
                                 headers=["Name", "Version", "Release"]))
    print("\nResults have been saved to comparison_results.txt")


def main():
    """
    Main function for CLI utility.
    Retrieves and compares packages, then outputs the results in the desired format.
    """
    print("Welcome to ALT Linux Package Comparator!")
    print("Fetching and comparing packages, please wait...")

    parser = argparse.ArgumentParser(description="Compare binary packages between p10 and sisyphus branches.")
    parser.add_argument('--output', choices=['json', 'text'],
                        help="Specify the output format: 'json' or 'text'.")
    args = parser.parse_args()

    # If output format is not provided as an argument, ask the user to input it
    if not args.output:
        while True:
            output_format = input("Please specify the output format (json, text): ").strip().lower()
            if output_format in ['json', 'text']:
                break
            print("Invalid format. Please enter 'json' or 'text'.")
    else:
        output_format = args.output

    # Retrieve and compare packages
    comparison_results = compare_all_architectures()

    # Output results in the specified format
    if output_format == 'json':
        save_results_to_json(comparison_results)
    elif output_format == 'text':
        save_results_to_text(comparison_results)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
