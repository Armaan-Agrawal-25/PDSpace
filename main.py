from flask import Flask, session, redirect, url_for, request, render_template
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import os
import numpy as np
import pandas as pd
from functions import *


app = Flask(__name__)
app.secret_key = "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"

 
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
CLIENT_SECRETS_FILE = "client_secret.json"


SCOPES = ['https://www.googleapis.com/auth/calendar.events']


@app.route('/authorize')
def authorize():
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE,
                                                     SCOPES)
    flow.redirect_uri = url_for('oauth2callback', _external=True,
                                _scheme='http')
    authorization_url, state = flow.authorization_url(access_type='offline',     include_granted_scopes='true')
    session['state'] = state
    return redirect(authorization_url)


@app.route('/oauth2callback')
def oauth2callback():
    state = session['state']
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES, state=state)
    flow.redirect_uri = url_for('oauth2callback', _external=True, _scheme='http')
    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)
    credentials = flow.credentials
    session['credentials'] = credentialsToDict(credentials)
    return redirect(url_for('home'))


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/makeReservation')
def make_reservation():
    return render_template('makeReservation.html')


@app.route('/deleteReservation')
def delete_reservation():
    return render_template('deleteReservation.html')


@app.route('/confirmReservation')
def confirm_reservations():
    room_number = request.args.get('room_number', '')
    start_time = request.args.get('start_time', '')
    end_time = request.args.get('end_time', '')
    name = request.args.get('name', '')
    email = request.args.get('email', '')
    date = request.args.get('date', '')
    event_id =  createReservation(name, email, room_number, start_time, end_time, date)

    if event_id == "Not Available":
        return redirect(url_for('not_available_route'))
    else:
        return render_template('confirmReservation.html', room_number=room_number, start_time=start_time, end_time=end_time, name=name, email=email, date=date, event_id=event_id)


@app.route('/confirmCancellation')
def confirm_cancellation():
    event_ID = request.args.get('event_ID', '')

    cancelReservation(event_ID)

    return render_template('confirmCancellation.html', event_id=event_ID)


@app.route('/viewReservations')
def view_reservations():
    reservations = getReservations()
    reservations = reservations.drop_duplicates()

    if not reservations.empty and 'EventID' in reservations.columns:
        reservations["EventID"] = reservations["EventID"].apply(blur)

    return render_template('viewReservations.html', dataframe=reservations)


@app.route('/viewAvailability')
def view_availability():
    availability = convertAvailability(getAvailability())
    availability = availability[availability["Time"] != "5:00 PM - 5:00 PM"]

    return render_template('viewAvailability.html', dataframe=availability)


@app.route('/filteredAvailabilities',methods = ['POST', 'GET'])
def filteredAvailabilities():
   category = request.args.get('category', '')
   room = request.args.get('room', '')
   time = request.args.get('time', '')
   
   availability = convertAvailability(getAvailability())

   if category == "Time":
      filtered = searchTime(availability, time)
   elif category == "Room":
      filtered = searchRoom(availability, int(room))
   else:
      filtered = searchRoomAndTime(availability, int(room), time)

   return render_template('filteredAvailabilities.html', dataframe=filtered, room=room, time=time)


@app.route('/notAvailable')
def not_available_route():
    return 'Time slot is not available. Please select another time slot.'


@app.route('/clearEverything')
def clear_everything():
    clearReservations()
    resetAvailabilities()
    return 'Reservations have been cleared and availabilities have been reset.'


if __name__ == "__main__":
  app.run('0.0.0.0', 8080)

