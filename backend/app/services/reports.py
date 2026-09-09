from app.services.memory import MissionMemory
def build_report(db,mission):
    snap=MissionMemory(db).mission_snapshot(mission); findings=[]; max_sev=1
    for i in snap['inspections']:
        max_sev=max(max_sev,int(i['risk'].get('severity',1))); findings.append({'task_id':i['task_id'],'severity':i['risk'].get('severity',1),'risk':i['risk'].get('risk_level','Low'),'detections':[d.get('label') for d in i['detections']]})
    return {'mission':snap,'summary':{'finding_count':len(findings),'max_severity':max_sev,'result':'Escalated' if max_sev>=5 else 'Completed'},'findings':findings}
