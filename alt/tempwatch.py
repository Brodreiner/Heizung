try:
    import time
    import temperature
    while(True):
        print "Vorlauf Fussbodenheizung:", temperature.vorlaufFussbodenheizung.value, " Grad Celsius"
        time.sleep(1)
except KeyboardInterrupt:
    exit()

