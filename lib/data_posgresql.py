# Samantha Miller (smiller3)
# CPSC-350:  Applications of Databases
# Database access objects stored outside of controller.

import psycopg2
import psycopg2.extras

from lib.config import *

# Connect to the postgreql database.
# Returns a connection object if connection was successful, or None if can't connect.
def connectToPostgres():
  connectionString = 'dbname=%s user=%s password=%s host=%s' % (POSTGRES_DATABASE, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST)
  print connectionString
  # BP2  Use try-except blocks
  try:
    return psycopg2.connect(connectionString)
  except Exception as e:    # BP2 especially this part where you print the exception
  	print(type(e))
	print(e)
	print("Can't connect to database")
	return None


# generic execute statement
# select=True if it is a select statement
#        False if it is an insert
#
def execute_query(query, conn, select=True, args=None):
	print "in execute query"
	cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
	results = None
	try: 
		quer = cur.mogrify(query, args)   # BP6  never use Python concatenation
		                                  # for database queries
		cur.execute(quer)
		if select:
			results = cur.fetchall()
		conn.commit()   # BP5  commit and rollback frequently
	except Exception as e:
		conn.rollback()
		print(type(e))
		print(e)
	cur.close()      # BP3 Dispose of old cursors as soon as possible
	return results

# Creates a new user for TMS
def registerUser(firstName, lastName, password, email, club, region, wantsNews):
  conn = connectToPostgres()
  if conn == None:
    return None
  #crypt(%s, gen_salt('bf')) - use in later lecture?
  query_string = "INSERT INTO users (first_name, last_name, password, email, club, region, wants_news) VALUES (%s, %s, crypt(%s, gen_salt('bf')), %s, %s, %s, %s);"
  execute_query(query_string, conn, select=False,  args=(firstName, lastName, password, email, club, region, wantsNews))
  conn.close()

# Creates a new tournament
def createTournament(eventName, tournamentName, time, ringCount):
  conn = connectToPostgres()
  if conn == None:
    return None
  query_string = "INSERT INTO tournament (tour_id, tour_name, match_length, ring_count, event_id) VALUES (DEFAULT, %s, %s, %s, %s);"
  execute_query(query_string, conn, select=False,  args=(tournamentName, time, ringCount, eventName))
  conn.close()
  
#Creates a new event
def createEvent(eventName, eventDate, ownerId):
  conn = connectToPostgres()
  if conn == None:
    return None
  query_string = "INSERT INTO event (event_id, event_name, event_date,owner_id) VALUES (DEFAULT, %s, %s, 1);" 
  execute_query(query_string, conn, select=False,  args=(eventName, eventDate))
  conn.close()

# Returns a list of all users on the site
def listAllUsers():
  conn = connectToPostgres()
  if conn == None:
    return None
  query_string = "SELECT id, first_name, last_name, club, region from users;"
  results = execute_query(query_string, conn)
  conn.close()
  return results

# Returns a list of all users on the site, given an identifying email.
def listRegionUsers(email):
  conn = connectToPostgres()
  if conn == None:
    return None
  print(email)
  results = None
  query_string1 = "SELECT region from users WHERE email=%s;"
  selectedRegion = execute_query(query_string1, conn, args=(email,))
  if selectedRegion != None:
    print(selectedRegion)
    print(selectedRegion[0][0])
    query_string2 = "SELECT id, first_name, last_name, club, region from users where region=%s;"
    results = execute_query(query_string2, conn, args=(selectedRegion[0][0],))
  conn.close()
  return results

# Returns true if user is logged into site
def logIn(email, password):
  conn = connectToPostgres()
  if conn == None:
    return None
  query_string = "SELECT first_name, email from users where email=%s and password=crypt(%s, password);"
  results = execute_query(query_string, conn, args=(email, password))
  conn.close()
  return results

# Creates a tournament for an event
#def createTournament(firstName, lastName, password, email, club, region, wantsNews):
#  conn = connectToPostgres()
#  if conn == None:
#    return None
#  #crypt(%s, gen_salt('bf')) - use in later lecture?
#  query_string = "INSERT INTO users (first_name, last_name, password, email, club, region, wants_news) VALUES (%s, %s, crypt(%s, gen_salt('bf')), %s, %s, %s, %s);"
#  execute_query(query_string, conn, select=False,  args=(firstName, lastName, password, email, club, region, wantsNews))
#  conn.close()

# Returns a list of events on the site
def getEvents():
  conn = connectToPostgres()
  if conn == None:
    return None
  query_string = "SELECT e.event_id, e.event_name, e.event_date, u.email from event AS e JOIN users AS u ON e.owner_id = u.id;"
  results = execute_query(query_string, conn)
  conn.close()
  return results

# Returns a list of events on the site
def getTournaments():
  conn = connectToPostgres()
  if conn == None:
    return None
  query_string = "SELECT t.tour_id, t.tour_name, t.match_length, t.ring_count, e.event_name from tournament t JOIN event e ON t.event_id = e.event_id;"
  results = execute_query(query_string, conn)
  conn.close()
  return results
  
# Returns a list of events on the site
def getTournamentsByEventId(e_id):
  conn = connectToPostgres()
  if conn == None:
    return None
  query_string = "SELECT t.tour_id, t.tour_name, t.match_length, t.ring_count, e.event_name from tournament t JOIN event e ON t.event_id = e.event_id WHERE e.event_id=%s;"
  results = execute_query(query_string, conn, args=(e_id))
  conn.close()
  return results

# Returns a tournament name by its id value
def getTourNameByTourId(t_id):
  conn = connectToPostgres()
  if conn == None:
    return None
  query_string = "SELECT tour_name from tournament WHERE tour_id=%s;"
  results = execute_query(query_string, conn, args=(t_id))
  conn.close()
  return results

#Insert data into match database
def insertIntoMatch(fighter1, fighter2, exchange_type, points1, points2, timestamp, counter, tour_id):
  conn = connectToPostgres()
  if conn == None:
    return None
  query_string = "INSERT INTO match (fighter1, fighter2, exchange_type, points1, points2, timestamp, bout_id, tour_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"
  execute_query(query_string, conn, select=False,  args=(fighter1,fighter2,exchange_type,points1,points2,timestamp, counter, tour_id))
  conn.close()

def idToName(u_id):
  conn = connectToPostgres()
  if conn == None:
    return None
  query_string = "SELECT last_name, first_name FROM users WHERE id = %s;"
  results = execute_query(query_string, conn)
  conn.close()
  return results

  
  
# Returns a list of matches by a given tournament id
def getMatchesByTourId(t_id):
  conn = connectToPostgres()
  if conn == None:
    return None
  #query_string = "SELECT m.match_id, u1.first_name, u1.last_name, u2.first_name, u2.last_name, m.SUM(points1), m.SUM(points2) from match m JOIN users u1 ON m.fighter1 = u.id JOIN users u2 ON u.fighter2=u2.id WHERE m.tour_id=%s GROUP BY m.match_id, m.fighter1, m.fighter2;"
  query_string = "SELECT match_id, fighter1, fighter2, points1, points2 from match WHERE tour_id=%s"
  results = execute_query(query_string, conn, args=(t_id))
  conn.close()
  return results

# Returns a list of match results (score sums) by a given tournament id
def getMatchResultsByTourId(t_id):
  conn = connectToPostgres()
  if conn == None:
    return None
  #query_string = "SELECT m.match_id, u1.first_name, u1.last_name, u2.first_name, u2.last_name, m.SUM(points1), m.SUM(points2) from match m JOIN users u1 ON m.fighter1 = u.id JOIN users u2 ON u.fighter2=u2.id WHERE m.tour_id=%s GROUP BY m.match_id, m.fighter1, m.fighter2;"
  query_string = "SELECT match_id, fighter1, fighter2, SUM(points1) AS points1, sum(points2) AS points2 from match WHERE tour_id=%s GROUP BY match_id, fighter1, fighter2 ORDER BY match_id"
  results = execute_query(query_string, conn, args=(t_id))
  conn.close()
  return results