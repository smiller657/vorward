import os
import json
from lib.config import *
from lib import data_posgresql as pg

from flask import Flask, render_template, request, session
app = Flask(__name__)
app.secret_key=os.urandom(24).encode('hex')

#session variables:  name, email

@app.route('/')
def mainIndex():
    # Determine if the user is logged in.
    if 'userName' in session:
        user = [session['userName'], session['email']]
    else:
        user = ['', '']
    return render_template('index.html', user=user)
    
@app.route('/about')
def aboutPage():
    # Determine if the user is logged in.
    if 'userName' in session:
        user = [session['userName'], session['email']]
    else:
        user = ['', '']
    maintenanceName = "Samantha Miller"
    maintenanceEmail = "smiller3@mail.umw.edu"
    hemaa = {'name': 'HEMA Alliance', 'url' : 'https://www.hemaalliance.com/', 
        'desc' : 'an educational not-for-profit organization that provides independent clubs and schools worldwide with resources',
        'email' : 'governing-council@hemaaliance.com'}
    return render_template('about.html', maintName=maintenanceName, maintEmail=maintenanceEmail, alliance=hemaa, user=user)
    
@app.route('/events', methods=['GET', 'POST'])
def eventPage():
    # Select and display all events in the database
    events = pg.getEvents()
    tours = []
    matches = []
    event_id = 0
    showTor = False
    tour_id = 0
    tour_name = ""
    #If form completed, get info from it.
    if request.method == 'POST':
        print("test in post to events")
        print(request.form)
        if 'formType' in request.form:
            print("in form type loop")
            # Get the data off of the event form
            if request.form['formType'] == 'eventForm':
                ename=request.form['event']
                edate=str(request.form['date'])
                pg.createEvent(ename,edate,1)
            elif request.form['formType'] == 'tourneyForm':
                # Get info off Tournament form to create a tournament
                event=request.form['event']
                tournament=request.form['tournament']
                rings=request.form['rings']
                matchLength=request.form['matchLength']
                print("making tournament")
                pg.createTournament(event, tournament, matchLength, rings)
            
        
        # Display the match information using tour info, if selected
        elif request.form['showEventTour']:
            if request.form['showTourMatch']:
                showTor = True
            print("found showEventTour")
            event_id=request.form['showEventTour']
            print(event_id)
            tours = pg.getTournamentsByEventId(event_id)
            tour_id=request.form['showTourMatch']
            matches = pg.getMatchResultsByTourId(tour_id)
            print(matches)
            tour_name = pg.getTourNameByTourId(tour_id)
        elif request.form['showTours']:
            print("found showTours")
            event_id = request.form['showTours']
            print(event_id)
            tours = pg.getTournamentsByEventId(event_id)
            matches = []
    events = pg.getEvents()
    if 'userName' in session:
        user = [session['userName'], session['email']]
    else:
        user = ['', '']
    return render_template("events.html",events=events,event_id=event_id, user=user, tours=tours, tour_id=tour_id, matches=matches, tour_name=tour_name, seematch=showTor)

@app.route('/eventForm')
def eventFormPage():
    # Determine if the user is logged in.
    if 'userName' in session:
        user = [session['userName'], session['email']]
    else:
        user = ['', '']
    return render_template('eventForm.html', user=user)


@app.route('/matchForm',methods=['GET', 'POST'])
def matchFormPage():
    tour_id = 0
    if request.method == 'POST':
        print("test in post matchForm")
        print(request.form)
        # Display the match information using tour info, if selected
        if request.form['matchTourId'] != "":
            tour_id=request.form['matchTourId']
    # Determine if the user is logged in.
    if 'userName' in session:
        user = [session['userName'], session['email']]
    else:
        user = ['', '']
    return render_template('matchForm.html', user=user,tour_id=tour_id)

@app.route('/matchCreated',methods=['GET', 'POST'])
def matchCreated():
    tour_id = 1
    if request.method == 'POST':
        print("test in post matchCreated")
        # Display the match information using tour info, if selected
        if request.form['matchTourId'] != "":
            tour_id=request.form['matchTourId']
    if 'userName' in session:
        user = [session['userName'], session['email']]
    else:
        user = ['', '']
    fighter1 = request.form['fighter1']
    fighter2 = request.form['fighter2']
    tournament = request.form['tournament']
    passedJson = request.form['jsonDict']
    
    data = json.loads(passedJson)
    
    records = []
    f1Total = 0
    f2Total = 0
    counter = 0
    
    for i in data:
        counter += 1
        dbTimestamp = str(i[0])
        dbExchangeType = str(i[1])
        dbFighter1Points = str(i[2])
        dbFighter2Points = str(i[3])
        f1Total += int(dbFighter1Points)
        f2Total += int(dbFighter2Points)
        newArr = [fighter1,fighter2,tournament,dbTimestamp,dbExchangeType,dbFighter1Points,dbFighter2Points]
        records.append(newArr)
        pg.insertIntoMatch(fighter1, fighter2, dbExchangeType, dbFighter1Points, dbFighter2Points, dbTimestamp, counter, tour_id)
    

    return render_template('matchCreated.html', user=user, records=records, f1Total=f1Total, f2Total=f2Total, fighter1=fighter1, fighter2=fighter2);
    

@app.route('/tourneyForm', methods=['GET', 'POST'])
def tourneyFormPage():
    event_id = 0
    if request.method == 'POST':
        print("test in post")
        # Display the match information using tour info, if selected
        if request.form['tourEventId'] != "":
            event_id=request.form['tourEventId']
    # Determine if the user is logged in.
    if 'userName' in session:
        user = [session['userName'], session['email']]
    else:
        user = ['', '']
    return render_template('tourneyForm.html', user=user, event_id=event_id)

@app.route('/contact')
def contactPage():
    # Determine if the user is logged in.
    if 'userName' in session:
        user = [session['userName'], session['email']]
    else:
        user = ['', '']
    workingEmailer=False
    maintenanceName = "Samantha Miller"
    maintenanceEmail = "smiller3@mail.umw.edu"
    return render_template('contact.html', canEmail=workingEmailer, maintName=maintenanceName, maintEmail=maintenanceEmail, user=user)

@app.route('/logged')
def loggedPage():
    loggedOut = False
    # If user is in session, remove to log out.
    if 'email' in session:
        session.clear()
        loggedOut = True
    # if request.method == 'POST': , methods=['GET', 'POST']
    #    email=request.form['email']
    #    pwd=request.form['pwd']
    #    result = pg.logIn(email, pwd) 
    
    # Determine if the user is logged in.
    if 'userName' in session:
        user = [session['userName'], session['email']]
    else:
        user = ['', '']
    return render_template('logged.html', loggedOut=loggedOut, user=user)

@app.route('/register')
def registerPage():
    # Determine if the user has logged in.
    if 'userName' in session:
        user = [session['userName'], session['email']]
    else:
        user = ['', '']
    return render_template('register.html', selected='register', user=user)

@app.route('/accountCreated', methods=['GET', 'POST'])
def accountCreatedPage():
    unsuccessfulLogin = False
    #If form completed, get info from it.
    if request.method == 'POST':
        print("test in post")
        # Check if we're creating a new account.
        if request.form['formType'] == 'registerForm':
            fname=request.form['fname']
            lname=request.form['lname']
            pwd=request.form['pwd']
            email=request.form['email']
            club = ""
            if request.form.get("club") != None:
                club=request.form['club']
            region=request.form['region']
            newsChecked = False
            if request.form.get("news") != None:
                newsChecked = True
            # Saves new user.
            pg.registerUser(fname, lname, pwd, email, club, region, newsChecked)
            #Logs user into session.
            session['userName'] = fname
            session['email'] = email
            userToLogin = [{'name':fname}, {'email':email}]
        elif request.form['formType'] == 'loginForm':
            # Otherwise, we are logging in.
            email=request.form['email']
            pwd=request.form['pwd']
            userToLogin = pg.logIn(email, pwd)
            # Log in the user if results are not null.
            if userToLogin != None and len(userToLogin) > 0:
                session['userName'] = userToLogin[0][0]
                session['email'] = userToLogin[0][1]
            else:
                unsuccessfulLogin = True
    # If there is a user in the session, maintain them, otherwise pass blank.  And populate user table.
    if 'userName' in session:
        user = [session['userName'], session['email']]
        results = pg.listRegionUsers(user[1])
    else:
        user = ['', '']
        results = pg.listAllUsers()
    return render_template('accountCreated.html', users=results, user=user, failedLogin=unsuccessfulLogin)

if __name__ == '__main__':
    app.run(host=os.getenv('IP', '0.0.0.0'), port=int(os.getenv('PORT', 8080)), debug=True)
