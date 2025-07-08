# RPC-based script

## Introduction
The purpose of this script is to insert programmatically multiple Circuit Style RSVP
LSP entities from a CSV file, using the CS RSVP Optimizer. The corresponding LSPs
and LSP Paths objects will be created too.

## Options:

    -plan-file: input plan file
    -out-file: output plan file
    -cs-rsvp-file: CSV file containing new CS RSVP LSPs information

## Additional options for the *_sdk.py script

    -cp-host: Crosswork Planning server IP address
    -cp-port: Crosswork Planning port where opm-service is running (Default port is 30744)

## How to use in WAE
Not supported in WAE.

## How to use in CP via the Job Manager
Notice that any required input file (plan file or others) should be imported
in CP via the Network Models UI prior to running the script, and selected as
input files during the settings in the Job Manager UI.

    $ create_cs_rsvp_lsp.py -plan-file <input-plan-file> -out-file output-plan-file> -cs-rsvp-file <csv-cs-rsvp-file>
    ...
    Example:
    ...
    $ create_cs_rsvp_lsp.py -plan-file sample_plan.pln -out-file sample_plan_lsp.pln -cs-rsvp-file cs_rsvp_file.csv

## How to use in CP via SDK Client
The script with name *_sdk.py is adapted to be executed from a CP SDK Client.
Notice that any required input file (plan file or others) in this example has
been previously uploaded / imported into the SDK client.

    $ python /path/to/create_cs_rsvp_lsp_sdk.py -plan-file <input-plan-file> -out-file <output-plan-file> -cp-host <cp-ip-address> -cp-port <opm-service-port> -cs-rsvp-file <csv-cs-rsvp-file>
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
    $ python scripts/create_cs_rsvp_lsp_sdk.py -plan-file plan-files/sample_plan.pln -out-file plan-files/sample_plan_lsp.txt -cp-host 198.19.1.100 -cp-port 30744 -cs-rsvp-file data/cs_rsvp_file.csv

