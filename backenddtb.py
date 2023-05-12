
import sqlite3
import csv
from tabulate import tabulate as tab


connect = sqlite3.connect('info.db')
c = connect.cursor()


def student_table():
    c.execute("DROP TABLE IF EXISTS Students;")
    c.execute("""
    CREATE TABLE Students(
        StudentID INTEGER PRIMARY KEY,
        StudentName TEXT NOT NULL
    );
    """)



def sport_table():
    c.execute("DROP TABLE IF EXISTS Sports;")
    c.execute("""
    CREATE TABLE Sports(
        SportID INTEGER PRIMARY KEY,
        SportName TEXT NOT NULL
    );
    """)



def coach_table():
    c.execute("DROP TABLE IF EXISTS Coaches;")
    c.execute("""
    CREATE TABLE Coaches(
        CoachID INTEGER PRIMARY KEY,
        CoachName TEXT NOT NULL
    );
    """)
    


def readin(name):
    with open((name + ".csv"), 'r') as f:
        reader = csv.reader(f)
        for r in reader:
            if name == "StudentTable":
                student_id = int(r[0])
                student_name = r[1]
                c.execute("INSERT INTO Students (StudentID, StudentName) VALUES(?,?);",
                          (student_id, student_name))
            if name == "SportTable":
                sport_id = int(r[0])
                sport_name = r[1]
                c.execute("INSERT INTO Sports (SportID, SportName)VALUES(?,?);",
                          (sport_id, sport_name))
            if name == "CoachTable":
                coach_id  = int(r[0])
                coach_name = r[1]
                c.execute("INSERT INTO Coaches (CoachID, CoachName)VALUES(?,?);",
                          (coach_id, coach_name))


#CoachID + SportID 
def team_table():
    c.execute("DROP TABLE IF EXISTS Teams;")
    c.execute("""
    CREATE TABLE Teams(
        TeamID INTEGER PRIMARY KEY AUTOINCREMENT,
        TeamName TEXT NOT NULL,
        Coach INTEGER,
        Sport INTEGER,
        FOREIGN KEY(Coach) REFERENCES Coaches(CoachID),
        FOREIGN KEY(Sport) REFERENCES Sports(SportId)
    );
    """)


#Student
def member_table():
    c.execute("DROP TABLE IF EXISTS Members;")
    c.execute("""
    CREATE TABLE Members(
        TeamID INTEGER PRIMARY KEY AUTOINCREMENT,
        TeamName TEXT NOT NULL,
        Coach INTEGER,
        Sport INTEGER,
        FOREIGN KEY(Coach) REFERENCES Coaches(CoachID),
        FOREIGN KEY(Sport) REFERENCES Sports(SportId)
    );
    """)

def printing_student():
    for row in c.execute("SELECT * FROM STUDENTS"):
        print(row)


student_table()
sport_table()
coach_table()
team_table()
readin("SportTable")
readin("StudentTable")
readin("CoachTable")
printing_student()
print("IT RUNS GREAT ETHAN KEEP IT UP!")