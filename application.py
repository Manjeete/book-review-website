import os
from flask import Flask, session, render_template, request, url_for,redirect,flash
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app=Flask(__name__)
DATABASE_URL="postgres://eaggqrlwacukhg:1da400a2b48765cf5616b5284e3a833c1b6db80ffdc80a9d1cc9233d4e00a2c7@ec2-107-20-230-70.compute-1.amazonaws.com:5432/d1immff20judvu"

# # Check for environment variable
# if not os.getenv(DATABASE_URL):
#     raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

@app.route('/',methods=["POST","GET"])
def index():
	return render_template("register.html")

@app.route('/register',methods=["POST"])
def register():
	name=request.form.get("name")
	username=request.form.get("username")
	email=request.form.get("email")
	password=request.form.get("password")
	check_email = db.execute("SELECT * FROM user_info WHERE email= :email",{"email":email}).fetchone()
	check_password = db.execute("SELECT * FROM user_info WHERE password= :password",{"password":password}).fetchone()
	if check_email or check_password is None:
		db.execute("INSERT INTO user_info(name,username,email,password) VALUES(:name,:username,:email,:password)",
			{"name":name,"username":username,"email":email,"password":password})
		db.commit()
		db.close()
		return render_template("register.html")
	else:
		return "Sorry!! Email or Password is already taken!"

@app.route('/login',methods=["POST","GET"])
def login():
	return render_template("login.html")

@app.route('/vlogin',methods=["post"])
def vlogin():
	email=request.form.get("email")
	password=request.form.get("password")
	query=db.execute("SELECT * FROM user_info WHERE email=:email AND password=:password",
	{"email":email,"password":password}).fetchall()
	for q in query:
		if q.email==email and q.password==password:
			session['logged_in'] = True
			session['username'] = q.username
			return render_template("search.html", username=session['username'])			
	return redirect("login")

@app.route('/search', methods=["POST"])
def search():
	search=request.form.get("search")
	result=db.execute("SELECT * FROM books WHERE isbn=:search OR author=:search OR title=:search",
	{"search":search}).fetchall()
	print(search)
	if result == []:
		return "Not found"
	return render_template("results.html",result=result)


@app.route('/details/<int:book_id>')
def details(book_id):
	b_result=db.execute("SELECT * FROM books WHERE id=:book_id",
	{"book_id":book_id}).fetchall()
	if b_result is None:
		return "No book exist"
	import requests
	for q in b_result:
		#  we are using try and except to handle exception
		# getting 400 response from API this is why we are using exception handling
		try:
			res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "rp90sQyZaFEGipR2Qd5rvw", "isbns": q.isbn})
			total_r=res.json()['books'][0]['work_ratings_count']
			avg_r=res.json()['books'][0]['average_rating']
		except:
			total_r="Not available"
			avg_r="Not available"
		reviews =db.execute("SELECT * FROM user_reviews WHERE book_id=:book_id",
		{"book_id":book_id}).fetchall()
	return render_template("details.html",username=session['username'],reviews=reviews,b_result=b_result,total_r=total_r,avg_r=avg_r)


@app.route('/user_reviews/<int:book_id>', methods=["POST"])
def user_reviews(book_id):
	review = request.form.get("review")
	rating = request.form.get("rating")
	user = request.form.get("username")
	# user review validation
	valid_review = db.execute("SELECT * FROM user_reviews WHERE r_user=:user AND book_id=:book_id",{"user":user,"book_id":book_id}).fetchall()
	# here we are checking whether valid_review is a truthy value or falsy value
	if valid_review:
		# showing this message to front end by using flash faction
		flash("Already reviewed!!")
		return redirect(url_for('details',book_id=book_id))
	db.execute("INSERT INTO user_reviews(review,rating,book_id,r_user) VALUES(:review,:rating,:book_id,:user);", 
		{"review":review,"rating":rating,"book_id":book_id,"user":user})
	db.commit()
	db.close()
	return redirect(url_for('details',book_id=book_id))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__=='__main__'	:
	app.run(debug=True)
