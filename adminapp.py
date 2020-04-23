

#url for main page
@app.route('/adm')
def admmain():
	#render the page login.html in a folder called templates
	return render_template("admin/login.html")

#url for register
@app.route('/admregisteruser')
def admreg_user():
	#render the page register.html in a folder called templates
	return render_template("admin/register.html")
	

#url for register
@app.route('/admforgotpass')
def admforgot():
	#render the page register.html in a folder called templates
	return render_template("admin/forgot-password.html")
	
#get user results
def admuser_res(demail):
	
	userres=None
	presql = "SELECT * FROM es_results where email='%s'"%(demail)
	conncursor.execute(presql)
	userres = conncursor.fetchall()
	return userres
	
#url for register
@app.route('/admresults')
def admresults():

	admemail = session['email']
	
	userres = user_res(email)
	#render the page register.html in a folder called templates
	return render_template("admin/results.html",userres=userres)

#url for home
@app.route('/admhome/')
def admhome():
	 
	if 'email' in session:
		admemail = session['email']
		return render_template("admin/index.html")
	else:
		flash('Please login')
		return redirect(url_for('admmain'))
	
#url for 404
@app.errorhandler(404)
def admpage_not_found(e):
	return render_template("admin/404.html")
		
#url for 405
@app.errorhandler(405)
def admmethod_not_found(e):
	return render_template("admin/405.html")
		
#url for login which will be used on the login page as: action="/login" method ="post"
@app.route('/admlogin/', methods=['GET', 'POST'])
def admlogin_page():

	error = ''
	success = ''
	try:
		
		conncursor=conn.cursor(dictionary=True)
		if request.method == "POST":
			#declare the data posted in to variables attempted_username and attempted_password
			emailval = request.form['lemail']
			#depassval=request.form['lpassword']
			passval = encrypt_string(request.form['lpassword'])
			
			
			#patients
			psql="select * from patients where email='%s'"%(emailval)
			conncursor.execute(psql)
			pdata=conncursor.fetchone()
			cont = conncursor.rowcount
			
			if passval == pdata["password"]:
				#setting sessions
				session['logged_in'] = True
				session['email'] = emailval
				#redirecting to the homepage after login
				
				return redirect(url_for('home'))
				
			else:
				#show error and return to the login page
				error = "Invalid credentials. Try Again. "
			
				return render_template("admin/login.html", error = error)
			
		else:
			#show error and return to the login page
			error = "Error connecting to server."

			return render_template("admin/login.html", error = error)
				
	except Exception as e:
		#error to recieve info and return to the login page
		error=e
		return render_template("admin/login.html", error = error)
	
#url for entry form
@app.route('/admentry/')
def admentry():
	 
	if 'email' in session:
		admemail = session['email']
		return render_template("admin/symptoms.html")
	else:
		flash('Please login')
		return redirect(url_for('main'))

#url for logout
@app.route('/admlogout/')
def admlogout():
	#close the sessions
	session.pop('email', None)
	return redirect(url_for('main'))

#get user data
def admuser_def(demail):
	
	userprof=None
	prosql = "SELECT * FROM admin where email='%s'"%(demail)
	profcursor.execute(prosql)
	userprof = profcursor.fetchone()
	return userprof
			
#url for profile
@app.route('/admprofile/')
def admprofile():
	
	if 'email' in session:
		admemail = session['email']
		#demail='manzininin'
		userprof = user_def(email)
		
		return render_template("admin/profile.html", userprof=userprof)
	else:
		flash('Please login')
		return redirect(url_for('admmain'))
		
#edit user profile 
@app.route('/admchangeprof/', methods=['GET', 'POST'])
def admedit_profile():

	error = ''
	success = ''
	admemail = session['email']
	try:
		
		if request.method == "POST":
			#declare the data posted in to variables 
			emailvap = request.form['email']
			fnamevap = request.form['fname']
			lnamevap = request.form['lname']
			dobvap = request.form['dob']
			citvap = request.form['city']
			
			#patients
			usql="update patients set firstname=%s, lastname=%s, age=%s, city=%s where email=%s"
			valu=(fnamevap, lnamevap, dobvap, citvap, emailvap)
			conncursor.execute(usql, valu)
			conn.commit()
			
			contu = conncursor.rowcount
			
			if contu > 0:
				#flash message
				flash('Profile successfully updated.')
				
				return redirect(url_for('admprofile'))
				
			else:
				#show error 
				flash("Error updating profile.")
			
				return redirect(url_for('admprofile'))
			
		else:
			#show error and return to the login page
			flash("Error connecting to server.")

			return redirect(url_for('admprofile'))
				
	except Exception as e:
		#error to recieve info and return to the login page
		flash('Error connecting to server.')
		return redirect(url_for('admprofile'))

#viewing the results
@app.route('/admviewresult/<idres>')
def admviewresult(idres):
	
	if 'email' in session:
		admemail = session['email']
		
		try:
			
			val=idres
			if conn.is_connected():
				resuser=user_def(email)
				#patients
				psql="select * from es_results where id='%s'"%(val)
				conncursor.execute(psql)
				resultone=conncursor.fetchone()
			
				return render_template("viewresult.html", resultone=resultone, resuser=resuser)
				
		except Exception as e:
			#error to recieve info and return to the login page
			flash(str(e))
			return render_template("result.html")
		
	else:
		flash('Please login')
		return redirect(url_for('admmain'))	
		
		
#random number generation function
def admrando():
	
	rnd=random.randrange(10000,99999)
	return rnd

#registration	
@app.route('/admregister', methods=['GET', 'POST'])
def admregister():

	error = ''
	success = ''
	try:
	
		if request.method == "POST":
			#declare the data posted in to variables 
			emailvar = request.form['email']
			passvar = encrypt_string(request.form['password2'])
			fnamevar = request.form['fname']
			lnamevar = request.form['lname']
			cityvar = request.form['address']
			agevar = request.form['dob']
			if emailvar==0:
				error="Please fill all form fields."
				return
			else:
			
				num=rando()
				let = 'PCD'
				filenum=let+str(num)
				
				
				if conn.is_connected():
				
					x = conncursor.execute("SELECT * FROM admin WHERE email = 'emailval'")
					econt = conncursor.rowcount
					if econt > 0:
						flash("That email address is already in use.")
						return render_template('admin/login.html')

					else:
					
						#using random numbers and characters to make an id number
						sql="select employeeid from admin where employeeid='filenum'"
						conncursor.execute(sql)
						res=conncursor.fetchone()
					if res == None:
				
						filenum=filenum
				
					else:

						fileno=res["employeeid"]
						while fileno==filenum:
							#rerun the random function
							num=rando()
							let = 'PCD'
							filenum=let+str(num)
							return filenum
					insql="INSERT INTO admin(employeeid, email, password, firstname, lastname, age, address) VALUES(%s, %s, %s, %s, %s, %s, %s)"
					val=(filenum, emailvar, passvar, fnamevar, lnamevar, agevar, cityvar)
			
					conncursor.execute(insql, val)
					conn.commit()
					#count the rows inserted
					usercount=conncursor.rowcount
			
					if usercount > 0:
				
						success='Account created successfully. Now you can login.'
						#redirecting to the homepage after login
				
						return redirect(url_for('admmain', success = success))

					else:
						#show error and return to the login page
						error = "Error saving data."	
		except (KeyError, ZeroDivisionError , NameError) as e:
			#error to recieve info and return to the login page
			flash(str(e)+" .Error getting data")
		
			return redirect(url_for('admregister'))				


@app.route('/admrunengine/', methods=['GET', 'POST'])
def admes_engine():
	global output, age, o_psa, o_num_symp, o_bph, o_pts, agefact, pcd_treat, pcd_results
	#session.pop('res', None)
	error = ''
	success = ''
	
	try:
	
		if request.method == "POST":
			#declare the data posted in to variables
			
			engine = InreferenceEngine()
			engine.reset()
			
			
			emailr = session['email']
			agevar = request.form['age']
			symp1 = request.form['frequ']
			symp2 = request.form['semu']
			symp3 = request.form['painu']
			symp4 = request.form['blodu']
			symp5 = request.form['weaku']
			symp6 = request.form['peju']
			symp7 = request.form['inad']
			symp8 = request.form['ed']
			symp9 = request.form['painbo']
			symp10 = request.form['swell']
			varpsa = request.form['psa']
			
				 
			"""engine.declare(Patient(age=int(agevar),
					 freq_night_urination =bool(symp1),
					 bloody_semen =bool(symp2),
					 painful_urination =bool(symp3),
					 bloody_stool =bool(symp4),
					 weak_urine_flow =bool(symp5),
					 painful_eju =bool(symp6),						   
					 inad_erec =bool(symp7),
					 erectile_dysfunc =bool(symp8),
					 pain_in_bones =bool(symp9),
					 swelling_lower_limbs=bool(symp10), 
					 psa=varpsa))
					 
			engine.run()"""
			
			esoutput(agevar,symp1,symp2,symp3,symp4,symp5,symp6,symp7,symp8,symp9,symp10,varpsa)	
			
			fact_symps=["age ->"+str(agevar),
					 "freq_night_urination ->"+symp1,
					 "bloody_semen ->"+ symp2,
					 "painful_urination ->"+ symp3,
					 "bloody_stool ->"+ symp4,
					 "weak_urine_flow ->"+ symp5,
					 "painful_eju ->"+ symp6,   
					 "inad_erec ->"+ symp7,
					 "erectile_dysfunc ->"+ symp8,
					 "pain_in_bones ->"+ symp9,
					 "swelling_lower_limbs->"+ symp10, 
					 "psa ->"+varpsa]
			#storing the results
			pcd_results=(age+
			'\n '+agefact+'\n '+
			' About PSA level: \t '+o_psa+
			' About number of symptoms: 	\t\n\n '+o_num_symp+
			'\n \n  Overrally:	\t'+output)
			
			#pcd_results=session['res']
			#STORING THE TREATMENT SUGGESTIONS
			pcd_treatment=pcd_treat;
			#store the symtoms AND FACTS
			
				
			fact_array=str(fact_symps)
			fact_ara=pcd_results+output
			flash(fact_ara)
			
			# database
			if fact_array!=None:
				conncursor=conn.cursor(dictionary=True)
				#saving into database
				rinsql="INSERT INTO es_results(`email`, `results`, `symptoms`, `treatments`) VALUES(%s, %s, %s, %s)"
					
				val=(emailr, pcd_results, fact_array, pcd_treatment)
			
				conncursor.execute(rinsql, val)
				conn.commit()
				#count the rows inserted
				usercount=conncursor.rowcount
			
				if usercount > 0:
				
					success='All your symptoms have been processed.'
					#redirecting to the homepage after login
				
					return redirect(url_for('admresults', success=success, pcd_results=pcd_results))
					#return render_template('results.html', success=success, eng=eng)

				else:
					#show error and return to the login page
					flash("Error saving data.")

					return redirect(url_for('admentry'))
			else:
				flash("Error connecting to server")
				return redirect(url_for('admentry'))
				
		else:
			#show error and return to the login page
			flash("Error processing your symptoms")

			return redirect(url_for('admentry'))
				
	except Exception as e:
		#error to recieve info and return to the login page
		flash(str(e)+" .Error getting data")
		
		return redirect(url_for('admentry'))

