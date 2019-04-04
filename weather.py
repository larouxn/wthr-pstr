import requests, json, time, sys
from datetime import datetime
from pytz import timezone
from subprocess import call
from omega_gpio import OmegaGPIO

#Making sure we're connected to the internet, otherwise we just loop and keep checking

def connected_to_internet(url='http://www.google.com/', timeout=5):
    try:
        _ = requests.get(url, timeout=timeout)
        #print("we're online")
        return True
    except requests.ConnectionError:
        #print("No internet connection available.")
        return False
    
online = connected_to_internet()

while online is False:
    print('not online')
    call(["logger", "-t", "weather", "Not online"])
    time.sleep(60)
    online = connected_to_internet()

print('We are online')
call(["logger", "-t", "weather", "we are online"])

config = '/root/.config.txt'
creds = open(config,'r').read().split('\n')

max1 = creds[0]
max2 = creds[1]
api = creds[2]


#Setting up Omega's pins
try:
    omega = OmegaGPIO()

    def clear_pins():
        omega.pin_off(2)
        omega.pin_off(17)
        omega.pin_off(16)

        omega.pin_off(15)
        omega.pin_off(46)
        omega.pin_off(45) 

        omega.pin_off(19)
        omega.pin_off(4)
        omega.pin_off(5)

        omega.pin_off(6)
        omega.pin_off(1)
        omega.pin_off(0)
        omega.pin_off(18)

    try:
           clear_pins()
    except:
           print('failed to set up pins')
           call(["logger", "-t", "weather", "failed to set up pins"])
           
    print('GPIO enabled')
    call(["logger", "-t", "weather", "GPIO enabled"])
        
except:
    print('cant enable Omega GPIO')
    call(["logger", "-t", "weather", "cant enable Omega GPIO"])

try:
    #getting maxmind info for own IP address
    r = requests.get('https://geoip.maxmind.com/geoip/v2.1/city/me', auth=(max1, max2))
    maxmind_info = r.json()
    location_info = maxmind_info['location']

    location_info['latitude']
    location_info['longitude']

    coords = str(location_info['latitude']), str(location_info['longitude'])

    lat = coords[0]
    long = coords[1]

    coordinates = lat + ',' + long

except:
    print('ip info error')
    call(["logger", "-t", "weather", "ip info error"])


def get_time():
    TZ = location_info['time_zone']
    #using timezone ID to get local time
    local = timezone(TZ)
    full_local_time = datetime.now(local)
    h_local_time = full_local_time.strftime('%H')
    m_local_time = full_local_time.strftime('%M')
    m_local_time = 1.66666*int(m_local_time)
    local_time = int(h_local_time) + 0.01*(int(m_local_time))
    return local_time

try:
    local_time = get_time()
    print(local_time)
    call(["logger", "-t", "weather", "local_time"])
except:
    print('couldnt get time')
    call(["logger", "-t", "weather", "couldnt get time"])
    



try:

    #Api locations finder
    URL = 'http://dataservice.accuweather.com/locations/v1/cities/geoposition/search.json?q='+ coordinates +'&apikey='+ api

    #Requesting location data, then converting to a library
    res = requests.get(URL)
    locationdata = res.json()
    #Below is location key of Google coordinates
    geokey = locationdata['Key']

    ######

    #Create dictionary
    forecast = {'test':'0'}

    #Creating entries for every hour of the day
    for i in range(25):
            forecast[i] = '0'
            
    #Adding :00 to each key
    forecast = {f'{k}:00': v for k, v in forecast.items()}


except:
    print('fail getting weather data')
    call(["logger", "-t", "weather", "fail getting weather data"])

while 1 == 1:
    print('enter loop')
    call(["logger", "-t", "weather", "enter loop"])
    #Loops between 4am and 11pm
    while local_time >= 4 and local_time <= 23:
        print('in second loop')
        call(["logger", "-t", "weather", "in second loop"])
        
        #Saving 9am and 12pm weather so can add it back in after old weather addition
        if local_time >= 21 and local_time <= 25:
            nine_saved_weather = forecast['9:00']
            twelve_saved_weather = forecast['12:00']

            
        #Get weather data for specified location request, then parse to list
        weatherURL= 'http://dataservice.accuweather.com/forecasts/v1/hourly/12hour/' + geokey + '?apikey=' + api

        try:
                res1 = requests.get(weatherURL)
                weatherdata = res1.json()

                #Function creates dictionary with hour:weather cond
                def build_dict(x):
                    p = weatherdata[x]   
                    H = p['DateTime']
                    h = (H[11:16])
                    F = p['IconPhrase']
                    forecast[h] = F

        except:
                print('accuweather error')
                call(["logger", "-t", "weather", "accuweather error"])

        #create list of numbers to use in creating forecast w/ build_dict
        numbers = [0,1,2,3,4,5,6,7,8,9,10,11]

        for item in numbers:
                build_dict(item)

                
        #accounting for weird AccuWeather format change to 08:00 from 8:00 in early morning.
        try:
            forecast['8:00'] = forecast['08:00']

        except:
                print('didnt update 8am')
                call(["logger", "-t", "weather", "didnt update 8am"])

        ##################### Getting historical weather data ###########
        try:
            #Create dictionary
            old_forecast = {'test':'0'}
                    
            #Adding :00 to each key
            old_forecast = {f'{k}:00': v for k, v in old_forecast.items()}

            #Get old weather data for specified location request, then parse to list
            old_weatherURL= 'http://dataservice.accuweather.com/currentconditions/v1/' + geokey + '/historical/24?apikey=' + api
            old_res = requests.get(old_weatherURL)
            old_weatherdata = old_res.json()

            #Function creates dictionary with hour:weather cond
            def old_build_dict(x):
                p = old_weatherdata[x]   
                H = p['LocalObservationDateTime']
                h = (H[11:14])
                F = p['WeatherText']
                old_forecast[h] = F

            #create list of numbers to use in creating forecast w/ build_dict
            old_numbers = [0,1,2,3,4,5,6, 7, 8, 9, 10, 11, 12]

            for item in old_numbers:
                    old_build_dict(item)

            #how many hours in the past are you going to add to dictionary? don't want to overwrite this evening with yday
            prev = local_time - 5
            ext_prev = local_time - 12
            #temporarily make int, instead of float
            prev = int(prev)
            ext_prev = int(ext_prev)
            
        except:
            print('getting historical weather data error')
        
        #Just 5 hours in the past
        if local_time >= 5 and local_time <= 12:
            for i in range(prev, int(local_time)):

                if int(i) <= 9 and int(i) >= 1:
                    j = (str(i)).zfill(2)
                else:
                    j = i
                try:
                    forecast[(str(i) + ':00')] = str(old_forecast[str(j) + ':'])
                except:
                    print('')

        #12 hours in the past        
        if local_time >= 12 and local_time <= 23:

            for i in range(ext_prev, int(local_time)):
            
                if int(i) <= 9 and int(i) >= 1:
                    j = (str(i)).zfill(2)
                else:
                    j = i
                try:
                    forecast[(str(i) + ':00')] = str(old_forecast[str(j) + ':'])
                except:
                    print('')

                    
        ##################### End of old weather data section ###########        


        #putting saved weather back in for 9am and 12pm (so it's todays not tomorrows)
        if local_time >= 21 and local_time <= 25:
            forecast['9:00'] = nine_saved_weather
            forecast['12:00'] = twelve_saved_weather          

        print(forecast)
        call(["logger", "-t", "weather", str(forecast)])

        #####getting temperature of this hour#####
        try:
                temp_dict = weatherdata[1]
                temp_details = temp_dict['Temperature']

                #temp in fahrenheit
                temp = temp_details['Value']
                temp = int(temp)
                
        except:
                time.sleep(o)

        #######GPIO_Allocation#######

        #Class conversions

        #Rainy - 'Rain' 'Showers' 'Fog' 'Flurries' 'T-storms'
        #Cloudy - 'Mostly Cloudy' 'Partly Cloudy' 'Cloudy'
        #Sunny - 'Clear' 'Partly sunny' 'Mostly Sunny' 'Sunny'


        #Turning on correct pins/icons
        pin_timer = 0
        clear_pins()
        Rain = ['Rain', 'Showers', 'Fog', 'Flurries', 'T-storms', 'Snow', 'Mostly Cloudy w/ Showers', 'Partly Sunny w/ Showers', 'Mostly Cloudy w/ T-Storms', 'Partly Sunny w/ T-Storms', 'Mostly Cloudy w/ Flurries', 'Partly Sunny w/ Flurries', 'Mostly Cloudy w/ Snow', 'Ice', 'Sleet', 'Freezing Rain', 'Rain and Snow', 'Partly Cloudy w/ Showers', 'Mostly Cloudy w/ Showers', 'Partly Cloudy w/ T-Storms', 'Mostly Cloudy w/ T-Storms', 'Mostly Cloudy w/ Flurries', 'Mostly Cloudy w/ Snow']
        Cloud = ['Mostly cloudy', 'A shower', 'Partly cloudy', 'Intermittent clouds', 'Cloudy', 'Dreary (Overcast)', 'Fog', 'Some clouds', 'Some clouds']
        Sun = ['Clear', 'Partly sunny', 'Mostly sunny', 'Sunny', 'Hazy', 'Hazy sunshine', 'Intermittent Clouds', 'Mostly clear', 'Clouds and sun']

        #aslong as cycle hasn't gone for 55mins, we continue
        while pin_timer <= 3300:
                print(pin_timer)
                call(["logger", "-t", "weather", str(pin_timer)])
                try:
                    
                    #8am
                    if forecast['8:00'] in Rain:                        
                        omega.pin_on(2)
                        print('8R')
                        call(["logger", "-t", "weather", "8R"])

                    if forecast['8:00'] in Cloud:
                        omega.pin_on(17)
                        print('8C')
                        call(["logger", "-t", "weather", "8C"])

                    if forecast['8:00'] in Sun:
                        omega.pin_on(16)
                        print('8S')
                        call(["logger", "-t", "weather", "8S"])

                    #12pm
                    if forecast['12:00'] in Rain: 
                        omega.pin_on(15)
                        print('12R')
                        call(["logger", "-t", "weather", "12R"])

                    if forecast['12:00'] in Cloud: 
                        omega.pin_on(46)
                        print('12C')
                        call(["logger", "-t", "weather", "12C"])

                    if forecast['12:00'] in Sun:
                        omega.pin_on(13)
                        print('12S')
                        call(["logger", "-t", "weather", "12S"])

                    #4pm
                    if forecast['16:00'] in Rain:
                        omega.pin_on(19)
                        print('16R')
                        call(["logger", "-t", "weather", "16R"])

                    if forecast['16:00'] in Cloud:
                        omega.pin_on(4)
                        print('16C')
                        call(["logger", "-t", "weather", "16C"])

                    if forecast['16:00'] in Sun:
                        omega.pin_on(5)
                        print('16S')
                        call(["logger", "-t", "weather", "16S"])

                    #8pm
                    if forecast['20:00'] in Rain:
                        omega.pin_on(18)
                        print('20R')
                        call(["logger", "-t", "weather", "20R"])

                    if forecast['20:00'] in Cloud:
                        omega.pin_on(1)
                        print('20C')
                        call(["logger", "-t", "weather", "20C"])

                    if forecast['20:00'] in Sun:
                        omega.pin_on(0)
                        print('20S')
                        call(["logger", "-t", "weather", "20S"])

                    pin_timer = pin_timer + 550
                    time.sleep(550)
                    
                # If there's problems getting weather, program just waits before trying in next loop around.    
                except:
                    pin_timer = pin_timer + 550
                    time.sleep(550)

                if temp >= 88 or temp == 88:
                        
                        try:
                                print('31c or hotter so pins off for 5')
                                call(["logger", "-t", "weather", "31C or hotter so pins off for 5"])
                                clear_pins()

                                pin_timer = pin_timer + 275
                                time.sleep(275)
                                print(pin_timer)
                                call(["logger", "-t", "weather", str(pin_timer)])

                        except:
                                pin_timer = pin_timer + 275
                                time.sleep(275)
                                print(pin_timer)
                                call(["logger", "-t", "weather", str(pin_timer)])

                else:
                        pin_timer = pin_timer + 275
                        time.sleep(275)
                        print(pin_timer)
                        call(["logger", "-t", "weather", str(pin_timer)])

                        


                
        else:
                print('pins turning off and resetting pin_timer')
                call(["logger", "-t", "weather", "pins turning off and resetting pin_timer"])
                pin_timer = 0

                #turning off pins for 5 mins
                try:
                        print('55mins up, time for a 5min break')
                        call(["logger", "-t", "weather", "55mins up, time for a 5min break"])
                        time.sleep(300)
                        clear_pins()
                        
                except:
                        print('55mins up, time for a 5min break')
                        call(["logger", "-t", "weather", "55mins up, timne for a 5min break"])
                        time.sleep(300)



        #with the sleep above and sleep below, thats 60mins, so we add +1 hour to the local_time object
        local_time = get_time()
        print("time is "+(str(local_time)))
        call(["logger", "-t", "weather", str(local_time)])

    else:
        #checks every 30 mins to see if it's time to start turning pins on again
        print('sleep_mode')
        print("time is "+(str(local_time)))
        call(["logger", "-t", "weather", str(local_time)])
        time.sleep(1800)
        
        #turning pins off for sleep mode
        try:
            clear_pins()
        except:
            print('')       

        local_time = get_time()
        
