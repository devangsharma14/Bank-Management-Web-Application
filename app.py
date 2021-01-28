from datetime import datetime, date
from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///casestudy.sqlite3'
app.config['SECRET_KEY'] = "random string"


db=SQLAlchemy(app)


class Users(db.Model):
	id = db.Column('user_id', db.Integer, primary_key=True)
	username = db.Column(db.String(50))
	password = db.Column(db.String(50))	
	role = db.Column(db.Integer)


class Customer(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	customerssnid = db.Column(db.String(50))
	customer_id = db.Column(db.Integer, default=100000000)
	customername = db.Column(db.String(50))
	age = db.Column(db.String(50))
	address = db.Column(db.String(50))
	state = db.Column(db.String(50))
	city = db.Column(db.String(50))
	status=db.Column(db.String(50))
	message=db.Column(db.String(50))
	date=db.Column(db.String(50))


class Accounts(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	customer_id = db.Column(db.Integer)
	acc_id = db.Column(db.Integer, default=400000000)
	acc_type=db.Column(db.String(10))
	balance=db.Column(db.Integer)
	stat=db.Column(db.String(10))
	message=db.Column(db.String(50))
	date = db.Column(db.DateTime, default=datetime.now)


class Transactions(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	tran_id = db.Column(db.Integer, default=700000000)
	acc_id = db.Column(db.Integer)
	acc_type=db.Column(db.String(10))
	desc=db.Column(db.String(10))
	date = db.Column(db.Date, default= date.today)
	tran_amt = db.Column(db.Integer)
	curr_bal = db.Column(db.Integer)


@app.route("/")
def home(): 
	if 'username' in session:
		username=session['username']
		role=Users.query.filter_by(username=username).first().role
		if role==0:
			return render_template("HomeExc.html", username=username, role="Customer Executive")
		else:
			return render_template("HomeCash.html", username=username, role="Cashier")
	else:
		return redirect(url_for('login'))


@app.route("/login", methods=['GET', 'POST'])
def login():
	if request.method=='GET':
		return render_template("Login.html")
	else:
		username=request.form['username']
		password=request.form['password']
		checkCust=Users.query.filter_by(username=username, password=password).first()
		#print(check)
		if checkCust==None:
			flash("Incorrect Username or Password")
			return redirect(url_for('login'))
		else:
			session['username']=username
			return redirect(url_for('home'))


@app.route("/signup", methods=['GET', 'POST'])
def signup():
	if request.method=='GET':
		return render_template("SignUp.html")
	else:
		username=request.form['username']
		password=request.form['password']
		confpass=request.form['confpass']
		role=int(request.form['role'])
		currUsers=Users.query.all()
		for currUser in currUsers:
			if currUser.username == username:
				flash("This Username already exists. Please select some other Username.")
				return redirect(url_for('signup'))
		#print(currUsers)
		if password != confpass:
			flash('Password and Confirm Password do not Match')
			return render_template("SignUp.html")
		else:
			user = Users(username=username, password=password, role=role)
			db.session.add(user)
			db.session.commit()
			flash("User Account created successfully")
			return redirect(url_for('login'))


@app.route('/logout')
def logout():
	session.pop('username', None)
	return redirect(url_for('home'))


@app.route("/createcustomer", methods=['GET','POST'])
def customerid():
	if 'username' in session:
		role=Users.query.filter_by(username=session['username']).first().role
		if int(role) == 0:
			if request.method=='POST':
				customerssnid=request.form['customerssnid']
				customername=request.form['customername']
				age=request.form['age']
				address=request.form['address']
				state=request.form['state']
				city=request.form['city']
				date = datetime.now()
				fin=Customer.query.filter_by(customerssnid=customerssnid).first()
				if fin:
					s="Customer SSN ID: "+ customerssnid + " already exists."
					flash(s)
					return redirect(url_for("customerid"))
				u = Customer(customerssnid=customerssnid, customername=customername, age=age, address=address, state=state, city=city, status='Active',message='Customer Created Successfully',date=date )
				db.session.add(u)
				upd=Customer.query.filter_by(customerssnid=customerssnid).first()
				upd.customer_id=upd.customer_id + upd.id
				db.session.commit()
				y="Successfully Created with Customer ID: "+ str(upd.customer_id)
				flash(y)
				return render_template("create_customer.html")
			else:
				return render_template("create_customer.html")	
		else:
			return redirect(url_for('home'))
	else: 
		return redirect(url_for('login'))


@app.route("/customersearch", methods=['GET','POST'])
def customersearch():
	if 'username' in session:
		role=Users.query.filter_by(username=session['username']).first().role
		if int(role) == 0:
			if request.method=='GET':
				return render_template("customersearch.html")
			else:
				cus=request.form['customerssnid']	
				cid=request.form['customer_id']		

				if not cus and not cid:
					flash("Both fields are empty!!!")
					return redirect(url_for('customersearch'))

				elif not cus and cid:
					check=Customer.query.filter_by(customer_id=cid).first()

				elif cus and not cid:
					check=Customer.query.filter_by(customerssnid=cus).first()

				else:
					check=Customer.query.filter_by(customerssnid=cus, customer_id=cid).first()

				if check==None:
					flash("Incorrect ID")
					return redirect(url_for('customersearch'))
				else:
					return render_template("updatedel.html",customerssnid=check.customerssnid, customer_id=check.customer_id, customername=check.customername, age=check.age, address=check.address, state=check.state, city=check.city )
		else:
			return redirect(url_for('home'))
	else: 
		return redirect(url_for('login'))


@app.route("/updatecpage/<id>", methods=['GET','POST'])
def updatecpage(id):
	if 'username' in session:
		role=Users.query.filter_by(username=session['username']).first().role
		if int(role) == 0:
			if id.isdigit():
				check=Customer.query.filter_by(customerssnid=int(id)).first()
				if check:
					if request.method=='GET':
						#print(check)
						return render_template("update.html",customerssnid=check.customerssnid, customer_id=check.customer_id, customername=check.customername, age=check.age, address=check.address)
					else:	
						newname=request.form['newcustomername']
						newaddress=request.form['newaddress']
						newage=request.form['newage']	
						ch=Customer.query.filter_by(customerssnid=check.customerssnid).first()
						#print(ch.customername)
						#print(newname)
						ch.customername=newname
						ch.address=newaddress
						ch.age=newage
						ch.message='customer update complete'
						ch.date=datetime.now()
						db.session.commit()
						flash("Successfully updated")
						return redirect(url_for('customersearch'))
				else:
					return redirect('/page_not_found')
			else:
				return redirect('/page_not_found')
		else:
			return redirect(url_for('home'))
	else: 
		return redirect(url_for('login'))


@app.route("/deletecpage/<id>", methods=['GET','POST'])
def deletecpage(id):
	if 'username' in session:
		role=Users.query.filter_by(username=session['username']).first().role
		if int(role) == 0:
			if id.isdigit():
				check=Customer.query.filter_by(customerssnid=int(id)).first()
				if check:
					if request.method=='GET':
						return render_template("delete.html",customerssnid=check.customerssnid, customer_id=check.customer_id, customername=check.customername, age=check.age, address=check.address)
					else:
						ch=Customer.query.filter_by(customerssnid=check.customerssnid).first()
						db.session.delete(ch)
						db.session.commit()
						flash("Successfully Deleted")
						return redirect(url_for('customersearch'))
				else:
					return redirect('/page_not_found')
			else:
				return redirect('/page_not_found')
		else:
			return redirect(url_for('home'))
	else: 
		return redirect(url_for('login'))


@app.route("/cstatus",methods=['GET','POST'])
def cstatus():
	if 'username' in session:
		role=Users.query.filter_by(username=session['username']).first().role
		if int(role) == 0:
			if request.method=='GET':
				table=Customer.query.all()
				return render_template("cstatus.html",check=table)
		else:
			return redirect(url_for('home'))
	else: 
		return redirect(url_for('login'))


@app.route("/viewpage/<id>",methods=['GET','POST'])
def viewpage(id):
	if 'username' in session:
		role=Users.query.filter_by(username=session['username']).first().role
		if int(role) == 0:
			if request.method=='GET':
				c=Customer.query.filter_by(customerssnid=id).first()
				return render_template("viewpage.html",customerssnid=c.customerssnid, customer_id=c.customer_id, customername=c.customername, age=c.age, address=c.address, state=c.state, city=c.city)
		else:
			return redirect(url_for('home'))
	else: 
		return redirect(url_for('login'))


@app.route("/create_bank_acc", methods=['GET','POST'])
def bank_acc():
	if 'username' in session:
		role=Users.query.filter_by(username=session['username']).first().role
		if int(role) == 0:
			if request.method=='GET':
				return render_template("Create_bank_Account.html")
			else:
				customer_id = request.form['cus_id']
				acc_type=request.form['acc_type']
				balance=request.form['dep_amt']
				checkCust = Customer.query.filter_by(customer_id=customer_id).first()
				if checkCust:
					check = Accounts.query.filter_by(customer_id=customer_id, acc_type=acc_type).first()
					if not check:
						if int(balance)!=0:
							acc = Accounts(customer_id=customer_id, acc_type=acc_type, balance=int(balance), stat='Active', message='account creation complete')
							db.session.add(acc)
							upd=Accounts.query.filter_by(customer_id=customer_id, acc_type=acc_type).first()
							upd.acc_id=upd.acc_id + upd.id
							trans = Transactions(acc_id=upd.acc_id, acc_type=acc_type, desc='Deposit', tran_amt=int(balance), curr_bal=int(balance))
							db.session.add(trans)
							updTran=Transactions.query.filter_by(acc_id=upd.acc_id, acc_type=acc_type, desc='Deposit', tran_amt=int(balance), curr_bal=int(balance)).first()
							updTran.tran_id=updTran.tran_id + updTran.id
							db.session.commit()
							g="Accounts creation initiated successfully with Account ID: "+str(upd.acc_id)
							flash(g)
							return redirect(url_for('bank_acc'))
						flash("Deposit Amount cannot be 0")
						return redirect(url_for('bank_acc'))

					s="Customer already has "+ acc_type +" account with Account ID: "+str(check.acc_id)
					flash(s)
					return redirect(url_for('bank_acc'))

				o="Customer id: "+ customer_id +" does not exist. Please enter valid customer id."	
				flash(o)
				return redirect(url_for('bank_acc'))
		else:
			return redirect(url_for('home'))
	else: 
		return redirect(url_for('login'))			


@app.route('/search_acc', methods=['GET', 'POST'])
def search_acc():
	if 'username' in session:
		role=Users.query.filter_by(username=session['username']).first().role
		if request.method=='GET':
			return render_template("Search_acc.html")
		else:
			customer_id = request.form['cus_id']
			acc_id = request.form['acc_id']

			if not customer_id and not acc_id:
				flash("Both fields are empty!!!")
				return redirect(url_for('search_acc'))

			elif not customer_id and acc_id:
				currAccs = Accounts.query.filter_by(acc_id=acc_id).all()

			elif customer_id and not acc_id:
				currAccs = Accounts.query.filter_by(customer_id=customer_id).all()
			
			else: 
				currAccs = Accounts.query.filter_by(acc_id=acc_id, customer_id=customer_id).all()

			if currAccs:
				if int(role) == 0: 
					return render_template('Delete_acc.html',items=currAccs)
				return render_template('Account_details.html',items=currAccs)
			
			flash("Enter valid ID.")
			return redirect(url_for('search_acc'))
	else: 
		return redirect(url_for('login'))


@app.route('/del_acc/<id>',methods=['GET','POST'])
def del_acc(id):
	if 'username' in session:
		role=Users.query.filter_by(username=session['username']).first().role
		if int(role) == 0:
			if request.method=='GET':
				return render_template("Delete_acc.html")

			else:
				#print(request.form)
				customer_id = id
				acc_type = request.form['acc_id']
				ch=Accounts.query.filter_by(customer_id=customer_id,acc_type=acc_type).first()
				#print(ch)
				db.session.delete(ch)
				db.session.commit()
				flash("Account deletion initiated successfully.")
				return redirect(url_for('search_acc'))
		else:
			return redirect(url_for('home'))
	else: 
		return redirect(url_for('login'))


@app.route("/acc_status",methods=['GET','POST'])
def acc_status():
	if 'username' in session:
		role=Users.query.filter_by(username=session['username']).first().role
		if int(role) == 0:
			if request.method=='GET':
				table=Accounts.query.all()
				return render_template("Acc_status.html",table=table)
		else:
			return redirect(url_for('home'))
	else: 
		return redirect(url_for('login'))


@app.route('/deposit/',methods=['GET','POST'])
def deposit():
	if 'username' in session:
		role=Users.query.filter_by(username=session['username']).first().role
		if int(role) == 1:
			if request.method=='GET':
				keys=request.args.get('acc_id')
				if ',' in keys:
					if len(keys.split(','))==3:
						x = keys.split(',')
						cus_id = x[2]
						acc_type = x[0]
						currAccs = Accounts.query.filter_by(customer_id=int(cus_id),acc_type=acc_type).first()
						return render_template("Deposit.html",items=currAccs)
				return redirect('/page_not_found')
			else:
				acc_id = request.form['acc_id']
				dep_amt = request.form['dep_amt']

				ch=Accounts.query.filter_by(acc_id=acc_id).first()
				currTrans = Transactions.query.all()
				temp = ch.balance

				if dep_amt=="0":
					flash("Deposit amount cannot be 0.")
					magic = ch.acc_type +","+ str(temp) +","+ str(ch.customer_id)
					return redirect(url_for('deposit',acc_id=magic))
				else:	
					ch.balance = ch.balance + int(dep_amt)
					lt = len(currTrans)
					tran_id = 500000001
					tran_id += lt
					tran = Transactions(tran_id=tran_id,acc_id=ch.acc_id,acc_type=ch.acc_type,desc='Deposit',tran_amt=int(dep_amt),curr_bal=int(ch.balance))

					db.session.add(tran)
					db.session.commit()
					flash("Amount deposited successfully.")

					magic = ch.acc_type +","+ str(temp) +","+ str(ch.customer_id)
					return redirect(url_for('deposit',acc_id=magic))
		else:
			return redirect(url_for('home'))
	else: 
		return redirect(url_for('login'))


@app.route('/withdraw/',methods=['GET','POST'])
def withdraw():
	if 'username' in session:
		role=Users.query.filter_by(username=session['username']).first().role
		if int(role) == 1:
			if request.method=='GET':
				keys=request.args.get('acc_id')
				if ',' in keys:
					if len(keys.split(','))==3:
						x = keys.split(',')
						cus_id = x[2]
						acc_type = x[0]
						currAccs = Accounts.query.filter_by(customer_id=int(cus_id),acc_type=acc_type).first()
						return render_template("Withdraw.html",items=currAccs)
				return redirect('/page_not_found')
			else:
				acc_id = request.form['acc_id']
				wit_amt = request.form['wit_amt']

				ch=Accounts.query.filter_by(acc_id=acc_id).first()
				currTrans = Transactions.query.all()
				temp = ch.balance

				if int(wit_amt) > ch.balance:
					flash("Withdraw not allowed, please choose smaller amount.")
					magic = ch.acc_type +","+ str(temp) +","+ str(ch.customer_id)
					return redirect(url_for('withdraw',acc_id=magic))
				else:
					ch.balance = ch.balance - int(wit_amt)
					lt = len(currTrans)
					tran_id = 500000001
					tran_id += lt
					tran = Transactions(tran_id=tran_id,acc_id=ch.acc_id,acc_type=ch.acc_type,desc='Withdraw',tran_amt=int(wit_amt),curr_bal=int(ch.balance))

					db.session.add(tran)
					db.session.commit()
					flash("Amount withdrawn successfully.")

					magic = ch.acc_type +","+ str(temp) +","+ str(ch.customer_id)
					return redirect(url_for('withdraw',acc_id=magic))
		else:
			return redirect(url_for('home'))
	else: 
		return redirect(url_for('login'))


@app.route('/transfer/', methods=['GET','POST'])
def transfer():
	if 'username' in session:
		role=Users.query.filter_by(username=session['username']).first().role
		if int(role) == 1:
			if request.method=='GET':
				return render_template("transfer.html")
			else:
				cus_id=request.form['customerid']
				stype=request.form['sourceaccount']
				ttype=request.form['targetaccount']
				#print(stype)
				#print(ttype)
				transferamount=request.form['transferamount']
				source=Accounts.query.filter_by(customer_id=cus_id,acc_type=stype).first()
				target=Accounts.query.filter_by(customer_id=cus_id,acc_type=ttype).first()
				if source and target:
					if int(source.balance)-int(transferamount)<0:
						flash("Transfer not possible due to less funds in Source Account")
						return redirect(url_for("transfer"))
					target.balance=int(target.balance)+int(transferamount)
					source.balance=int(source.balance)-int(transferamount)
					said=source.acc_id
					taid=target.acc_id
					db.session.commit()
					trans=Transactions(acc_id=said,acc_type=source.acc_type,desc='Withdraw',tran_amt=int(transferamount),curr_bal=source.balance)
					db.session.add(trans)
					updid=Transactions.query.filter_by(acc_id=said,acc_type=source.acc_type,desc='Withdraw',tran_amt=int(transferamount),curr_bal=source.balance).first()
					updid.tran_id=updid.tran_id+updid.id
					db.session.commit()
					flash('Transfer Successfull')
					return redirect(url_for('transfer'))
				flash("Transfer Functionality not allowed for given Customer.")
				return redirect(url_for('search_acc'))
		else:
			return redirect(url_for('home'))
	else: 
		return redirect(url_for('login'))


@app.route('/statement11/', methods=['GET','POST'])
def statement11():
	if 'username' in session:
		role=Users.query.filter_by(username=session['username']).first().role
		if int(role) == 1:
			if request.method=='GET':
				return render_template("statement11.html")
			else:
				acc_id=request.form['acc_id']
				nooft=request.form['nooft']
				#print(acc_id)
				t=Transactions.query.filter_by(acc_id=int(acc_id)).all()
				if t:
					loop=min(int(nooft), len(t))
					return render_template("transferstatus.html",transfer=t,N=loop)
				flash("Wrong ID")
				return redirect(url_for("statement11"))
		else:
			return redirect(url_for('home'))
	else: 
		return redirect(url_for('login'))


@app.route('/statement2', methods=['GET','POST'])
def statement2():
	if 'username' in session:
		role=Users.query.filter_by(username=session['username']).first().role
		if int(role) == 1:
			if request.method=='GET':
				return render_template("statement2.html")
			else:
				acc_id=request.form['acc_id']
				sdate=request.form['sdate']
				edate=request.form['edate']
				#print(sdate)
				a=sdate.split('-')
				b=edate.split('-')
				d=Transactions.query.filter_by(acc_id=int(acc_id)).all()
				sdate=date(int(a[0]),int(a[1]),int(a[2]))
				edate=date(int(b[0]),int(b[1]),int(b[2]))
				#print(sdate)
				print(d[0].date)
				q=[]
				for i in d:
					if i.date>=sdate and i.date<=edate:
						q.append(i)

				return render_template("transferstatus.html",transfer=q,N=len(q))
		else:
			return redirect(url_for('home'))
	else: 
		return redirect(url_for('login'))


@app.errorhandler(404)
def page_not_found(error):
	return render_template("page_not_found.html"), 404


if __name__=="__main__":
	db.create_all()
	app.run(debug=True)

