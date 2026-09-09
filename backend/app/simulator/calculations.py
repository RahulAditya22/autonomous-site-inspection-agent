import math
def distance(a,b): return math.hypot(b[0]-a[0], b[1]-a[1])
def estimate_battery(distance_units,rate=0.45,reserve=8): return distance_units*rate+reserve
def route_distance(points): return sum(distance(points[i],points[i+1]) for i in range(len(points)-1))
