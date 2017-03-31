import os

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
    # Determine if the user is logged in.
    hasEvents = True
    # Select and display all events in the database
    events = pg.getEvents()
    tours = pg.getTournaments()
    if 'userName' in session:
        user = [session['userName'], session['email']]
    else:
        user = ['', '']
        return render_template("events.html",events=events,user=user,eventsAvailable=hasEvents,tours=tours)
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
    
    return render_template('events.html', eventsAvailable=hasEvents, events=events, user=user,tours=tours)

@app.route('/eventForm')
def eventFormPage():
    # Determine if the user is logged in.
    if 'userName' in session:
        user = [session['userName'], session['email']]
    else:
        user = ['', '']
    hasEvents = True
    events = [{'tourney': 'DC HEMA Open', 'club': 'Virginia Academy of Fencing', 'dates': 'January 13-15, 2017', 'location': 'National Harbor, MD'},
    {'tourney': 'Shortpoint', 'club': 'Capital KDF', 'dates': 'April 1, 2017', 'location': 'Annadale, VA'},
    {'tourney': 'Longpoint', 'club': 'Maryland KDF', 'dates': 'July 6-9, 2017', 'location': 'Baltimore, MD'}]
    return render_template('eventForm.html', eventsAvailable=hasEvents, events=events, user=user)


@app.route('/matchForm')
def matchFormPage():
    # Determine if the user is logged in.
    if 'userName' in session:
        user = [session['userName'], session['email']]
    else:
        user = ['', '']
    hasEvents = True
    events = [{'tourney': 'DC HEMA Open', 'club': 'Virginia Academy of Fencing', 'dates': 'January 13-15, 2017', 'location': 'National Harbor, MD'},
    {'tourney': 'Shortpoint', 'club': 'Capital KDF', 'dates': 'April 1, 2017', 'location': 'Annadale, VA'},
    {'tourney': 'Longpoint', 'club': 'Maryland KDF', 'dates': 'July 6-9, 2017', 'location': 'Baltimore, MD'}]
    return render_template('matchForm.html', eventsAvailable=hasEvents, events=events, user=user)

@app.route('/tourneyForm')
def tourneyFormPage():
    # Determine if the user is logged in.
    if 'userName' in session:
        user = [session['userName'], session['email']]
    else:
        user = ['', '']
    return render_template('tourneyForm.html', user=user)

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
