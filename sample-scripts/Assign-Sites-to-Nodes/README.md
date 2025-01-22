# OPM-based script

## Introduction
Hostname of nodes will be splitted by '.'. The second part of hostnames
represents the Site. And Nodes will be grouped on Sites based on the second
part of their hostnames.

## How to use in WAE
The design_api_python binary tool is located under the `<WAE-Design-Install-Dir>/bin` folder

    $ ./design_api_python /path/to/assign_sites_to_nodes.py <input-plan-file> <output-plan-file>
    ...
    Example:
    ...
    $ ./design_api_python /path/to/assign_sites_to_nodes.py /path/to/unprocessed-lab.pln /path/to/plansites.pln

## How to use in CP via the Job Manager
Notice that any required input file (plan file or others) should be imported
in CP via the Network Models UI prior to running the script, and selected as
input files during the settings in the Job Manager UI.

    $ assign_sites_to_nodes.py <input-plan-file> <output-plan-file>
    ...
    Example:
    ...
    $ assign_sites_to_nodes.py unprocessed-lab.pln plansites.pln

## How to use in CP via SDK Client
The script with name *_sdk.py is adapted to be executed from a CP SDK Client.
Notice that any required input file (plan file or others) in this example has
been previously uploaded / imported into the SDK client.
Crosswork Planning default opm-service port is 30744

    $ python /path/to/assign_sites_to_nodes_sdk.py <input-plan-file> <output-plan-file> <cp-ip-address> <opm-service-port>
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
    $ python scripts/assign_sites_to_nodes_sdk.py -plan-file plan-files/unprocessed-lab.pln -out-file plan-files/plansites.pln 198.19.1.100 30744

