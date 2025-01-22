# RPC-based script

## Introduction
The purpose of this script is to create programmatically multiple Traffic
Levels in the network model, including demands traffic.

## Options:

    -plan-file: input plan file
    -out-file: output plan file
    -traffic-level-count: number of new traffic levels to be created
    -traffic-inc-pct: percentage to increase demands traffic at each traffic level

## How to use in WAE
The design_api_python binary tool is located under the `<WAE-Design-Install-Dir>/bin` folder

    $ ./design_api_python /path/to/create_traff_lvl_dmds.py -plan-file <input-plan-file> -out-file <output-plan-file> -traffic-level-count <int> -traffic-inc-pct <int>
    ...
    Example:
    ...
    $ ./design_api_python /path/to/create_traff_lvl_dmds.py -plan-file /path/to/sr_sage.pln -out-file /path/to/plan_traffic_levels.pln -traffic-level-count 3 -traffic-inc-pct 40

