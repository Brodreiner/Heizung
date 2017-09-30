import sql

def getOutdoorTemperature():
    import xml.etree.ElementTree as ET
    import urllib2
    url = "http://api.openweathermap.org/data/2.5/weather?q=Lochhausen&mode=xml&APPID=9acd9ad2302f1a6c2437b69ca19c7da5"
    try:
        temperatureInKelvin = ET.parse(urllib2.urlopen(url,timeout=5)).getroot().find("temperature").get("value")
        temperatureInCelsius = float(temperatureInKelvin)-273.15
    except:
        print "Error getting outdoor temperature from " + url + "!"
        sql.reportError("ERROR", "INTERNET_CONNECTION", "Fehler beim Verbinden mit " + url + "!")
        return None
    return temperatureInCelsius


