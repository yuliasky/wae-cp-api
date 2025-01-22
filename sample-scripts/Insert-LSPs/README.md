# RPC-based script

## Introduction
The purpose of this script is to insert programmatically multiple RSVP-TE
LSPs and Named Paths (optional) from a CSV file.

## Options:

    -plan-file: input plan file
    -out-file: output plan file
    -lsps-file: CSV file containing new LSPs information

## Additional options for the *_sdk.py script

    -cp-host: Crosswork Planning server IP address
    -cp-port: Crosswork Planning port where opm-service is running (Default port is 30744)

## How to use in WAE
The design_api_python binary tool is located under the `<WAE-Design-Install-Dir>/bin` folder

    $ ./design_api_python /path/to/insert_lsp_traffic.py -plan-file <input-plan-file> -out-file <output-plan-file> -lsps-file <csv-lsps-file>
    ...
    Example:
    ...
    $ ./design_api_python /path/to/update_demands_api.py -plan-file /path/to/us_wan.pln -out-file /path/to/plan_lsps.pln -lsps-file /path/to/lsps_file.csv

## How to use in CP via the Job Manager
Notice that any required input file (plan file or others) should be imported
in CP via the Network Models UI prior to running the script, and selected as
input files during the settings in the Job Manager UI.

    $ insert_lsp_traffic.py -plan-file <input-plan-file> -out-file <output-plan-file> -lsps-file <csv-lsps-file>
    ...
    Example:
    ...
    $ insert_lsp_traffic.py -plan-file us_wan.pln -out-file plan_lsps.pln -lsps-file lsps_file.csv

## How to use in CP via SDK Client
The script with name *_sdk.py is adapted to be executed from a CP SDK Client.
Notice that any required input file (plan file or others) in this example has
been previously uploaded / imported into the SDK client.

    $ python /path/to/insert_lsp_traffic.py -plan-file <input-plan-file> -out-file <output-plan-file> -cp-host <cp-ip-address> -cp-port <opm-service-port> -lsps-file <csv-lsps-file>
    ...
    Example:
    In the following example, the SDK Client has the following directory structure:
    ...
    $ ls -ltr
    total 12
    drwxr-xr-x. 3 wae wae 4096 Aug 27 13:38 lib
    drwxr-xr-x. 3 wae wae   17 Aug 27 13:38 docs
    -rwx------. 1 wae wae 4562 Dec  1 16:40 generate_client_certs
    drwxr-xr-x. 5 wae wae   60 Dec  7 06:02 etc
    drwxrwxr-x. 2 wae wae   30 Dec 12 17:45 data
    drwxrwxr-x. 2 wae wae  139 Dec 12 19:09 scripts
    drwxrwxr-x. 2 wae wae  117 Dec 12 21:18 plan-files
    $
    $ python scripts/insert_lsp_traffic.py -plan-file plan-files/us_wan.pln -out-file plan-files/pln_lsps.pln -cp-host 198.19.1.100 -cp-port 30744 -demands-file data/lsps_file.csv

