# Student name: Chiyu He (Finn) ;   Student ID: 1147535  

from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
import psycopg2
import connect
import uuid



dbconn = None

app = Flask(__name__)

def getCursor():    
    global dbconn    
    if dbconn == None:
        conn = psycopg2.connect(dbname=connect.dbname, user=connect.dbuser, password=connect.dbpass, host=connect.dbhost, port=connect.dbport)
        dbconn = conn.cursor()  
        return dbconn
    else:
        return dbconn

def genID():
    return uuid.uuid4().fields[1]


@app.route("/")  # (home.html) this route is the action for home page and create a ViEW for using later.
def home():
    cur = getCursor()
    cur.execute("DROP VIEW IF EXISTS section1 CASCADE;")
    cur.execute("CREATE VIEW section1 AS SELECT member.MemberID, member.familyName, member.firstname, member.DateOfBirth, member.AdultLeader, groupmember.GroupID, groupmember.JoinedDate, groupmember.LeftDate FROM groupmember FULL OUTER JOIN member ON groupmember.MemberID = member.MemberID WHERE LeftDate is null; ")
    return render_template("home.html")

# The first part is for young people(no identification), that includes 3 routes and 4 html files. 
# It can allow young people find the group of a activity from activitynight and see the  potential 
  # attendees at an event (members of the group) and allow users to mark themselves present.

@app.route("/young/")  # (home.html-young.html)this route is the action for young people look for information about activity and ensure the group of activity, young people can find the member information of a group by clicking the corresponding groupid.
def young():
    cur = getCursor()
    cur.execute("select * from activitynight;")
    select_result = cur.fetchall()  
    column_names = [desc[0] for desc in cur.description]
    print(f"{column_names}")
    return render_template('young.html', dbresult=select_result, dbcols=column_names)


@app.route("/basical/") #(adult.html-activitynight2.html)this route is the action for adult look for information about activity and ensure the group of activity, adult can find the member information of a group by clicking the corresponding groupid. 
def basicinformation():
    cur = getCursor()
    cur.execute("select * from activitynight")
    select_result = cur.fetchall()  
    column_names = [desc[0] for desc in cur.description]
    return render_template('activitynight2.html',dbresult=select_result, dbcols=column_names)


@app.route("/activitynight/") #(adult.html-activitynight2.html)this route is the action for adult look for information about activity, adult can find the member information of a group by clicking the button "add more". 
def activityinformation():
    cur = getCursor()
    cur = getCursor()
    cur.execute("select * from activitynight")
    select_result = cur.fetchall()  
    column_names = [desc[0] for desc in cur.description]
    return render_template('activitynight3.html',dbresult=select_result, dbcols=column_names)


@app.route('/memberlist', methods = ['GET']) #(young.html-memberlist.html)this route is the action for young people look for the potential attendees at an event (members of the group).Young people can enter the attendancestatus-update page of some memeber by click the corresponding memberid.
def getMember():
    cur = getCursor()
    print(request.args)
    memberid = request.args.get('memberlist')
    print(memberid)
    cur = getCursor()
    cur.execute("DROP VIEW IF EXISTS CurrentGroupMember CASCADE;")
    cur.execute("CREATE VIEW CurrentGroupMember AS SELECT section1.MemberID, section1.familyName, section1.firstname, section1.DateOfBirth, section1.AdultLeader, section1.GroupID, section1.JoinedDate, section1.LeftDate, attendance.AttendanceStatus, attendance.Notes FROM attendance FULL OUTER JOIN section1 ON section1.MemberID = attendance.MemberID; ")
    cur.execute("select * from CurrentGroupMember where GroupID=%s",(memberid,))
    select_result = cur.fetchall()  
    column_names = [desc[0] for desc in cur.description]
    print(f"{column_names}")
    return render_template('memberlist.html',dbresult=select_result, dbcols=column_names)


@app.route('/memberlist2', methods = ['GET']) #(activitynight2.html-memberlist2.html)this route is the action for adult look for the potential attendees at an event (members of the group). Adult can enter the attendance-information-update page  of some member by clicking the button "add more".
def getMember2():
    cur = getCursor()
    print(request.args)
    memberid = request.args.get('memberlist2')
    print(memberid)
    cur = getCursor()
    cur.execute("DROP VIEW IF EXISTS section2 CASCADE;")
    cur.execute("CREATE VIEW section2 AS SELECT member.MemberID, member.familyName, member.firstname, member.DateOfBirth, member.AdultLeader, groupmember.GroupID, groupmember.JoinedDate, groupmember.LeftDate FROM groupmember FULL OUTER JOIN member ON groupmember.MemberID = member.MemberID; ")
    cur.execute("DROP VIEW IF EXISTS CurrentGroupMember2 CASCADE;")
    cur.execute("CREATE VIEW CurrentGroupMember2 AS SELECT section2.MemberID, section2.familyName, section2.firstname, section2.DateOfBirth, section2.AdultLeader, section2.GroupID, section2.JoinedDate, section2.LeftDate, attendance.AttendanceStatus, attendance.Notes FROM attendance FULL OUTER JOIN section2 ON section2.MemberID = attendance.MemberID; ")
    cur.execute("select * from CurrentGroupMember2 where GroupID=%s",(memberid,))
    select_result = cur.fetchall()  
    column_names = [desc[0] for desc in cur.description]
    print(f"{column_names}")
    return render_template('memberlist2.html',dbresult=select_result, dbcols=column_names)



@app.route('/statussituation/update', methods = ['GET','POST'])  #(form.html-memberlist.html)this route is the action for young people update their firstname and attendance.
def statusUpdate():
    if request.method == 'POST':
        memberid = request.form.get('memberid')
        firstname = request.form.get('firstname')
        attendancestatus = request.form.get('attendancestatus')
        cur = getCursor()
        cur.execute("UPDATE member SET firstname=%s where memberid=%s", (firstname,str(memberid),))
        cur.execute("UPDATE attendance SET attendancestatus = %s where memberid = %s", (attendancestatus,str(memberid),))
        cur.execute("DROP VIEW IF EXISTS CurrentGroupMember CASCADE;")
        cur.execute("CREATE VIEW CurrentGroupMember AS SELECT section1.MemberID, section1.familyName, section1.firstname, section1.DateOfBirth, section1.AdultLeader, section1.GroupID, section1.JoinedDate, section1.LeftDate, attendance.AttendanceStatus, attendance.Notes FROM attendance FULL OUTER JOIN section1 ON section1.MemberID = attendance.MemberID; ")
        cur.execute("select * from CurrentGroupMember where memberid=%s",(memberid,))
        select_result = cur.fetchall()  
        column_names = [desc[0] for desc in cur.description]
        print(f"{column_names}")
        return render_template('memberlist.html',dbresult=select_result, dbcols=column_names)
    else:
        id = request.args.get('memberid')
        if id =='':
            return redirect("/")
        else:
            cur = getCursor()
            cur.execute("DROP VIEW IF EXISTS CurrentGroupMember CASCADE;")
            cur.execute("CREATE VIEW CurrentGroupMember AS SELECT section1.MemberID, section1.familyName, section1.firstname, section1.DateOfBirth, section1.AdultLeader, section1.GroupID, section1.JoinedDate, section1.LeftDate, attendance.AttendanceStatus, attendance.Notes FROM attendance FULL OUTER JOIN section1 ON section1.MemberID = attendance.MemberID; ")
            cur.execute("SELECT * FROM CurrentGroupMember where memberid = %s", (str(id),))
            select_result = cur.fetchall()  # fetchall()  can return mutiple tuples; fetchone() just return one tuple, the result of them is a list.
            print(select_result)
            return render_template('form.html', memberdetails = select_result)


@app.route('/statussituation2/update2', methods = ['GET','POST'])#(form2.html-memberlist2.html)this route is the action for adult update their attendance information (includ update the leftdate)
def statusUpdate2():
    if request.method == 'POST':
        memberid = request.form.get('memberid')
        firstname = request.form.get('firstname')
        attendancestatus = request.form.get('attendancestatus')
        leftdate = request.form.get('leftdate')
        notes = request.form.get('notes')
        
        if firstname != "":
            cur = getCursor()
            cur.execute("UPDATE member SET firstname=%s where memberid=%s", (firstname,str(memberid),))
        if leftdate != "":
            cur = getCursor()
            cur.execute("UPDATE groupmember SET leftdate=%s where memberid=%s", (leftdate,str(memberid),))
        if attendancestatus != "":
            cur = getCursor()
            cur.execute("UPDATE attendance SET attendancestatus=%s where memberid = %s", (attendancestatus,str(memberid),))
        if notes != "":
            cur = getCursor()
            cur.execute("UPDATE attendance SET notes=%s where memberid = %s", (notes,str(memberid),))
        
        cur = getCursor()
        cur.execute("DROP VIEW IF EXISTS section2 CASCADE;")
        cur.execute("CREATE VIEW section2 AS SELECT member.MemberID, member.familyName, member.firstname, member.DateOfBirth, member.AdultLeader, groupmember.GroupID, groupmember.JoinedDate, groupmember.LeftDate FROM groupmember FULL OUTER JOIN member ON groupmember.MemberID = member.MemberID; ")
        cur.execute("DROP VIEW IF EXISTS CurrentGroupMember2 CASCADE;")
        cur.execute("CREATE VIEW CurrentGroupMember2 AS SELECT section2.MemberID, section2.familyName, section2.firstname, section2.DateOfBirth, section2.AdultLeader, section2.GroupID, section2.JoinedDate, section2.LeftDate, attendance.AttendanceStatus, attendance.Notes FROM attendance FULL OUTER JOIN section2 ON section2.MemberID = attendance.MemberID; ")
        cur.execute("select * from CurrentGroupMember2 where memberid=%s",(memberid,))
        select_result = cur.fetchall()  
        column_names = [desc[0] for desc in cur.description]
        print(f"{column_names}")
        return render_template('memberlist2.html',dbresult=select_result, dbcols=column_names)
    else:
        id = request.args.get('memberid')
        if id =='':
            return redirect("/")
        else:
            cur = getCursor()
            cur.execute("DROP VIEW IF EXISTS section2 CASCADE;")
            cur.execute("CREATE VIEW section2 AS SELECT member.MemberID, member.familyName, member.firstname, member.DateOfBirth, member.AdultLeader, groupmember.GroupID, groupmember.JoinedDate, groupmember.LeftDate FROM groupmember FULL OUTER JOIN member ON groupmember.MemberID = member.MemberID; ")
            cur.execute("DROP VIEW IF EXISTS CurrentGroupMember2 CASCADE;")
            cur.execute("CREATE VIEW CurrentGroupMember2 AS SELECT section2.MemberID, section2.familyName, section2.firstname, section2.DateOfBirth, section2.AdultLeader, section2.GroupID, section2.JoinedDate, section2.LeftDate, attendance.AttendanceStatus, attendance.Notes FROM attendance FULL OUTER JOIN section2 ON section2.MemberID = attendance.MemberID; ")
            cur.execute("SELECT * FROM CurrentGroupMember2 where memberid = %s", (str(id),))
            select_result = cur.fetchall()  # fetchall()  can return mutiple tuples( rows ); fetchone just return one tuple( row )
            print(select_result)
            return render_template('form2.html', memberdetails = select_result)


@app.route('/addstatus', methods = ['GET','POST']) #(form3.html-memberlist2.html)this route is the action for adult add new member information (includ add the leftdate)
def addstatus():
    if request.method == 'POST':
        print(request.form)
        id = genID()
        print(id)
        firstname = request.form.get('firstname')
        groupid = request.form.get('groupid')
        leftdate = request.form.get('leftdate')
        attendancestatus = request.form.get('attendancestatus')
        notes = request.form.get('notes')
        
        if firstname !="":
            cur = getCursor()
            cur.execute("INSERT INTO member(memberid, firstname) VALUES (%s,%s);", (str(id), firstname, ))
        if groupid != "" and leftdate == "":
            cur = getCursor()
            cur.execute("INSERT INTO groupmember(memberid, groupid) VALUES (%s,%s);", (str(id), groupid, ))
        if groupid == "" and leftdate != "":
            cur = getCursor()
            cur.execute("INSERT INTO groupmember(memberid, leftdate) VALUES (%s,%s);", (str(id), leftdate, )) 
        if groupid != "" and leftdate != "":
            cur = getCursor()
            cur.execute("INSERT INTO groupmember(memberid, groupid,leftdate) VALUES (%s,%s,%s);", (str(id), groupid,leftdate, ))
        if attendancestatus != "" and notes == "":
            cur = getCursor()
            cur.execute("INSERT INTO attendance(memberid, attendancestatus) VALUES (%s,%s);", (str(id), attendancestatus, ))
        if attendancestatus == "" and notes != "":
            cur = getCursor()
            cur.execute("INSERT INTO attendance(memberid, notes) VALUES (%s,%s);", (str(id), notes, )) 
        if attendancestatus != "" and notes != "":
            cur = getCursor()
            cur.execute("INSERT INTO attendance(memberid, attendancestatus,notes) VALUES (%s,%s,%s);", (str(id), attendancestatus,notes, ))
        
        cur = getCursor()
        cur.execute("DROP VIEW IF EXISTS section2 CASCADE;")
        cur.execute("CREATE VIEW section2 AS SELECT member.MemberID, member.familyName, member.firstname, member.DateOfBirth, member.AdultLeader, groupmember.GroupID, groupmember.JoinedDate, groupmember.LeftDate FROM groupmember FULL OUTER JOIN member ON groupmember.MemberID = member.MemberID; ")
        cur.execute("DROP VIEW IF EXISTS CurrentGroupMember2 CASCADE;")
        cur.execute("CREATE VIEW CurrentGroupMember2 AS SELECT section2.MemberID, section2.familyName, section2.firstname, section2.DateOfBirth, section2.AdultLeader, section2.GroupID, section2.JoinedDate, section2.LeftDate, attendance.AttendanceStatus, attendance.Notes FROM attendance FULL OUTER JOIN section2 ON section2.MemberID = attendance.MemberID; ")
        cur.execute("SELECT * FROM CurrentGroupMember2 where memberid = %s", (str(id),))
        select_result = cur.fetchall()  # fetchall()  can return mutiple tuples( rows ); fetchone just return one tuple( row )
        column_names = [desc[0] for desc in cur.description]
        return render_template('memberlist2.html', dbresult=select_result, dbcols=column_names, )
    else:
        return render_template('form3.html')


@app.route('/addactivity', methods = ['GET','POST']) #(form4.html-activitynight3.html)this route is the action for adult add new activity information (includ add the leftdate)
def addactivity():
    if request.method == 'POST':
        print(request.form)
        id = genID()
        print(id)
        groupid = request.form.get('groupid')
        nighttitle = request.form.get('nighttitle')
        description = request.form.get('description')
        activitynightdate = request.form.get('activitynightdate')
        #situation 1
        if groupid != "" and nighttitle == "" and description == "" and activitynightdate == "":
            cur = getCursor()
            cur.execute("INSERT INTO activitynight(activitynightid, groupid) VALUES (%s,%s);", (str(id), groupid,))
        #situation 2
        if groupid == "" and nighttitle != "" and description == "" and activitynightdate == "":
            cur = getCursor()
            cur.execute("INSERT INTO activitynight(activitynightid, nighttitle) VALUES (%s,%s);", (str(id), nighttitle,))
        #situation 3
        if groupid == "" and nighttitle == "" and description != "" and activitynightdate == "":
            cur = getCursor()
            cur.execute("INSERT INTO activitynight(activitynightid, description) VALUES (%s,%s);", (str(id), description,))
        #situation 4
        if groupid == "" and nighttitle == "" and description == "" and activitynightdate != "":
            cur = getCursor()
            cur.execute("INSERT INTO activitynight(activitynightid, activitynightdate) VALUES (%s,%s);", (str(id), activitynightdate,))
        #situation 5
        if groupid != "" and nighttitle != "" and description == "" and activitynightdate == "":
            cur = getCursor()
            cur.execute("INSERT INTO activitynight(activitynightid, groupid, nighttitle) VALUES (%s,%s,%s);", (str(id), groupid, nighttitle,))
        #situation 6
        if groupid != "" and nighttitle == "" and description != "" and activitynightdate == "":
            cur = getCursor()
            cur.execute("INSERT INTO activitynight(activitynightid, groupid, description) VALUES (%s,%s,%s);", (str(id), groupid, description,))
        #situation 7
        if groupid != "" and nighttitle == "" and description == "" and activitynightdate != "":
            cur = getCursor()
            cur.execute("INSERT INTO activitynight(activitynightid, groupid, activitynightdate) VALUES (%s,%s,%s);", (str(id), groupid, activitynightdate,))
        #situation 8
        if groupid == "" and nighttitle != "" and description != "" and activitynightdate == "":
            cur = getCursor()
            cur.execute("INSERT INTO activitynight(activitynightid, nighttitle, description) VALUES (%s,%s,%s);", (str(id), nighttitle, description,))
        #situation 9
        if groupid == "" and nighttitle != "" and description == "" and activitynightdate != "":
            cur = getCursor()
            cur.execute("INSERT INTO activitynight(activitynightid, nighttitle, activitynightdate) VALUES (%s,%s,%s);", (str(id), nighttitle, activitynightdate,))
        #situation 10
        if groupid == "" and nighttitle == "" and description != "" and activitynightdate != "":
            cur = getCursor()
            cur.execute("INSERT INTO activitynight(activitynightid, description, activitynightdate) VALUES (%s,%s,%s);", (str(id), description, activitynightdate,))
        #situation 11
        if groupid != "" and nighttitle != "" and description != "" and activitynightdate == "":
            cur = getCursor()
            cur.execute("INSERT INTO activitynight(activitynightid, groupid, nighttitle, description) VALUES (%s,%s,%s,%s);", (str(id), groupid, nighttitle, description,))
        #situation 12
        if groupid != "" and nighttitle == "" and description != "" and activitynightdate != "":
            cur = getCursor()
            cur.execute("INSERT INTO activitynight(activitynightid, groupid, description, activitynightdate) VALUES (%s,%s,%s,%s);", (str(id), groupid, description, activitynightdate,))
        #situation 13
        if groupid != "" and nighttitle != "" and description == "" and activitynightdate != "":
            cur = getCursor()
            cur.execute("INSERT INTO activitynight(activitynightid, groupid, nighttitle, activitynightdate) VALUES (%s,%s,%s,%s);", (str(id), groupid, nighttitle, activitynightdate,))
        #situation 14
        if groupid == "" and nighttitle != "" and description != "" and activitynightdate != "":
            cur = getCursor()
            cur.execute("INSERT INTO activitynight(activitynightid, nighttitle, description, activitynightdate) VALUES (%s,%s,%s,%s);", (str(id), nighttitle, description, activitynightdate,))
        #situation 15
        if groupid != "" and nighttitle != "" and description != "" and activitynightdate != "":
            cur = getCursor()
            cur.execute("INSERT INTO activitynight(activitynightid, groupid, nighttitle, description, activitynightdate) VALUES (%s,%s,%s,%s,%s);", (str(id), groupid, nighttitle, description, activitynightdate,))
        
        cur = getCursor()
        cur.execute("SELECT * FROM activitynight where activitynightid = %s", (str(id),))
        select_result = cur.fetchall()  # fetchall()  can return mutiple tuples( rows ); fetchone just return one tuple( row )
        column_names = [desc[0] for desc in cur.description]
        return render_template('activitynight3.html', dbresult=select_result, dbcols=column_names, )
    else:
        return render_template('form4.html')


@app.route("/identification/") #(home.html-identification.html)this route is the action for adult insert their identification information.
def identify():
    return render_template('identification.html')


@app.route("/adult", methods = ['GET','POST']) #(home.html-identification.html-adult.html)this route is the action for adult check who they are. If the memberid can match their firstname,they can enter the information editor page, else just return home page.
def adult():
    if request.method == 'POST':
        checkid = request.form.get('memberid')
        print(checkid)
        checkname = request.form.get('firstname')
        print(checkname)
        cur = getCursor()
        cur.execute("SELECT firstname FROM member where memberid=%s;",(int(checkid),))
        select_result = cur.fetchone()
        orginalname = select_result[0]
        print (orginalname)
        if  orginalname == checkname:
            return render_template('adult.html')
        else:
            return render_template('home.html')


