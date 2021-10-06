import app

@app.route('/applyforleave', methods=['GET', 'POST'])
def applyForLeave():
    leave_mssg = None
    if 'facultyId' in session:
        not_access_to_leave = ['director']
        if session['role'] in not_access_to_leave:
            return redirect(url_for('home'))

            
        if request.method == 'POST':
            # get remaining leave for this faculty
            cursor.execute("SELECT * from remaining_leave r where r.faculty_id = %s;",
                [session['facultyId']]);
            remainingLeave = cursor.fetchone()[1]

            endDate = datetime.datetime.strptime(request.form['enddate'], '%Y-%m-%d').date()
            startDate = datetime.datetime.strptime(request.form['startdate'], '%Y-%m-%d').date()

            if endDate < startDate:
                return render_template('apply_leave.html', role=session['role'],
                                leave_mssg="end date cannot be lower than start date",  show_form= 1)

            requestedLeave = endDate - startDate
            requestedLeave = requestedLeave.days +1

            allowedLeave = min(requestedLeave, remainingLeave);

            endDate = startDate + datetime.timedelta(days = allowedLeave-1)

            today = datetime.date.today()
            type = 'n'
            if startDate <= today:
                type = 'r'

            #return render_template('apply_leave.html', role=session['role'],
            #leave_mssg="" + str(requestedLeave) + "---" + str(endDate) + " -- " + type,  show_form= 1)
            
            try:
                cursor.execute("INSERT INTO leave_application(faculty_id, subject, description, start_date\
                    , end_date, type) VALUES (%s, %s, %s, %s, %s, %s)", (session['facultyId'],
                        request.form['subject'], request.form['description'], startDate,
                        endDate, type));
                conn.commit();
            except Exception as e:
                conn.rollback();
                return render_template('apply_leave.html', role=session['role'],
                                leave_mssg=e,  show_form= 1)

            return render_template('apply_leave.html', role=session['role'],
                                leave_mssg="successfully applied for leave",  show_form= 0)

            

        # check if this faculty's leave application is already in process
        # or if he has currently ongoing vacation
        today = datetime.date.today()
        show_form = 1
        
        cursor.execute("select * from check_for_ongoing_leave_application(%s);",
            [session['facultyId']]);
        show_form = cursor.fetchone()[0];

        
        if show_form == 1:
            show_form = 0
        else:
            show_form = 1

        if show_form == 0:
            leave_mssg = 'You have already applied for leave or You have ongoing vacation.'
            return render_template('apply_leave.html', role=session['role'],
            leave_mssg=leave_mssg,  show_form=show_form )
        else:
            return render_template('apply_leave.html', role=session['role'],
            leave_mssg=leave_mssg,  show_form=show_form )

    else:
        return redirect(url_for('login_page'))