from fastapi import FastAPI
from astral import LocationInfo
from astral.sun import sun
from datetime import datetime,date
from astral import moon
import requests
import math
import ephem
from datetime import datetime
from meteor_showers import METEOR_SHOWERS

app = FastAPI(
    title="Cosmic Companion API",
    description="Get Sky conditions, moon phase, ISS visibility and more from any location on Earth.",
    version="1"

)

@app.get("/")
def root():
    return {"message" : "Hello this is working type shiiii"}




@app.get("/sun")
def get_sun_times(lat:float,lon:float):
    location = LocationInfo(latitude=lat,longitude=lon)
    s = sun(location.observer,date=date.today())

    return{
        "latitude": lat,
        "longitude": lon,
        "date": str(date.today()),
        "sunrise": s["sunrise"].strftime("%H:%M:%S"),
        "sunset": s["sunset"].strftime("%H:%M:%S"),
        "dawn": s["dawn"].strftime("%H:%M:%S"),
        "dusk": s["dusk"].strftime("%H:%M:%S"),
        "noon": s["noon"].strftime("%H:%M:%S")
    }



def getMoonPhaseName(phase_value:float) ->str:
    if phase_value <1.75 or phase_value >= 26.25:
        return "New Moon"
    
    elif phase_value <5.25:
        return "Waxing Cresent"
    elif phase_value <8.75:
        return "First Quarter"
    elif phase_value<12.25:
        return "Waxing Gibbous"
    elif phase_value <15.75:
        return "Full Moon"
    elif phase_value < 19.25:
        return "Waning Gibbous"
    elif phase_value <22.75:
        return "Last Quarter"
    else:
        return "Waning Cresent"
    
def is_shower_active(start_str, end_str, today):
    def parse_md(s):
        m, d = map(int, s.split("-"))
        return (m, d)
    
    start = parse_md(start_str)
    end = parse_md(end_str)
    current = (today.month, today.day)
    
    if start <= end:
        return start <= current <= end
    else:  # wraps around new year
        return current >= start or current <= end


@app.get("/moon")
def get_moonINFO():
    phaseValue = moon.phase(date.today())

    return{
        "date" : str(date.today()),
        "moon_phase": getMoonPhaseName(phaseValue),
        "phase_value" : round(phaseValue,2)
    }







def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Earth's radius in km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 2 * R * math.asin(math.sqrt(a))





@app.get("/iss")
def get_iss_info(lat: float, lon: float):
    response = requests.get("http://api.open-notify.org/iss-now.json")
    data = response.json()
    
    iss_lat = float(data["iss_position"]["latitude"])
    iss_lon = float(data["iss_position"]["longitude"])
    
    distance = haversine_distance(lat, lon, iss_lat, iss_lon)
    
    # ISS orbits at ~400km, visible roughly within ~2300km ground distance
    is_visible_range = distance < 2300
    
    return {
        "iss_position": {
            "latitude": iss_lat,
            "longitude": iss_lon
        },
        "your_location": {"latitude": lat, "longitude": lon},
        "distance_km": round(distance, 1),
        "iss_in_range": is_visible_range}



@app.get("/planets")
def get_visible_planets(lat:float,lon:float):
    observer = ephem.Observer()
    observer.lat = str(lat)
    observer.lon = str(lon)
    observer.date = datetime.utcnow()

    planets = {
        "Mercury": ephem.Mercury(),
        "Venus": ephem.Venus(),
        "Mars": ephem.Mars(),
        "Jupiter": ephem.Jupiter(),
        "Saturn": ephem.Saturn(),
        "Uranus": ephem. Uranus(),
        "Neptune": ephem.Neptune()
        }
    
    visible = []
    all_planets = {}


    for name, body in planets.items():
        body.compute(observer)
        altitude_deg = float(body.alt)*180/math.pi

        all_planets[name] ={
            "altitide_deg": round(altitude_deg,2),
            "magnitude": round(float(body.mag),2),
            "above_horizon": altitude_deg > 0
        }

        if altitude_deg > 0:
            visible.append(name)
        

    return{
        "your_location": {"latitude":lat,"longitude":lon},
        "datetime_utc": str(observer.date),
        "visible_planets": visible,
        "details": all_planets
    }
  



@app.get("/meteor-showers")
def get_meteor_showers():
    today = date.today()

    active = []
    upcoming = []

    for shower in METEOR_SHOWERS:
        is_active = is_shower_active(shower["start"],shower["end"],today)

        peak_month, peak_day = map(int,shower["peak"].split("-"))
        days_to_peak = (date(today.year, peak_month, peak_day)-today).days
        if days_to_peak<0:
            days_to_peak+=365

        entry = {
            "name": shower["name"],
            "peak_date": shower["peak"],
            "active_window": f"{shower['start']} to {shower['end']}",
            "peak_rate_per_hour": shower["rate"],
            "days_to_peak": days_to_peak,
            "description": shower["description"],
            "status": "ACTIVE" if is_active else "UPCOMING"
        }

        if is_active:
            active.append(entry)
        else:
            upcoming.append(entry)
    
    # sort upcoming by days to peak
    upcoming.sort(key=lambda x: x["days_to_peak"])
    
    return {
        "date": str(today),
        "active_showers": active,
        "next_3_upcoming": upcoming[:3]
    }