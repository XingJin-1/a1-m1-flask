
import json

#s= '{"cpee":"https://cpee.org/flow/engine/","instance-url":"https://cpee.org/flow/engine/57275","instance-uuid":"7fd9170f-6a63-4321-bf22-bc83d586b7cb","instance-name":"xing-log-test","instance":57275,"topic":"position","type":"event","name":"change","timestamp":"2021-09-29T23:18:54.583+02:00","content":{"after":[{"position":"a4"}],"attributes":{"guarded_id":"","author":"Christine Ashcreek","design_stage":"development","model_version":"","design_dir":"TUM-Prak.dir","uuid":"7fd9170f-6a63-4321-bf22-bc83d586b7cb","creator":"Christine Ashcreek","model_uuid":"af6aa536-9c99-4cd2-9726-365568325fbf","guarded":"none","theme":"extended","modeltype":"CPEE","info":"xing-log-test"}}'

s = '{"a":"aa", "b":"bb"}'
sj = json.loads(s)
print(sj)