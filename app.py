from flask import Flask, redirect, url_for, session, request, render_template
from google_auth_oauthlib.flow import Flow
import os
from googleapiclient.discovery import build
import datetime
from google.oauth2 import credentials as google_credentials
from pathlib import Path

secret_path = Path(__file__).resolve().parent / "client_secret.json"

app = Flask(__name__)

def date_to_datetime_local(date_str):
    if date_str:
        date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S%z')
        return date_obj.strftime('%Y-%m-%dT%H:%M')
    return ''

app.jinja_env.filters['date_to_datetime_local'] = date_to_datetime_local

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'

app.secret_key = os.urandom(24)

@app.route("/")
def about():
    return render_template("index.html")

@app.route('/login')
def login():
    flow = Flow.from_client_secrets_file(
        secret_path,
        scopes=['https://www.googleapis.com/auth/calendar'],
        redirect_uri=url_for('oauth2callback', _external=True))

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true')

    session['state'] = state

    return redirect(authorization_url)

@app.route('/oauth2callback')
def oauth2callback():
    state = session.get('state')

    if not state:
        return "État de session manquant", 400

    flow = Flow.from_client_secrets_file(
        secret_path,
        scopes=['https://www.googleapis.com/auth/calendar'],
        state=state,
        redirect_uri=url_for('oauth2callback', _external=True))

    flow.fetch_token(authorization_response=request.url)

    credentials = flow.credentials
    session['credentials'] = credentials_to_dict(credentials)

    return redirect(url_for('show_events'))

@app.route('/show_events')
def show_events():

    credentials = google_credentials.Credentials(
        **session['credentials'])

    service = create_calendar_service(credentials)
    events = list_upcoming_events(service)

    return render_template('events.html', events=events)

def format_date(date_str):
    date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S%z')
    return date_obj.strftime('%d/%m/%Y %H:%M')

def credentials_to_dict(credentials):
    return {'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes}

def create_calendar_service(credentials):
    return build('calendar', 'v3', credentials=credentials)

def list_upcoming_events(service, max_results=10):
    now = datetime.datetime.utcnow().isoformat() + 'Z'
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                          maxResults=max_results, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    for event in events:
        if 'dateTime' in event['start']:
            event['start']['dateTime'] = format_date(event['start']['dateTime'])
        if 'dateTime' in event['end']:
            event['end']['dateTime'] = format_date(event['end']['dateTime'])
        event['id'] = event.get('id')

    return events

@app.route('/create_event', methods=['POST'])
def create_event():

    if 'credentials' not in session:
        return redirect(url_for('login'))

    title = request.form.get('title')
    start_date_str = request.form.get('date')

    start_datetime = datetime.datetime.fromisoformat(start_date_str)
    end_datetime = start_datetime + datetime.timedelta(hours=1)  #durée par défaut, on peut modifier la durée de l'événement

    event = {
        'summary': title,
        'start': {'dateTime': start_datetime.isoformat(), 'timeZone': 'Europe/Paris'},
        'end': {'dateTime': end_datetime.isoformat(), 'timeZone': 'Europe/Paris'}
    }

    #créer l'événement via l'api google
    credentials = google_credentials.Credentials(**session['credentials'])
    service = create_calendar_service(credentials)
    service.events().insert(calendarId='primary', body=event).execute()

    return redirect(url_for('show_events'))

@app.route('/delete_event/<event_id>', methods=['POST'])
def delete_event(event_id):

    if 'credentials' not in session:
        return redirect(url_for('login'))

    credentials = google_credentials.Credentials(**session['credentials'])
    service = create_calendar_service(credentials)

    #supprimer l'événement
    try:
        service.events().delete(calendarId='primary', eventId=event_id).execute()
    except Exception as e:
        print(e)

    return redirect(url_for('show_events'))

@app.route('/edit_event/<event_id>', methods=['GET'])
def edit_event(event_id):
    if 'credentials' not in session:
        return redirect(url_for('login'))

    credentials = google_credentials.Credentials(**session['credentials'])
    service = create_calendar_service(credentials)

    #récup données événement
    event = service.events().get(calendarId='primary', eventId=event_id).execute()

    return render_template('edit_event.html', event=event)

@app.route('/update_event/<event_id>', methods=['POST'])
def update_event(event_id):
    if 'credentials' not in session:
        return redirect(url_for('login'))

    #récupérer données formulaire
    title = request.form.get('title')
    start_date_str = request.form.get('date')

    #convertir au format attendu
    start_datetime = datetime.datetime.fromisoformat(start_date_str)
    end_datetime = start_datetime + datetime.timedelta(hours=1)  #durée par défaut

    credentials = google_credentials.Credentials(**session['credentials'])
    service = create_calendar_service(credentials)

    #update les données existantes
    event = service.events().get(calendarId='primary', eventId=event_id).execute()
    event['summary'] = title
    event['start']['dateTime'] = start_datetime.isoformat()
    event['end']['dateTime'] = end_datetime.isoformat()

    updated_event = service.events().update(calendarId='primary', eventId=event_id, body=event).execute()

    return redirect(url_for('show_events'))

if __name__ == "__main__":
    app.run(debug=True)
