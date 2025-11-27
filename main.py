#!/usr/bin/env python3
"""Monitors Cisco UCS threshold-crossed events."""
import xml.etree.ElementTree as ET

from time import sleep

import xmltodict

from ucsmsdk.ucshandle import UcsHandle

## filter_str
# (property_name, 'property_value', type='match_type: eq,ne,gt,lt,...')

active_faults = "(cause, 'threshold-crossed', type='eq') and (severity, 'cleared', type='ne')"
cleared_faults = "(cause, 'threshold-crossed', type='eq') and (severity, 'cleared', type='eq')"

try:
    handle = UcsHandle("10.4.8.20", "ldap.test", "1234QWer", secure=True)
    handle.login()

    while True:
        faults = handle.query_classid(class_id="faultInst", filter_str=active_faults)
        if faults:
            for mo in faults:
                # ManagedObject https://ciscoucs.github.io/ucsmsdk_docs/ucsmsdk.html#ucsmsdk.ucsmo.ManagedObject
                xml_str = ET.tostring(mo.to_xml(), encoding='unicode')
                xml_dict = xmltodict.parse(xml_str)
        sleep(30)

except Exception as err:
    print(err)

finally:
    handle.logout()


