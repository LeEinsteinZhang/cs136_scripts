# Universitu of Waterloo Course Account Marks Scripts

This project includes two scripts: `marm2` and `edx`, which are designed for downloading and managing grades and submissions for academic courses.

## Setup and Installation

### Prerequisites

- Ensure you have the required permissions and environment to run these scripts (e.g., bash environment, necessary packages).
- Ensure the `~/bin` directory exists on your system, or create it.

### Setup Steps

1. Clone or download this project to your course account.

2. Run the `setup.sh` script to set up your environment. This script will link the `marm2` and `edx` scripts to the `~/bin` directory, making them executable from this scripts.

    ```bash
    ./setup.sh
    ```

3. Follow the prompts. If `~/bin/edx` or `~/bin/marm2` already exists, `setup.sh` will ask if you want to replace them. If you choose not to replace, it will also offer the option to rename these links.

4. Call `edx` module with flag `-i` to initialize the edx repo.

## Script Instruction

### marm2 Script

The `marm2` script is used for downloading grades for specified assignments or projects.

### edx Script

The `edx` script is for managing term configurations, exemptions files, and generating grade reports, among other tasks.

### Deatils Usage

For more advanced features and options, refer to the help information (`-h`) provided by each script. Or read the [user manual](user_manual.pdf) in the repo.

## Contributing

Contributions to this project are welcome via Pull Requests or by submitting Issues.

## License

This project is licensed under the [MIT License](LICENSE). See the LICENSE file for details.
