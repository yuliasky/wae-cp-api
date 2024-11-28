# RPC-based script

## Introduction
The purpose of this script is to run Simulation Analysis tool via API, and then
get the Maximum Worst-Case Interface Traffic and Utilization values from the
simulated model.
This script is adapted to be executed from a CP SDK Client.

## Options:

    -plan-file: input plan file
    -cp-host: Crosswork Planning server IP address
    -cp-port: Crosswork Planning port where opm-service is running (Default port is 30744)
    -failure-types: Failure Set options to be passed to the Simulation Analysis tool:
                    [Nodes Sites Circuits Ports PortCircuits]

## How to use in CP via SDK Client
Notice that any required input file (plan file or others) in this example has
been previously uploaded / imported into the SDK Client.

    $ python /path/to/get_wc_traffic_util.py -plan-file <input-plan-file> -cp-host <cp-ip-address> -cp-port <opm-service-port> -failure-type <failure-sets-list>
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
    $ python scripts/get_wc_traffic_util.py -plan-file plan-files/us_wan.txt -cp-host 198.19.1.100 -cp-port 30744 -failure-type Nodes Circuits
