**PDSpace:** Designed and developed a Flask web application that allows Princeton Day School students and faculty to book the meeting spaces located in the library. Users can book any of the three library conference rooms for durations ranging from 30 minutes to 2 hours. When a user makes a reservation, an event is created in their Google Calendar with the room and time information. They can also browse available time slots and search for available slots by room, time, or both. Users can also look at existing reservations made by others.

Details:
- Wrote a Python application utilizing the Flask framework that allows a user to browse, create, or cancel reservations.
- Utilized the Pandas library to handle displaying the listings and filtering of said data based on user requests.
- Wrote HTML code to specify the look and design of the application.

Files:
- main.py: Contains the framework for the application, including creating the Flask web app as well as the different pages within the app
- functions.py: Contains the different methods that allow the app to function, including the method that allows a user to create and browse listings.
- templates: Contains the HTML files used to specify the look and design of each specific page, including taking in user input and displaying the listings
- static: Contains the CSS files for helping include styling in the HTML files
- availability.csv: Contains a list of the availabilties of each of the library conference rooms
- reservations.csv: Contains a list of the reservations made by users

