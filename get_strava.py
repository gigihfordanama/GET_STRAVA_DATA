from stravalib.client import Client
import pandas as pd
from datetime import datetime
from pytz import timezone


client = Client()
code = 'yourCode'
client_id = 38768
client_secret = 'YourSecret'

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
    for key, value in streams.items():
        streams[key] = value.data

    df_overview = df_overview.append(pd.DataFrame([{
        'Name': activity.name,
        'Date': activity.start_date_local,
        'Durasi [min]': int(activity.moving_time.seconds / 60),
        'Jarak [m]': round(activity.distance.num, 1),
        'Measurements': list(streams.keys())
    }], index=[activity.id]))
    activities[activity.id] = pd.DataFrame(streams)
writer = pd.ExcelWriter('strava_export_{}.xlsx'.format(str(year)), engine='openpyxl')
df_overview.to_excel(writer, "Overview")

for activity_id, df in activities.items():
    df.to_excel(writer, ' '.join([str(df_overview.loc[activity_id]['Date'].date()),
    df_overview.loc[activity_id]['Name']])[:30])

writer.save()
