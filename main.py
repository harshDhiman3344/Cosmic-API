from fastapi import FastAPI
from astral import LocationInfo
from astral.sun import sun
from datetime import datetime,date
from astral import moon

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
    

@app.get("/moon")
def get_moonINFO():
    phaseValue = moon.phase(date.today())

    return{
        "date" : str(date.today()),
        "moon_phase": getMoonPhaseName(phaseValue),
        "phase_value" : round(phaseValue,2)
    }




