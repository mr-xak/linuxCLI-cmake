# ALT Linux Package Comparator

This tool compares binary packages between the `p10` and `sisyphus` branches of ALT Linux.

## Requirements

- Python 3.x
- `requests` library
- `tabulate` library
- `tqdm` library
- `rpm_vercmp` library

## Installation

1. Clone the repository and navigate into the project directory:

    ```sh
    git clone https://github.com/cobaltCorsair/linuxCLI.git
    cd linuxCLI
    ```

2. Install the required Python libraries:

    ```sh
    pip install -r requirements.txt
    ```
   
3. Make the CLI script executable:

    ```sh
    chmod +x compare_packages.sh
    ```

## Usage

Run the following command to compare packages:

   ```sh
   python main.py
   ```

You will be prompted to specify the output format (json or text).
Alternatively, you can specify the output format directly using the --output argument:

   ```sh
   python main.py --output json
   ```

## Running the CLI Script

Run the following command to compare packages:

```sh
./compare_packages.sh
```

You will be prompted to specify the output format (json or text).
Alternatively, you can specify the output format directly:

```sh
./compare_packages.sh json
```

### Output Formats
- `json`: Saves the comparison results to a JSON file named **comparison_results.json.**
- `text`: Saves the comparison results to a text file named **comparison_results.txt.**

## Example
To run the script and output the results in JSON format:
```sh
./compare_packages.sh json
```
This will fetch the package lists from the ALT Linux API, compare them, and save the results to **comparison_results.json.**

## JSON Structure

The JSON output will have the following structure:

`{
  "arch1": {
    "p10_only": [
      {
        "name": "package1",
        "version": "1.0",
        "release": "1",
        "arch": "arch1"
      },
      ...
    ],
    "sisyphus_only": [
      {
        "name": "package2",
        "version": "2.0",
        "release": "1",
        "arch": "arch1"
      },
      ...
    ],
    "sisyphus_newer": [
      {
        "name": "package3",
        "version": "3.0",
        "release": "2",
        "arch": "arch1"
      },
      ...
    ]
  },
  ...
}`

## License
This project is licensed under the **MIT License**.