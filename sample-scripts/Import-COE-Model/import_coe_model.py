#!/usr/bin/python

import re,sys,os
import datetime
import com.cisco.wae.design
import argparse
import base64
import json
import requests
import urllib3
import time

from com.cisco.wae.design.model.plotLayout import LayoutKey
from com.cisco.wae.design.model.plotLayout import LayoutRecord
from com.cisco.wae.design.model.plotLayout import LayoutType
from com.cisco.wae.design.tools import DemandMeshCreatorOptions
from com.cisco.wae.design.tools import DemandDeductionOptions
from com.cisco.wae.design.model import PlanFormat
from com.cisco.wae.design.model.net import NodeKey



def process_argv():
    '''
        Returns the cli arguments in a dictionary
    '''
    argv = list(sys.argv)
    options = {}
    argv.pop(0)
    while len(argv) > 0:
        item = argv.pop(0)
        next_item = argv.pop(0)
        options[re.sub(r'^-', '', item)] = next_item
    return options

def get_cli_options():
    '''
        Captures and validates the CLI options
    '''
    options = process_argv()
    return options

def printmsg(msg):
    print(msg)

def print_request(req):
    printmsg('{}\n{}\n{}'.format(
        req.method + ' ' + req.url,
        '\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
        req.body
    ))

def send_request(reqtype, url, params, headers):
    req = requests.Request(reqtype, url, data = params, headers = headers)
    prep = req.prepare()
    print_request(prep)
    session  = requests.Session()
    return session.send(prep, verify = False)

def connect_cnc(cnc_ip, cnc_user, cnc_password):
    '''
        Get Ticket
    '''
    printmsg('\nGetting TGT token')
    url = "https://{}:30603/crosswork/sso/v1/tickets".format(cnc_ip)
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    params = {
        "username":cnc_user,
        "password":cnc_password
    }

    response = send_request('POST', url, params, headers)
    tgt_token = response.text
    printmsg('TGT token\n'+ tgt_token)

    '''
        Get Token
    '''
    printmsg('\nGetting JWT token')
    url = "https://{}:30603/crosswork/sso/v1/tickets/{}".format(cnc_ip, tgt_token)
    params = {
        "service": "https://cw.domain.com/app-dashboard"
    }

    response = send_request('POST', url, params, headers)
    jwt_token = response.text
    printmsg('JWT token\n'+ jwt_token)

    return jwt_token

def get_coe_model(cnc_ip, jwt_token, pln_name, pln_schema):
    printmsg('\nMaking COE API call')
    url = "https://{}:30603/crosswork/nbi/optima/v2/restconf/operations/cisco-crosswork-optimization-engine-operations:get-plan".format(cnc_ip)
    headers = {"Authorization":"Bearer {}".format(jwt_token),"Content-Type": "application/json"}
    params = '{"input": {"version"' + ':"{}",'.format(pln_schema) + '"format":"txt"}}'

    response = send_request('POST', url, params, headers)

    print('\nResponse headers:')
    for k,v in response.headers.items():
        print(str(k) + ' : ' + str(v))

    if response.status_code == 200:
        if pln_name:
            f = open(pln_name, 'wb')
            f.write(base64.b64decode(response.json()['cisco-crosswork-optimization-engine-operations:output']['planfile-content']))
            f.close()
        else:
            print('\n' + base64.b64decode(response.json()['cisco-crosswork-optimization-engine-operations:output']['planfile-content']).decode("utf-8"))

def clean_nodes_tags(plan):
    node_manager = plan.getNetwork().getNodeManager()

    node_key_list = node_manager.getAllNodeKeys()
    for node_key in node_key_list:
        node = node_manager.getNode(key=node_key)
        node.removeAllTags()

def copy_from_temlate(plan, plan_template):
    layout_manager_tmp = plan_template.getLayoutManager()
    layout_template = layout_manager_tmp.getLayout(key=LayoutKey(name="Default"))
    layout_template_rec = layout_template.getRecord()
    print("This is the layout template record:", layout_template_rec)

    layout_manager = plan.getLayoutManager()
    layout_rec_tmp = LayoutRecord(
        key=LayoutKey(name="tmp"),
        type=LayoutType.LAYOUT_DESIGN
    )
    layout_manager.newLayout(rec=layout_rec_tmp)
    layout_manager.removeLayout(key=LayoutKey(name="Default"))
    layout_manager.newLayout(rec=layout_template_rec)
    layout_manager.removeLayout(key=LayoutKey(name="tmp"))

    site_manager_tmp = plan_template.getNetwork().getSiteManager()
    site_rec_list_tmp = site_manager_tmp.getAllSiteRecords()

    site_manager = plan.getNetwork().getSiteManager()
    for site_rec in site_rec_list_tmp:
        new_site = site_manager.newSite(siteRec=site_rec)
        print("New Site: ", new_site.getRecord())

    node_manager = plan.getNetwork().getNodeManager()
    node_key_list = node_manager.getAllNodeKeys()
    node_manager_tmp = plan_template.getNetwork().getNodeManager()
    node_key_list_tmp = node_manager_tmp.getAllNodeKeys()
    for node_key in node_key_list:
        for node_key_tmp in node_key_list_tmp:
            if node_key.name == node_key_tmp.name:
                node_tmp = node_manager_tmp.getNode(key=node_key_tmp)
                site_tmp = node_tmp.getSite()
                if site_tmp:
                    node = node_manager.getNode(key=node_key)
                    site_key = site_tmp.getKey()
                    site = site_manager.getSite(key=site_key)
                    node.setSite(site)
                else:
                    node = node_manager.getNode(key=node_key)
                    node.setLatitude(node_tmp.getLatitude())
                    node.setLongitude(node_tmp.getLongitude())

def copy_from_inventory(plan, plan_template):
    node_manager = plan.getNetwork().getNodeManager()
    node_manager_tmp = plan_template.getNetwork().getNodeManager()

    nodes = node_manager.getAllNodes()
    for node_key in nodes:
        node = node_manager.getNode(key=node_key)
        node_name = node.getName()
        node_vendor = node.getVendor()
        node_model = node.getModel()
        node_os = node.getOS()
        if node_vendor == '' and node_model == '' and node_os == '':
            if node_manager_tmp.hasNode(key=NodeKey(name=node_name)):
                node_tmp = node_manager_tmp.getNode(key=NodeKey(name=node_name))
                node.setVendor(val=node_tmp.getVendor())
                node.setModel(val=node_tmp.getModel())
                node.setOS(val=node_tmp.getOS())

def main(argv=None):
    
    options = get_cli_options()

    # Process arguments
    plan_file = options['plan-file']
    out_file = options['out-file']
    cnc_ip = options['cnc-ip']
    cnc_user = options['cnc-user']
    cnc_password = options['cnc-password']
    pln_schema = options['pln-schema']
    copy_template = options['copy-template']
    create_demands = options['create-demands']

    print(datetime.datetime.now())
    conn = com.cisco.wae.design.ServiceConnectionManager.newService()
    conn_template = com.cisco.wae.design.ServiceConnectionManager.newService()

    # Disable insecure warnings
    printmsg('\nDisabling insecure request warning')
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # Connect to CNC and get the OE Model
    jwt_token = connect_cnc(cnc_ip, cnc_user, cnc_password)
    pln_name = "plan_d.txt"
    get_coe_model(cnc_ip, jwt_token, pln_name, pln_schema)
    time.sleep(30)
    with open(pln_name, 'rb') as file_r:
        plan = conn.getPlanManager().newPlanFromBytes(file_r.read())

        # Clean Tags from Nodes
        clean_nodes_tags(plan)

        # Call Copy From Template if copy_template is set to True
        if copy_template == 'true':
            pln_template = options['pln-template']
            print("Template name is:", pln_template)
            plan_template = conn_template.getPlanManager().newPlanFromFileSystem(pln_template)
            copy_from_temlate(plan, plan_template)
            # If copy_template AND copy_inventory are set to True, then copy inventory properties [Vendor, Model, OS] from Template
            copy_inventory = options['copy-inventory']
            if copy_inventory == 'true':
                copy_from_inventory(plan, plan_template)

        # Insert full Demand Mesh and run Demand Deduction with default values if create_demands is set to True
        if create_demands == 'true':
            tool_manager = conn.getToolManager()
            dmdMeshCreator = tool_manager.newDemandMeshCreator()
            dmdMeshCreator_opts = DemandMeshCreatorOptions()
            dmdMeshCreator.run(netObj=plan.getNetwork(), options=dmdMeshCreator_opts)

            dmdDeduct = tool_manager.newDemandDeduction()
            dmdDeduct_opts = DemandDeductionOptions()
            dmdDeduct.run(netObj=plan.getNetwork(), options=dmdDeduct_opts)
            print("Demand Deduction is completed")

        with open(out_file, 'wb') as file_w:
            file_w.write(plan.serializeToBytes(format=PlanFormat.PlnFile))
        com.cisco.wae.design.ServiceConnectionManager.shutdownService(conn)
        com.cisco.wae.design.ServiceConnectionManager.shutdownService(conn_template)
    print(datetime.datetime.now())

# end main()


if __name__ == '__main__':
    main()
    exit(0)