from app.models.db import SessionLocal, Drone
def seed():
    db=SessionLocal()
    if not db.get(Drone,'D-01'):
        db.add_all([Drone(id='D-01',battery=85,speed=12),Drone(id='D-02',battery=96,speed=10,status='maintenance'),Drone(id='D-03',battery=64,speed=11)])
        db.commit()
    db.close()
