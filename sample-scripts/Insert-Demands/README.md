# RPC-based script

## Introduction
The purpose of this script is to insert programmatically multiple Demands
and Demands Traffic from a CSV file.

## Options:

    -plan-file: input plan file
    -out-file: output plan file
    -demands-file: CSV file containing new demands information

## Additional options for the *_sdk.py script

    -cp-host: Crosswork Planning server IP address
    -cp-port: Crosswork Planning port where opm-service is running (Default port is 30744)

## How to use
The design_api_python binary tool is located under the `<WAE-Design-Install-Dir>/bin` folder

    $ ./design_api_python /path/to/update_demands_api.py -plan-file <input-plan-file> -out-file <output-plan-file> -demands-file <csv-demands-file>
    ...
    Example:
    ...
    $ ./design_api_python /path/to/update_demands_api.py -plan-file /path/to/sr_sage.pln -out-file /path/to/sr_sage_api_dmds.pln -demands-file /path/to/demands_file.csv

## How to use in CP via the Job Manager
Notice that any required input file (plan file or others) should be imported
in CP via the Network Models UI prior to running the script, and selected as
input files during the settings in the Job Manager UI.

    $ python update_demands_api.py -plan-file <input-plan-file> -out-file <output-plan-file> -demands-file <csv-demands-file>
    ...
    Example:
    ...
    $ update_demands_api.py -plan-file sr_sage.pln -out-file sr_sage_api_dmds.pln -demands-file demands_file.csv

## How to use in CP via SDK Client
The script with name *_sdk.py is adapted to be executed from a CP SDK Client.
Notice that any required input file (plan file or others) in this example has
been previously uploaded / imported into the SDK client.

    $ python /path/to/update_demands_api_sdk.py -plan-file <input-plan-file> -out-file <output-plan-file> -cp-host <cp-ip-address> -cp-port <opm-service-port> -demands-file <csv-demands-file>
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
    $ python scripts/update_demands_api_sdk.py -plan-file plan-files/sr_sage.pln -out-file plan-files/sr_sage_api_dmds.pln -cp-host 198.19.1.100 -cp-port 30744 -demands-file data/demands_file.csv

