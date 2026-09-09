from app.simulator.controller import SimulatedDroneController
def test_takeoff_and_navigation_consume_battery():
    d=SimulatedDroneController('D-01',battery=85); d.takeoff(); before=d.get_telemetry().battery; d.goto_waypoint(20,0); after=d.get_telemetry().battery; assert d.get_telemetry().altitude==20; assert after<before
def test_abort():
    d=SimulatedDroneController('D-01'); d.takeoff(); d.abort_mission(); assert d.get_telemetry().mission_status=='aborted'
