from stravalib.client import Client

client_id = 26296  # Replace this ID
client = Client()
url = client.authorization_url(client_id=client_id,
                               redirect_uri='http://127.0.0.1:8000/authorization',
                               scope='view_private')
print(url)
