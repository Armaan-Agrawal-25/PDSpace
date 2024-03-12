from flask import Flask, session, redirect, url_for, request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import os
from os import times_result
import numpy as np
import pandas as pd
from datetime import datetime
import random

reservations_df = pd.read_csv('reservations.csv')

dict_times = {"8:00 AM" : True, "8:30 AM" : True, "9:00 AM" : True, "9:30 AM" : True, "10:00 AM": True, "10:30 AM": True, "11:00 AM": True, "11:30 AM": True, "12:00 PM": True, "12:30 PM": True, "1:00 PM": True, "1:30 PM": True, "2:00 PM": True, "2:30 PM": True, "3:00 PM": True, "3:30 PM": True, "4:00 PM": True, "4:30 PM": True, "5:00 PM": True}

conference_room_availability = {
      1: {time: True for time in dict_times},
      2: {time: True for time in dict_times},
      3: {time: True for time in dict_times}
}

def getReservations():
    return reservations_df


def getAvailability():
    return conference_room_availability


def getKey(dictionary, n):
    if n < 0:
        n += len(dictionary)
    for i, key in enumerate(dictionary.keys()):
        if i == n:
            return key
    raise IndexError("dictionary index out of range")


def credentialsToDict(credentials):
    return {'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes}


def convertToIsoFormat(date, time):
      date_time_str = f"{date} {time}"
      date_time_obj = datetime.strptime(date_time_str, "%m/%d/%y %I:%M %p")
      iso_format_str = date_time_obj.isoformat()

      return iso_format_str


def generate_random_code(length=8):
    return ''.join(random.choices('0123456789', k=length))


def createEvent(start_time_str, end_time_str, summary, email, description=None, location=None):
    if 'credentials' not in session:
        return redirect(url_for('authorize'))

    credentials = Credentials(**session['credentials'])
    if not credentials.valid:
        if credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            return redirect(url_for('authorize'))

    service = build('calendar', 'v3', credentials=credentials)

    event = {
        'summary': summary,
        'location': location,
        'description': description,
        'start': {'dateTime': start_time_str, 'timeZone': 'America/New_York'},
        'end': {'dateTime': end_time_str, 'timeZone': 'America/New_York'},
    }

    event = service.events().insert(calendarId='primary', body=event).execute()

    event_id = event['id']

    return event_id


def deleteEvent(event_id):
    if 'credentials' not in session:
        return redirect(url_for('authorize'))

    credentials = Credentials(**session['credentials'])
    if not credentials.valid:
        if credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            return redirect(url_for('authorize'))

    service = build('calendar', 'v3', credentials=credentials)
    service.events().delete(calendarId='primary', eventId=event_id).execute()
    

def createReservation(name, email, room_number, start_time, end_time, date):
    global reservations_df, conference_room_availability

    room_number = int(room_number)

    start_time_str = convertToIsoFormat(date, start_time)
    end_time_str = convertToIsoFormat(date, end_time)
    summary = 'Busy'
    description = 'Busy'

    print(start_time_str)
    print(end_time_str)

    if room_number == 1:
      location = "US Library Conference Room #1"
      eventID = createEvent(start_time_str, end_time_str, summary, description, location)
    elif room_number == 2:
      location = "US Library Conference Room #2"
      eventID = createEvent(start_time_str, end_time_str, summary, description, location)
    else:
      location = "US Library Classroom"
      eventID = createEvent(start_time_str, end_time_str, summary, description, location)

    if not conference_room_availability[room_number][start_time]:
        return "Not Available"

    conference_room_availability[room_number][start_time] = False

    for i in range(list(dict_times).index(start_time), list(dict_times).index(end_time)):
            key = getKey(dict_times, i)
            conference_room_availability[room_number][key] = False

    newListing = pd.Series({
            "Name": name,
            "Email": email,
            "RoomNumber": room_number,
            "StartTime": start_time,
            "EndTime": end_time,
            "Date": date,
            "EventID": eventID
    })

    reservations_df = pd.concat([reservations_df, newListing.to_frame().T], ignore_index=True)
    reservations_df.to_csv('reservations.csv', index=False)

    convertAvailability(conference_room_availability)

    return eventID


def cancelReservation(event_id):
    global reservations_df, conference_room_availability

    reservation = reservations_df.loc[reservations_df['EventID'] == event_id]

    if not reservation.empty:
        room_number = int(reservation['RoomNumber'].values[0])
        start_time = reservation['StartTime'].values[0]
        end_time = reservation['EndTime'].values[0]

        conference_room_availability[room_number][start_time] = True
        for i in range(list(dict_times).index(start_time), list(dict_times).index(end_time)):
            key = getKey(dict_times, i)
            conference_room_availability[room_number][key] = True

        reservations_df.drop(reservation.index, inplace=True)
        reservations_df.to_csv('reservations.csv', index=False)

        convertAvailability(conference_room_availability)

        deleteEvent(event_id)


def convertAvailability(availability):
    availability_list = []

    for room, times in availability.items():
        for time, available in times.items():
            end_time_index = list(dict_times).index(time) + 1

            if end_time_index < len(dict_times):
                end_time = getKey(dict_times, end_time_index)
            else:
                end_time = time

            availability_list.append({
                'RoomNumber': room,
                'Time': f'{time} - {end_time}',
                'Available': 'Yes' if available else 'No'
            })

    availability_df = pd.DataFrame(availability_list)
    availability_df.to_csv('availability.csv', index=False)

    return availability_df

def convertEventID(eventID):
    availability_list = []

    for room, times in availability.items():
        for time, available in times.items():
            end_time_index = list(dict_times).index(time) + 1

            if end_time_index < len(dict_times):
                end_time = getKey(dict_times, end_time_index)
            else:
                end_time = time

            availability_list.append({
                'RoomNumber': room,
                'Time': f'{time} - {end_time}',
                'Available': 'Yes' if available else 'No'
            })

    availability_df = pd.DataFrame(availability_list)
    availability_df.to_csv('availability.csv', index=False)

    return availability_df
  

def loadAvailability():
    try:
        availability_df = pd.read_csv('availability.csv')
        availability_dict = {}
        for room in availability_df['Room Number'].unique():
            room_availability = availability_df[availability_df['Room Number'] == room]
            availability_dict[room] = dict(zip(room_availability['Time'], room_availability['Available']))

        return availability_dict

    except FileNotFoundError:
      return {
            1: {time: True for time in dict_times},
            2: {time: True for time in dict_times},
            3: {time: True for time in dict_times}
      }


def blur(event_ID):
    return "*****"


def searchRoom(df, room):
    filtered = df[(df['RoomNumber'] == room)]
    return filtered


def searchTime(df, time):
    filtered = df[(df['Time'] == time)]
    return filtered


def searchRoomAndTime(df, room, time):
    filtered = df[(df['RoomNumber'] == room) & (df['Time'] == time)]
    return filtered


def clearReservations():
    global reservations_df
    columns = ['Name', 'Email', 'RoomNumber', 'StartTime', 'EndTime', 'Date', 'EventID']
    reservations_df = pd.DataFrame(columns=columns)
    reservations_df.to_csv('reservations.csv', index=False)


def rename_column(df, old_name, new_name):
    df_copy = df.copy()
    return df_copy.rename(columns={old_name: new_name})


def resetAvailabilities():
    global conference_room_availability, dict_times

    conference_room_availability = {
        1: {time: True for time in dict_times},
        2: {time: True for time in dict_times},
        3: {time: True for time in dict_times}
    }

    convertAvailability(conference_room_availability)