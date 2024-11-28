# RPC-based script

## Introduction
The purpose of this script is to automate the export of the network model
from COE into a new plan file. Additionally, script offers other options
to do copy from template (sites and locations), copy of inventory (vendor,
model and os) and insert demands (demand mesh and demand decution with 
default settings) in the new plan file. 

## Options:

    plan-file: input plan file
    out-file: output plan file
    cnc-ip: CNC/COE IP address
    cnc-user: CNC/COE username
    cnc-password: CNC/COE password
    pln-schema: plan file schema version (e.g. 7.6 / 7.5 / etc)
    copy-template: true or false
    pln-template [Optional]: template plan file. Required if copy-template is set to true.
    copy-inventory [Optional]: true or false. Required if copy-template is set to true.
    create-demands: true or false


## How to use in WAE
The design_api_python binary tool is located under the `<WAE-Design-Install-Dir>/bin` folder

    $ ./design_api_python /path/to/import_coe_model.py plan-file <input-plan-file> out-file <output-plan-file> cnc-ip <ip-address> cnc-user <user> cnc-password <password> pln-schema <schema-version> copy-template <false/true> pln-template <template-plan-file> copy-inventory <false/true> create-demands <false/true>
    ...
    Example:
    ...
    $ ./design_api_python /path/to/import_coe_model.py plan-file /path/to/EmptyPlanFile.db out-file /path/to/COEPlanFile.txt cnc-ip 198.19.1.219 cnc-user admin cnc-password 'p455w0Rd!!' pln-schema 7.6 copy-template true pln-template /path/to/coe6-template.pln copy-inventory true create-demands true

## How to use in CP via the Job Manager
Notice that any required input file (plan file or others) should be imported
in CP via the Network Models UI prior to running the script, and selected as
input files during the settings in the Job Manager UI.

    $ import_coe_model.py plan-file <input-plan-file> out-file <output-plan-file> cnc-ip <ip-address> cnc-user <user> cnc-password <password> pln-schema <schema-version> copy-template <false/true> pln-template <template-plan-file> copy-inventory <false/true> create-demands <false/true>
    ...
    Example:
    ...
    $ import_coe_model.py plan-file EmptyPlanFile.db out-file COEPlanFile.txt cnc-ip 198.19.1.219 cnc-user admin cnc-password 'p455w0Rd!!' pln-schema 7.6 copy-template true pln-template coe6-template.pln copy-inventory true create-demands true
