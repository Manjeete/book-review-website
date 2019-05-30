import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

DATABASE_URL="postgres://cdmekxoqflindy:23bb78e306e10865549be635b880e628373d2016e617e3f660483bbfcf5c222d@ec2-54-83-50-174.compute-1.amazonaws.com:5432/ddm76rg8a80b6j"
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
