#!/usr/bin/env python
from stravalib.client import Client
import pandas as pd
from datetime import datetime
from pytz import timezone

import MySQLdb as mdb
import datetime

conn = mdb.connect(host='localhost', user='User', passwd='PWD', db='DB')

cursor = conn.cursor ()
cursor.execute ("DELETE FROM strava where unik_id IS NOT NULL")
row = cursor.fetchall()
print "RESULT:", row






client = Client()
code = 'xxx'
client_id =  xxx
client_secret = 'xxx'


year = 2019
resolution = 'high'
types = ['time', 'altitude', 'heartrate', 'temp', 'distance', 'watts']

access_token = client.exchange_code_for_token(client_id=client_id,
                        client_secret=client_secret,
                        code=code)


client = Client(access_token=access_token)
df_overview = pd.DataFrame()
activities = dict()

for activity in client.get_activities(after='{}-01-01T00:00:00Z'.format(str(year)),
                                before='{}-01-01T00:00:00Z'.format(str(year + 1))):
    streams = client.get_activity_streams(activity.id,
                                        types=types,
                                        series_type='time',
                                        resolution=resolution)

    #print activity.id
    #print activity.start_date_local
    #print activity.moving_time.seconds
    #print activity.distance.num
    #print float(activity.average_speed)
    #print float(activity.max_speed)
    #print activity.name


    insert_query = ("""INSERT INTO strava (unik_id, waktu, nama_peserta, durasi_detik, jarak_tempuh, kec_max, kec_rata2) VALUES (%s, %s, %s, %s, %s, %s, %s);""")
    cursor.execute(insert_query, (int(activity.id), activity.start_date_local, activity.name, activity.moving_time.seconds, activity.distance.num, float(activity.max_speed),float( activity.average_speed)))


    for key, value in streams.items():
        streams[key] = value.data

    df_overview = df_overview.append(pd.DataFrame([{
        'Nama Peserta': activity.name,
        'Waktu': activity.start_date_local,
        'Durasi [menit]': float(activity.moving_time.seconds / 60),
        'Durasi [detik]': int(activity.moving_time.seconds),
        'Jarak [meter]': round(activity.distance.num, 1),
        'Kec. Rata2 (m/s)': activity.average_speed,
        'Kec. Maks (m/s)': activity.max_speed,
    }], index=[activity.id]))
    activities[activity.id] = pd.DataFrame(streams)

writer = pd.ExcelWriter('strava_export_{}.xlsx'.format(str(year)), engine='openpyxl')
df_overview.to_excel(writer, "Laporan")
for activity_id, df in activities.items():
    df.to_excel(writer, ' '.join([str(df_overview.loc[activity_id]['Waktu'].date()),
    df_overview.loc[activity_id]['Nama Peserta']])[:30])

writer.save()
conn.commit()
cursor.close()
conn.close()
                   
