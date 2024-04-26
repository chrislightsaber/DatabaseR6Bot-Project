import sqlite3


conn = sqlite3.connect('r6s_stats.db')
cursor = conn.cursor()

#Create the Player table
cursor.execute('''
CREATE TABLE IF NOT EXISTS Player (
    Username TEXT PRIMARY KEY,
    KD_Ratio REAL,
    Ranked_Points INTEGER,
    KOST REAL,
    Ranked_Win_Percent REAL,
    Games_Played INTEGER
)''')

#Create the Map table
cursor.execute('''
CREATE TABLE IF NOT EXISTS Map (
    MapName TEXT PRIMARY KEY,
)''')

#Create the Operator table
cursor.execute('''
CREATE TABLE IF NOT EXISTS Operator (
    OpName TEXT PRIMARY KEY
)''')

#Create the PlayerMap associative table
cursor.execute('''
CREATE TABLE IF NOT EXISTS PlayerMap (
    Username TEXT,
    MapName TEXT,
    Win_Percent REAL,
    Matches_Played INTEGER,
    PRIMARY KEY (Username, MapName),
    FOREIGN KEY (Username) REFERENCES Player(Username),
    FOREIGN KEY (MapName) REFERENCES Map(MapName)
)''')

# Create the PlayerOperator associative table
cursor.execute('''
CREATE TABLE IF NOT EXISTS PlayerOperator (
    Username TEXT,
    OpName TEXT,
    KD_Ratio REAL,
    Role TEXT,
    KOST REAL,
    Round_Win_Percent REAL,
    Rounds_Played INTEGER,
    PRIMARY KEY (Username, OpName),
    FOREIGN KEY (Username) REFERENCES Player(Username),
    FOREIGN KEY (OpName) REFERENCES Operator(OpName)
)''')

#Commit the changes
conn.commit()

#Close the database connection
conn.close()
