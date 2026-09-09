from __future__ import annotations
from pathlib import Path
from flask import Blueprint,jsonify,request,send_from_directory
from pydantic import ValidationError
from sqlalchemy import select
from app.models.db import SessionLocal,Mission,Drone
from app.models.schemas import MissionCreate,SafetyApproval,QueryRequest
from app.services.executor import MissionExecutor
from app.services.memory import MissionMemory
from app.services.reports import build_report
from app.config import settings
api=Blueprint('api',__name__,url_prefix='/api'); ROOT=Path(__file__).resolve().parents[3]; executor=MissionExecutor()
@api.get('/health')
def health():return jsonify({'status':'ok','mode':'local','vision_model':settings.vision_model})
@api.get('/drones')
def drones():
    db=SessionLocal(); rows=db.scalars(select(Drone)).all(); out=[{'id':d.id,'status':d.status,'battery':round(d.battery,1),'position':{'x':d.x,'y':d.y,'altitude':d.altitude},'speed':d.speed,'communication':d.communication,'camera_status':d.camera_status,'health':d.health,'current_task':d.current_task,'mission_status':d.mission_status} for d in rows]; db.close(); return jsonify(out)
@api.get('/missions')
def missions():
    db=SessionLocal(); rows=db.scalars(select(Mission).order_by(Mission.created_at.desc())).all(); mem=MissionMemory(db); out=[mem.mission_snapshot(m) for m in rows]; db.close(); return jsonify(out)
@api.post('/missions')
def create_mission():
    try:payload=MissionCreate.model_validate(request.get_json(force=True))
    except (ValidationError,TypeError,ValueError) as e:return jsonify({'error':str(e)}),400
    db=SessionLocal()
    try:m=executor.create(db,payload.objective,payload.drone_id); return jsonify(MissionMemory(db).mission_snapshot(m)),201
    except ValueError as e:return jsonify({'error':str(e)}),409
    finally:db.close()
@api.get('/missions/<mission_id>')
def mission(mission_id):
    db=SessionLocal(); m=db.get(Mission,mission_id)
    if not m:db.close();return jsonify({'error':'Mission not found'}),404
    out=MissionMemory(db).mission_snapshot(m); db.close(); return jsonify(out)
@api.post('/missions/<mission_id>/start')
def start(mission_id):
    db=SessionLocal(); exists=db.get(Mission,mission_id); db.close()
    if not exists:return jsonify({'error':'Mission not found'}),404
    from threading import Thread; Thread(target=lambda:executor.run(mission_id,False),daemon=True).start(); return jsonify({'status':'started','mission_id':mission_id}),202
@api.post('/missions/<mission_id>/demo')
def demo(mission_id):
    db=SessionLocal(); exists=db.get(Mission,mission_id); db.close()
    if not exists:return jsonify({'error':'Mission not found'}),404
    from threading import Thread; Thread(target=lambda:executor.run(mission_id,True),daemon=True).start(); return jsonify({'status':'demo_started','mission_id':mission_id}),202
@api.post('/missions/<mission_id>/approval')
def approval(mission_id):
    try:payload=SafetyApproval.model_validate(request.get_json(force=True))
    except Exception as e:return jsonify({'error':str(e)}),400
    db=SessionLocal(); m=db.get(Mission,mission_id)
    if not m:db.close();return jsonify({'error':'Mission not found'}),404
    if m.status!='awaiting_approval':db.close();return jsonify({'error':'Mission is not awaiting approval'}),409
    if payload.approved:m.status='approved';db.commit();MissionMemory(db).save_event(mission_id,'Human','approval','Human approved the safety-gated action.');db.close();return jsonify({'status':'approved'})
    m.status='aborted';db.commit();MissionMemory(db).save_event(mission_id,'Human','approval','Human rejected the safety-gated action; mission aborted.');db.close();return jsonify({'status':'rejected'})
@api.get('/rag')
def rag():return jsonify(executor.rag.retrieve(request.args.get('q','site safety'),settings.rag_top_k))
@api.post('/memory/query')
def memory_query():
    try:q=QueryRequest.model_validate(request.get_json(force=True))
    except Exception as e:return jsonify({'error':str(e)}),400
    db=SessionLocal();out=MissionMemory(db).search(q.question);db.close();return jsonify({'matches':out})
@api.post('/inspections/analyze')
def analyze_upload():
    from PIL import Image
    upload=request.files.get('image')
    if not upload or not upload.filename:return jsonify({'error':'image file is required'}),400
    suffix=Path(upload.filename).suffix.lower()
    if suffix not in {'.jpg','.jpeg','.png','.webp'}:return jsonify({'error':'unsupported image type'}),415
    import uuid; upload_dir=ROOT/'backend'/'uploads';upload_dir.mkdir(parents=True,exist_ok=True);path=upload_dir/(uuid.uuid4().hex+suffix);upload.save(path)
    try:
        with Image.open(path) as img:img.verify()
        perception=executor.perception.analyze(str(path));risk=__import__('app.scoring.risk',fromlist=['score']).score(perception['detections']);rag=executor.rag.retrieve(' '.join(d['label'] for d in perception['detections']) or 'image quality inspection safety',settings.rag_top_k);return jsonify({'perception':perception,'risk':risk,'retrieved_knowledge':rag})
    except Exception as exc:path.unlink(missing_ok=True);return jsonify({'error':f'image analysis failed: {exc}'}),422
@api.get('/missions/<mission_id>/report')
def report(mission_id):
    db=SessionLocal();m=db.get(Mission,mission_id)
    if not m:db.close();return jsonify({'error':'Mission not found'}),404
    out=build_report(db,m);db.close();return jsonify(out)
@api.get('/demo/images/<path:name>')
def demo_image(name):return send_from_directory(ROOT/'data'/'demo',name)
