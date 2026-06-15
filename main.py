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



