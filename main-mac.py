import requests, json, time, sys
from datetime import datetime
from pytz import timezone
#from omega_gpio import OmegaGPIO

#making log entry
#old_stdout = sys.stdout

#file to input log into
#log_file = open("/root/log/log","w")
#sys.stdout = log_file



try:
    #omega = OmegaGPIO()

    #def clear_pins():
    #    omega.pin_off(2)
    #    omega.pin_off(17)
    #    omega.pin_off(16)

    #    omega.pin_off(15)
    #    omega.pin_off(46)
    #    omega.pin_off(45) 

    #    omega.pin_off(19)
    #    omega.pin_off(4)
    #    omega.pin_off(5)

    #   omega.pin_off(6)
    #   omega.pin_off(1)
    #   omega.pin_off(0)
    #   omega.pin_off(18)

    #try:
    #       clear_pins()
    #except:
    #       print('')
    print('GPIO enabled')
        
except:
    print('cant enable Omega GPIO')


try:
    #getting maxmind info for own IP address
    r = requests.get('https://geoip.maxmind.com/geoip/v2.1/city/me', auth=('138089', 'j9Bmlulq9c6i'))
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
except:
    print('couldnt get time')
    



try:
    #AccuWeather API
    api = 'MNH5Q4mOjWPmAFOGFEJqgSO5rLl7zwSs'

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

    #######
    #log out
    #sys.stdout = old_stdout
    #log_file.close()

except:
    print('fail getting weather data')

while 1 == 1:
    print('enter loop')    
    #Loops between 5am and 11pm
    while local_time >= 4 and local_time <= 23:
        print('in second loop')

        #closing log
        #sys.stdout = old_stdout
        #log_file.close()
        #file to input log into
        #log_file = open("/root/log/log","w")
        #sys.stdout = log_file
        
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

        #create list of numbers to use in creating forecast w/ build_dict
        numbers = [0,1,2,3,4,5,6,7,8,9,10,11]

        for item in numbers:
                build_dict(item)

                
        #accounting for weird AccuWeather format change to 08:00 from 8:00 in early morning.
        try:
            forecast['8:00'] = forecast['08:00']

        except:
                print('didnt update 8am')

        ##################### Getting old weather data ###########

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

        #####getting temperature of this hour#####
        try:
                temp_dict = weatherdata[1]
                temp_details = temp_dict['Temperature']

                #temp in fahrenheit
                temp = temp_details['Value']
                temp = int(temp)
                print(temp)
        except:
                time.sleep(o)

        #######GPIO_Allocation#######

        #Class conversions

        #Rainy - 'Rain' 'Showers' 'Fog' 'Flurries' 'T-storms'
        #Cloudy - 'Mostly Cloudy' 'Partly Cloudy' 'Cloudy'
        #Sunny - 'Clear' 'Partly sunny' 'Mostly Sunny' 'Sunny'


        #Turning on correct pins/icons
        pin_timer = 0
        #clear_pins()
        Rain = ['Rain', 'Showers', 'Fog', 'Flurries', 'T-storms', 'Snow', 'Mostly Cloudy w/ Showers', 'Partly Sunny w/ Showers', 'Mostly Cloudy w/ T-Storms', 'Partly Sunny w/ T-Storms', 'Mostly Cloudy w/ Flurries', 'Partly Sunny w/ Flurries', 'Mostly Cloudy w/ Snow', 'Ice', 'Sleet', 'Freezing Rain', 'Rain and Snow', 'Partly Cloudy w/ Showers', 'Mostly Cloudy w/ Showers', 'Partly Cloudy w/ T-Storms', 'Mostly Cloudy w/ T-Storms', 'Mostly Cloudy w/ Flurries', 'Mostly Cloudy w/ Snow']
        Cloud = ['Mostly cloudy', 'Partly cloudy', 'Intermittent clouds', 'Cloudy', 'Dreary (Overcast)', 'Fog', 'Some clouds']
        Sun = ['Clear', 'Partly sunny', 'Mostly sunny', 'Sunny', 'Hazy', 'Hazy sunshine', 'Intermittent Clouds', 'Mostly clear']

        #aslong as cycle hasn't gone for 55mins, we continue
        while pin_timer <= 3300:
                print(pin_timer)
                try:
                    
                    #8am
                    if forecast['8:00'] in Rain:                        
                        #omega.pin_on(2)
                        print('8R')

                    if forecast['8:00'] in Cloud:
                        #omega.pin_on(17)
                        print('8C')

                    if forecast['8:00'] in Sun:
                        #omega.pin_on(16)
                        print('8S')                       

                    #12pm
                    if forecast['12:00'] in Rain: 
                        #omega.pin_on(15)
                        print('12R')

                    if forecast['12:00'] in Cloud: 
                        #omega.pin_on(46)
                        print('12C')

                    if forecast['12:00'] in Sun:
                        #omega.pin_on(13)
                        print('12S')

                    #4pm
                    if forecast['16:00'] in Rain:
                        #omega.pin_on(19)
                        print('16R')

                    if forecast['16:00'] in Cloud:
                        #omega.pin_on(4)
                        print('16C')

                    if forecast['16:00'] in Sun:
                        #omega.pin_on(5)
                        print('16S')

                    #8pm
                    if forecast['20:00'] in Rain:
                        #omega.pin_on(18)
                        print('20R')

                    if forecast['20:00'] in Cloud:
                        #omega.pin_on(1)
                        print('20C')

                    if forecast['20:00'] in Sun:
                        #omega.pin_on(0)
                        print('20S')

                    pin_timer = pin_timer + 550
                    time.sleep(550)
                    
                # If there's problems getting weather, program just waits before trying in next loop around.    
                except:
                    pin_timer = pin_timer + 550
                    time.sleep(550)

                if temp >= 88 or temp == 88:
                        
                        try:
                                print('31c or hotter so pins off for 5')
                                #clear_pins()

                                pin_timer = pin_timer + 275
                                time.sleep(275)
                                print(pin_timer)

                        except:
                                pin_timer = pin_timer + 275
                                time.sleep(275)
                                print(pin_timer)

                else:
                        pin_timer = pin_timer + 275
                        time.sleep(275)
                        print(pin_timer)

                        


                
        else:
                print('pins turning off and resetting pin_timer')
                pin_timer = 0

                #turning off pins for 5 mins
                try:
                        print('55mins up, time for a 5min break')
                        time.sleep(300)
                        #clear_pins()
                        
                except:
                        print('55mins up, time for a 5min break')
                        time.sleep(300)



        #with the sleep above and sleep below, thats 60mins, so we add +1 hour to the local_time object
        local_time = get_time()
        print("time is "+(str(local_time)))
        #closing log
        #sys.stdout = old_stdout
        #log_file.close()

    else:
        #checks every 30 mins to see if it's time to start turning pins on again
        print('sleep_mode')
        print("time is "+(str(local_time)))
        time.sleep(1800)
        
        #turning pins off for sleep mode
        #try:
            #clear_pins()
        #except:
            # print('')       

        local_time = get_time()
        
        #open log
        #log_file = open("/root/log/log","w")
        #sys.stdout = log_file
        
