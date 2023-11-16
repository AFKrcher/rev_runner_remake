import os
from skyfield.api import Topos, load, utc
from datetime import datetime
import pandas as pd
import numpy as np

url = 'http://celestrak.org/NORAD/elements/gp.php?GROUP=last-30-days&FORMAT=2le'
satellites = load.tle_file(url, reload=True)

location = Topos(latitude_degrees=40, longitude_degrees=-105)

ts = load.timescale()
t0 = ts.now()
t1 = t0 + 0.5

# Full version loads sats and groundstations from a JSON file
# Also loads custom TLEs from a local text file
loaded_sats = [sat.model.satnum for sat in satellites]
print("These are the loaded satellites:\n", loaded_sats)

my_sats = input("Enter which satellites you want: ")
sat_list = [int(item.strip()) for item in my_sats.split(',')] if my_sats != "" else loaded_sats[:10]
print("You've selected: ", sat_list)

df = pd.DataFrame([])
for sat in satellites:
    if sat.model.satnum in sat_list:
        pass_times = []
        times, events = sat.find_events(location, t0, t1, altitude_degrees=0.0)
        pair = [None, None]
        for t, evt in zip(times, events):
            pt = t.utc_strftime('%m-%d %H:%M:%S')
            if evt == 0:
                pair[0] = pt
            elif evt == 2:
                pair[1] = pt
                pass_times.append(pair)
                pair = [None, None]
        if pair[0] is not None:
            pass_times.append(pair)

        for pt in pass_times:
            df2 = pd.DataFrame({'Sat': sat.model.satnum, 'Rise': pt[0], 'Fall': pt[1]}, index=[0])
            df = pd.concat([df,df2])
        
df = df.sort_values(by="Rise")
print(df)
df.to_csv('access.csv', index=False)
os.startfile("access.csv")
input("Press any button to close.")
