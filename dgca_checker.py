import json

def check_compliance(waypoints, json_data):
    max_alt = json_data.get("target_altitude_m", 60)
    
    if max_alt > 120:
        return {"status": "FAIL", "reason": "Altitude exceeds 120m DGCA Green Zone limit.", "score": 0}
        
    for lat, lon, _ in waypoints:
        if 24.2110 <= lat <= 24.2115 and 83.0310 <= lon <= 83.0320:
            return {"status": "FAIL", "reason": "Path intersects with restricted industrial airspace.", "score": 40}
            
    return {"status": "PASS", "reason": "Flight compliant with DGCA Green Zone parameters.", "score": 100}
