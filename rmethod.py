
import sqlite3
import csv
from tabulate import tabulate as tab


connect = sqlite3.connect('info.db')
c = connect.cursor()


def person_table():
    c.execute("DROP TABLE IF EXISTS Persons;")
    c.execute("""
        CREATE TABLE Persons(
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Firstname TEXT NOT NULL,
            LastName TEXT NOT NULL,
            Email TEXT NOT NULL UNIQUE
    );
    """)    


def role_table():
    c.execute("DROP TABLE IF EXISTS Roles;")
    c.execute("""   
        CREATE TABLE Roles(
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT NOT NULL);
    """)    


def team_table():
    c.execute("DROP TABLE IF EXISTS Teams;")
    c.execute("""
            CREATE TABLE Teams(
                ID integer PRIMARY KEY AUTOINCREMENT,
                Name TEXT NOT NULL,
                SportID INTEGER NOT NULL,
                FOREIGN KEY(SportID) REFERENCES Sports(ID)
     );
    """)    


def sport_table():
    c.execute("DROP TABLE IF EXISTS Sports;")
    c.execute("""
    CREATE TABLE Sports(
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Name TEXT NOT NULL UNIQUE
    );
    """)


def almighty():
    c.execute("DROP TABLE IF EXISTS Cthulhu;")
    c.execute("""
    CREATE TABLE Cthulhu(
        PersonID INTEGER NOT NULL,
        RoleID INTEGER NOT NULL,
        TeamID INTEGER NOT NULL,
        FOREIGN KEY(PersonID) REFERENCES Persons(ID),
        FOREIGN KEY(RoleID) REFERENCES Roles(ID),
        FOREIGN KEY(TeamID) REFERENCES Teams(ID)
    );
    """)

#this removes the duplicates from the sport column
def unique_sports(csv):
    sports = []
    for i in range (len(csv)):
        sports.append(csv[i][5])
    temp_set = set()
    temp_set.update(sports)
    temp_set = list(temp_set)
    #print(temp_set)
    return temp_set
    

#this function deals with reading in the csv and adding the data to the correct tables
#! SORT CANT BE CALLED FIRST YET BECAUSE READ_LIST TAKES IN THE CSV AND ADDS IT TO THE TABLES. 
def read_list(name):
    reply = []
    with open((name + ".csv"), 'r') as f:
        reader = csv.reader(f)
        for r in reader:
            reply.append(r)
            c.execute("INSERT INTO Persons(FirstName, LastName, Email) VALUES (?,?,?);", (r[3], r[4], r[2]))
            c.execute("SELECT * FROM Persons")
    #before we can add sports to the table we need to remove duplicates that is what the function is for^^
    #This is also a different loop because it the iterable (list) is a different length
    headings, form_list = cleaning(reply)
    headings = headings[0]
    sports_list = unique_sports(form_list)
    for sport in sports_list:
        c.execute("INSERT INTO Sports(Name) VALUES(?);", (sport,))
    connect.commit()
    connect.close()
    return headings, form_list, reply


#this needs to be called before the data is added to the tables
#The function purpose is to return a sorted/arranged 2d list of fields
def sort(headings, form_list):
    
    show_fields = ["Parent Email", 
              "Student Email",
              "First Name",
              "Last Name",
              "Year level",
              "Sport",
              "Health Info",
              "Parent Confirmation",
              "Student Confirmation",
              "Payment Method"
              ]
    
    #this little bit makes another my list of fields comparable to 
    fields = []
    for i in show_fields:
        temp_field  = clean_name(i)
        fields.append(temp_field)
    #go through the csv list and sort everything
    #GAME LOOP
    readable_headings = []
    print(headings)
    for q in headings:
        temp_headings = clean_name(q)
        readable_headings.append(temp_headings)
    print(readable_headings)

        
    format()
    #i+1 for the users sake, it will make me lose my mind
    for i in range (len(fields)):
        print(str(i+1) + ", " + str(fields[i]))
    format()
    for i in range (len(form_list)):
        print(form_list[i][0])



#return 3 different things
def clean_name(name):
    boo  = bool
    name = name.lower()
    space_count = name.count(" ")
    if space_count == 0:
        return name
    elif space_count == 1:
        # Two words: combine into one
        words = name.split(" ")
        return "".join(words)
    else:
        print("Hey, I can't tell what datatype this is. Could you please help me out")
        return name

def format():  
    print()
    print("--------------------------------------------------------------------------------------")
    print()


#This function cleans the CSV by removing the unessesary headings and timestamps.
def cleaning(form_list):
    #removing timestamps
    for i in form_list:
        del i[0]
    #pop the headings to a list
    headings = []
    headings.append(form_list.pop(0))
    return headings, form_list
 
def make_tables():
    person_table()
    role_table()
    team_table()
    sport_table()
    team_table()
    almighty()


make_tables()
headings, form_list, reply = read_list("formdraft3")
sort(headings, form_list)
 