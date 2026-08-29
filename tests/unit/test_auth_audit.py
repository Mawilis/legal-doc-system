from collections import UserDict
import logging
from typing import cast
from tools.eos.auth.audit import log_auth_event

def test_omitted_and_none_details():
    assert log_auth_event('E','P',True)['details']=={}
    assert log_auth_event('E','P',False,None)['details']=={}

def test_mapping_copy_and_isolation():
    source={'reason':'x'}; result=log_auth_event('E','P',True,source)
    details=cast(dict[str, object], result['details'])
    assert details==source and details is not source
    source['reason']='y'; assert details['reason']=='x'
    details['reason']='z'; assert source['reason']=='y'
    assert log_auth_event('E','P',True,UserDict({'n':1}))['details']=={'n':1}

def test_fields_status_timestamp_and_emission(caplog):
    with caplog.at_level(logging.INFO,'WilsyOS.SecurityAudit'):
        payload=log_auth_event('EVENT','principal',True,{})
    assert payload['event_type']=='EVENT' and payload['principal']=='principal' and payload['status']=='SUCCESS'
    assert payload['timestamp'] and len(caplog.records)==1 and 'SECURITY AUDIT' in caplog.records[0].message
    assert 'tenant_id' not in payload and 'role' not in payload and 'permission' not in payload
    assert log_auth_event('EVENT','principal',False)['status']=='REJECTED'
