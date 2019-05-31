import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

DATABASE_URL="postgres://eaggqrlwacukhg:1da400a2b48765cf5616b5284e3a833c1b6db80ffdc80a9d1cc9233d4e00a2c7@ec2-107-20-230-70.compute-1.amazonaws.com:5432/d1immff20judvu"
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    with open("books.csv") as f:
	    reader = csv.reader(f)
	    for isbn, title, author, year in reader:
	        db.execute("INSERT INTO books (isbn, title, author,year) VALUES (:isbn, :title, :author, :year)",
	                    {"isbn": isbn, "title": title, "author": author, "year": year})
	        print(f"Added book isbn: {isbn} title: {title} author:  {author} year: {year}")
	db.commit()

if __name__ == "__main__":
    main()
