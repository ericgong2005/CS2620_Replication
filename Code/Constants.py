'''
This file contains constants used by the GRPC Database Manager
'''

from pathlib import Path

DATABASE_DIRECTORY = Path(__file__).parent / "Databases"
PASSWORD_DATABASE = Path(__file__).parent / "Databases/Database_test/passwords.db"
MESSAGES_DATABASE = Path(__file__).parent / "Databases/Database_test/messages.db"
PASSWORD_DATABASE_SCHEMA = "Passwords (Username TEXT PRIMARY KEY, Password TEXT NOT NULL)"
MESSAGES_DATABASE_SCHEMA = ("Messages (Id INTEGER PRIMARY KEY AUTOINCREMENT, Sender TEXT NOT NULL, " +
                            "Recipient TEXT NOT NULL, Time_sent TEXT NOT NULL, Read BOOLEAN NOT NULL DEFAULT 0, " + 
                            "Subject TEXT, Body TEXT)")