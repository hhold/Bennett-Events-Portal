# importing required libraries and modules
from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField
from wtforms.fields.html5 import DateField
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import datetime
import sendgrid
import os
from sendgrid.helpers.mail import *

#authentication of firestore credentials
cred = credentials.Certificate('bennettra-f6176-39124368e57f.json')
firebase_admin.initialize_app(cred)

#defining what date 'today' is
todaydate = datetime.datetime.today().strftime('%Y-%m-%d')

#initializing firestore
db = firestore.client()

#initializing Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'bennettsecret'

#a function to count the number of events on a given date, with 'today' as default date
def numofEvents(date_events = todaydate):
    dates_ref = db.collection(date_events)
    totevents = dates_ref.get()
    c = 0
    for i in totevents:
        c+=1
    return c

#index page or main menu
@app.route('/')
def index():
    global numevents
    numevents = numofEvents()
    return render_template('index.html', numevents = numevents) #renders index.html on screen

#making a form for event details
class EventForm(FlaskForm):

    nameClub = StringField('Club Name')
    nameEvent = StringField('Name of Event')
    nameHall = StringField('Name of Hall')
    eventDate = DateField('Date of Event')
    eventTime = StringField('Time')
    eventDetails = StringField('Event Details')

#form event details page
@app.route('/form', methods=['GET', 'POST'])
def form():
    form = EventForm()

    if form.validate_on_submit():   #validating form data
        return dbpush(form.nameClub.data,form.nameEvent.data,form.nameHall.data,form.eventDate.data,form.eventTime.data,form.eventDetails.data)
    return render_template('form.html', form=form)  #in case of invalid data user will be presented with the form again

#sending data to firestore and using SendGrid API to send email invitations
def dbpush(nameClub,nameEvent,nameHall,eventDate,eventTime,eventDetails):

    doc = db.collection(str(eventDate)).document(nameEvent)     #setting data in firestore
    doc.set({
    'Club': nameClub,
    'Event': nameEvent,
    'Venue': nameHall,
    'Date': str(eventDate),
    'Time': eventTime,
    'Details': eventDetails
    })

    sg = sendgrid.SendGridAPIClient(apikey='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')     #sending emails
    from_email = Email("events@bennett")
    to_email = Email("hn5298@bennett.edu.in")
    subject = nameEvent+" at Bennett"
    mailtext = nameClub+" is hosting "+ nameEvent+" on "+str(eventDate)+" at "+eventTime+", venue: "+nameHall+". Details of the event: "+eventDetails+""".

    Looking forward to seeing you there.

    - Bennett Events Portal."""
    content = Content("text/plain", mailtext)
    mail = Mail(from_email, subject, to_email, content)
    response = sg.client.mail.send.post(request_body=mail.get())

    #display success page
    return render_template('success.html')


#input field that allows picking a date through an interactive calendar
class DateViewForm(FlaskForm):
    pickdate = DateField("Choose date")

#form to pick a date
@app.route('/dateview', methods=['GET', 'POST'])
def dateview():
    dateform = DateViewForm()
    if dateform.validate_on_submit():
        return display(str(dateform.pickdate.data))
    return render_template('dateview.html', form = dateform)


#displaying all events on a given date
@app.route('/display', methods=['GET', 'POST'])
def display(date_events = todaydate):
    dates_ref = db.collection(date_events)
    events = dates_ref.get()
    eventscopy = dates_ref.get()
    numevents = numofEvents(date_events)
    if(numevents==0):
        return render_template('display.html', eventdata = 'empty') #display 'no events on this date' page
    else:
        return render_template('display.html', eventdata = events)


if __name__ == '__main__':
    app.run(debug=False)        #setting Flask to production mode
