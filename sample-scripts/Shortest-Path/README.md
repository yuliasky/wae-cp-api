# OPM-based script

## Introduction
The purpose of this script is to calculate the shortest for a new demand.
As a result, a dictionary will be returned containing the following infomration for the new demand:
- Max./min./avg. latency
- Total path metric
- Routing path hop by hop

Output example:

    {'minimum_latency': 36.49, 'average_latency': 36.49, 'maximum_latency': 36.49, 'total_path_metric': 2185.0, 'maximum_interface_utilization': 112.36, 'routing_path': "[{'node': 'cr1.chi', 'name': 'to_cr2.nyc'}, {'node': 'cr1.mia', 'name': 'to_er1.mia'}, {'node': 'cr1.nyc', 'name': 'to_cr2.wdc'}, {'node': 'cr2.nyc', 'name': 'to_cr1.nyc'}, {'node': 'cr2.sea', 'name': 'to_cr1.chi'}, {'node': 'cr2.wdc', 'name': 'to_cr1.mia'}, {'node': 'er1.sea', 'name': 'to_cr2.sea'}]"}

## How to use in CP via the Job Manager
Notice that any required input file (plan file or others) should be imported in CP via the Network Models UI prior to running the script, and selected as input files during the settings in the Job Manager UI.

    $ get_route_shortest_path.py <input-plan-file> <source-node> <destination-node> <metric-type> <bw> <cp-ip-address> <opm-service-port>
    ...
    Example:
    ...
    $ get_route_shortest_path.py plan-files/us_wan.txt er1.sea er1.mia igp 1000

In order to view the results, you would need to open or download the log file from the output file generated after the job is completed.

## How to use in CP via SDK Client
The script with name `*_sdk.py` is adapted to be executed from a CP SDK Client.
Notice that any required input file (plan file or others) in this example has been previously uploaded / imported into the SDK client.

    $ python /path/to/get_route_shortest_path_sdk.py <input-plan-file> <source-node> <destination-node> <metric-type> <bw> <cp-ip-address> <opm-service-port>
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
    $ python scripts/get_route_shortest_path_sdk.py plan-files/us_wan.txt er1.sea er1.mia igp 1000 -cp-host 198.19.1.100 -cp-port 30744

