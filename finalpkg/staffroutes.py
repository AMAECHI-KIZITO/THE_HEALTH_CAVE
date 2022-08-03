import re,os,random
from datetime import datetime,date
from flask import Flask,render_template,abort,request,make_response,redirect,flash,session,send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func
from finalpkg import thc,db,csrf
from finalpkg.thc_models import *


#### DASHBOARDS
@thc.route('/doctor_dashboard/')
def doctor():
    if session.get('staff_no')!=None and session.get('staff_id')!=None and session.get('staff_name')!=None and session.get('staff_hospid')!=None:
        
        doc_appts=db.session.query(Appointment).filter(Appointment.apt_staff_id==session.get('staff_id'),func.date(Appointment.date_of_appt)==date.today()).all()
        
        doc_msgs=db.session.query(Messages).filter(Messages.receiver_staff_id==session.get('staff_id')).order_by(Messages.msg_id.desc()).all()
        
        
        staffinfo=db.session.query(Staff).filter(Staff.staff_id==session.get('staff_id')).all()
        
        doc_surgery=db.session.query(Surgery).filter(Surgery.lead_surgeon_staff_id==session.get('staff_id'),func.date(Surgery.date_of_surg)==date.today()).all()
        
        
        return render_template('staff/doctordashboard.html',docapt=doc_appts,inbox=doc_msgs,staffinfo=staffinfo,doc_surgery=doc_surgery)
    else:
        return redirect('/login/')

@thc.route('/nurse_dashboard/')
def nurse():
    if session.get('staff_no')!=None and session.get('staff_id')!=None and session.get('staff_name')!=None and session.get('staff_hospid')!=None:
        staffinfo=db.session.query(Staff).filter(Staff.staff_id==session.get('staff_id')).all()
        
        day_appts=db.session.query(Appointment).filter(Appointment.apt_hosp_id==session.get('staff_hospid'),func.date(Appointment.date_of_appt)==date.today()).all()
        
        todaysurgery=db.session.query(Surgery).filter(Surgery.surg_hosp_id==session.get('staff_hospid'),func.date(Surgery.date_of_surg)==date.today()).all()
        
        return render_template('staff/nursedashboard.html',appt=day_appts,staffinfo=staffinfo,todaysurgery=todaysurgery)
    else:
        return redirect('/login/')



####FIND OTHER HOSPITAL STAFF
@thc.route('/findstaff/')
def find_staff():
    if session.get('staff_no')!=None and session.get('staff_id')!=None and session.get('staff_name')!=None and session.get('staff_hospid')!=None:
        staffinfo=db.session.query(Staff).filter(Staff.staff_id==session.get('staff_id')).all()
        return render_template('staff/staff_find.html',staffinfo=staffinfo)
    else:
        return redirect('/login/')

# @thc.route('/searchingstaff/')
# def dynamicstaffsearch():
#     selected=request.args.get('input')
#     result=db.session.query(Staff).filter((Staff.staff_number==selected)|(Staff.fname==selected)|(Staff.lname==selected)).all()
    
#     for x in result:
#         results=f"{x.fname}"
        
#     return results


@thc.route('/search_bystaff/',methods=['POST'])
def staf_search_staff():
    if session.get('staff_no')!=None and session.get('staff_id')!=None and session.get('staff_name')!=None and session.get('staff_hospid')!=None:
        staffinfo=db.session.query(Staff).filter(Staff.staff_id==session.get('staff_id')).all() #for personalization
        
        lookfor=request.form.get('staffno')
        find=db.session.query(Staff).filter((Staff.staff_number==lookfor)|(Staff.fname==lookfor)|(Staff.lname==lookfor)|(Staff.othername==lookfor)).all()
        if find:
            return render_template('staff/search_bystaffresult.html',find=find,staffinfo=staffinfo)
        
        else:
            flash('No record match', category='no_staff_found')
            return render_template('staff/search_bystaffresult.html',staffinfo=staffinfo)
    else:
        return redirect('/login/')
    
 
 
    
####FIND OTHER HOSPITAL PATIENT
@thc.route('/findpatient/')
def find_patient():
    if session.get('staff_no')!=None and session.get('staff_id')!=None and session.get('staff_name')!=None and session.get('staff_hospid')!=None:
        staffinfo=db.session.query(Staff).filter(Staff.staff_id==session.get('staff_id')).all()
        return render_template('staff/findCHTpatient.html',staffinfo=staffinfo)
    else:
        return redirect('/login/')
    
####FIND OTHER HOSPITAL PATIENTS RESULT
@thc.route('/searchpatient/',methods=['POST'])
def staff_search_patient():
    staffinfo=db.session.query(Staff).filter(Staff.staff_id==session.get('staff_id')).all()
    if session.get('staff_no')!=None and session.get('staff_id')!=None and session.get('staff_name')!=None and session.get('staff_hospid')!=None:
        patientfinder=request.form.get('patient_no')
        thepatientnum=re.sub('/','-',patientfinder)
        find=db.session.query(Patient).filter(Patient.patient_number==thepatientnum).all()
        if find:
            return render_template('staff/searchpatientresult.html',find=find,staffinfo=staffinfo)
        else:
            flash('Patient Not Found', category='no_patient_found')
            return render_template('staff/searchpatientresult.html',staffinfo=staffinfo)
    else:
        return redirect('/login/')
 
 
 
#### DOCTOR STAFF CHANGE PASSWORD
@thc.route('/changepassword/')
def staff_changepswd():
    if session.get('staff_no')!=None and session.get('staff_id')!=None and session.get('staff_name')!=None and session.get('staff_hospid')!=None:
        staffinfo=db.session.query(Staff).filter(Staff.staff_id==session.get('staff_id')).all()
        return render_template('staff/changepassword.html',staffinfo=staffinfo)
    else:
        return redirect('/login/')
    
@thc.route('/pswdchange/',methods=['POST'])
def password_modify():
    if session.get('staff_no')!=None and session.get('staff_id')!=None and session.get('staff_name')!=None and session.get('staff_hospid')!=None:
        oldpwd=request.form.get('oldpswd')
        newpwd=request.form.get('newpswd')
        confamnewpwd=request.form.get('confamnewpswd')       
        id=request.form.get('stfff')
        
        
        changes=db.session.query(Staff).filter(Staff.staff_id==id).first()
        if changes:
            existpwdhash=changes.staff_password
            if oldpwd!='' and newpwd!='' and confamnewpwd!='':
                matching=check_password_hash(existpwdhash,oldpwd)
                if matching and newpwd==confamnewpwd:
                    hashedpwd=generate_password_hash(confamnewpwd)
                    changes.staff_password=hashedpwd
                    db.session.commit()
                    flash('Password Reset Successful',category='password_reset')
                    return redirect('/changepassword/')
                else:
                    flash('Password Reset Not Successful',category='password_not_reset')
                    return redirect('/changepassword/')
            else:
                flash('Please complete all fields',category='password_not_reset')
                return redirect('/changepassword/')
        else:
            flash('Something went wrong',category='password_not_reset')
            return redirect('/changepassword/')
    else:
        return redirect('/login/')
    
##### DOCTOR STAFF PHONE CHANGE    
@thc.route('/changephone/')
def staff_changePhone():
    if session.get('staff_no')!=None and session.get('staff_id')!=None and session.get('staff_name')!=None and session.get('staff_hospid')!=None:
        staffinfo=db.session.query(Staff).filter(Staff.staff_id==session.get('staff_id')).all()
        return render_template('staff/changephone.html',staffinfo=staffinfo)
    else:
        return redirect('/login/')
    
@thc.route('/staffphonechange/',methods=['POST'])
def modify_phone():
    if session.get('staff_no')!=None and session.get('staff_id')!=None and session.get('staff_name')!=None and session.get('staff_hospid')!=None:
        old_no=request.form.get('oldnumber')
        new_no=request.form.get('newnumber')
        confam_no=request.form.get('confam_new_number')
        
        id=request.form.get('stfff')
        changes=db.session.query(Staff).get(id)
        if changes:
            if old_no!='' and new_no!='' and confam_no!='':
                if changes.staff_phone==old_no and new_no==confam_no:
                    try:
                        changes.staff_phone=confam_no
                        db.session.commit()
                        flash('Phone Number Successfully Changed',category='phone_changed')
                        return redirect('/changephone/')
                    except:
                        flash('Phone Number Already Exists',category='phone_not_changed')
                        return redirect('/changephone/')
                else:
                    flash('Phone Number Reset Not Successful',category='phone_not_changed')
                    return redirect('/changephone/')
            else:
                flash('Kindly complete all fields',category='phone_not_changed')
                return redirect('/changephone/')
        else:
            flash('Something went wrong',category='phone_not_changed')
            return redirect('/changephone/')
    else:
        return redirect('/login/')
    

#### NURSE STAFF CHANGE PASSWORD
@thc.route('/nursechangepassword/')
def staff_nurse_changepswd():
    if session.get('staff_no')!=None and session.get('staff_id')!=None and session.get('staff_name')!=None and session.get('staff_hospid')!=None:
        staffinfo=db.session.query(Staff).filter(Staff.staff_id==session.get('staff_id')).all()
        return render_template('staff/nursechangepassword.html',staffinfo=staffinfo)
    else:
        return redirect('/login/')



@thc.route('/nursepswdchange/',methods=['POST'])
def nurse_password_modify():
    if session.get('staff_no')!=None and session.get('staff_id')!=None and session.get('staff_name')!=None and session.get('staff_hospid')!=None:
        oldpwd=request.form.get('oldpswd')
        newpwd=request.form.get('newpswd')
        confamnewpwd=request.form.get('confamnewpswd')
        id=request.form.get('stfff')
        
    
        changes=db.session.query(Staff).filter(Staff.staff_id==id).first()
        if changes:
            existpwdhash=changes.staff_password
            if oldpwd!='' and newpwd!='' and confamnewpwd!='':
                matching=check_password_hash(existpwdhash,oldpwd)
                if matching and newpwd==confamnewpwd:
                    hashedpwd=generate_password_hash(confamnewpwd)
                    changes.staff_password=hashedpwd
                    db.session.commit()
                    flash('Password Reset Successful',category='password_reset')
                    return redirect('/nursechangepassword/')
                else:
                    flash('Password Reset Not Successful',category='password_not_reset')
                    return redirect('/nursechangepassword/')
            else:
                flash('Please complete all fields',category='password_not_reset')
                return redirect('/nursechangepassword/')
        else:
            flash('Something went wrong',category='password_not_reset')
            return redirect('/nursechangepassword/')
    else:
        return redirect('/login/')



#### NURSE CHANGE PHONE NUMBER   
@thc.route('/nursechangephone/')
def nurse_changePhone():
    if session.get('staff_no')!=None and session.get('staff_id')!=None and session.get('staff_name')!=None and session.get('staff_hospid')!=None:
        staffinfo=db.session.query(Staff).filter(Staff.staff_id==session.get('staff_id')).all()
        return render_template('staff/nursechangephone.html',staffinfo=staffinfo)
    else:
        return redirect('/login/')    

@thc.route('/nursephonechange/',methods=['POST'])
def modify_nurse_phone():
    if session.get('staff_no')!=None and session.get('staff_id')!=None and session.get('staff_name')!=None and session.get('staff_hospid')!=None:
        old_no=request.form.get('oldnumber')
        new_no=request.form.get('newnumber')
        confam_no=request.form.get('confam_new_number')
        
        id=request.form.get('stfff')
        changes=db.session.query(Staff).get(id)
        if changes:
            if old_no!="" and new_no!="" and confam_no!="":
                if changes.staff_phone==old_no and new_no==confam_no:
                    try:
                        changes.staff_phone=confam_no
                        db.session.commit()
                        flash('Phone Number Successfully Changed',category='phone_changed')
                        return redirect('/nursechangephone/')
                    except:
                        flash('Phone Number Already Exists',category='phone_not_changed')
                        return redirect('/nursechangephone/')
                else:
                    flash('Phone Number Reset Not Successful',category='phone_not_changed')
                    return redirect('/nursechangephone/')
            else:
                flash('Something went wrong',category='phone_not_changed')
                return redirect('/nursechangephone/')
        else:
            flash('Something went wrong',category='phone_not_changed')
            return redirect('/nursechangephone/')
    else:
        return redirect('/login/')   



#### DOCTOR COLLEAGUES LIST AND MSG
@thc.route('/colleagues/')
def find_codocs():
    if session.get('staff_no')!=None and session.get('staff_id')!=None and session.get('staff_name')!=None and session.get('staff_hospid')!=None:
        staffinfo=db.session.query(Staff).filter(Staff.staff_id==session.get('staff_id')).all()
        staff_colleagues=db.session.query(Staff).filter(Staff.stf_hospID==session.get('staff_hospid'),Staff.staff_id!=session.get('staff_id')).all()
        return render_template('staff/colleagues.html',staffinfo=staffinfo,costaff=staff_colleagues)
    else:
        return redirect('/login/')

       
#DOCTORS SEND AND RECEIVE MESSAGE to OUTSIDE STAFF
@thc.route('/sendmessage/',methods=['POST'])
def sendmessage():
    if session.get('staff_no')!=None and session.get('staff_id')!=None and session.get('staff_name')!=None and session.get('staff_hospid')!=None:
        reason=request.form.get('topic')
        msg=request.form.get('message')
        sender=request.form.get('sender')
        senderH=request.form.get('senderhospital')
        receiver=request.form.get('receiver')
        
        if reason!='' and msg!='':
            addmsg=Messages(sender_staff_id=sender,topic=reason,message=msg,receiver_staff_id=receiver,sender_hosp_id=senderH)
            db.session.add(addmsg)
            db.session.commit()
            flash('Message Sent', category='msgsent')
            return redirect('/findstaff/')
        else:
            flash('Fields can\'t be empty', category='bad_sendmsg')
            return redirect('/findstaff/')
    else:
        return redirect('/login/')
    
    
    
#DOCTORS SEND AND RECEIVE MESSAGE to Colleagues
@thc.route('/send_costaff_message/',methods=['POST'])
def send_colleague_message():
    if session.get('staff_no')!=None and session.get('staff_id')!=None and session.get('staff_name')!=None and session.get('staff_hospid')!=None:
        reason=request.form.get('topic')
        msg=request.form.get('message')
        sender=request.form.get('sender')
        senderH=request.form.get('senderhospital')
        receiver=request.form.get('receiver')
        
        if reason!=None and msg!=None:
            addmsg=Messages(sender_staff_id=sender,topic=reason,message=msg,receiver_staff_id=receiver,sender_hosp_id=senderH)
            db.session.add(addmsg)
            db.session.commit()
            return 'Message Sent'
        else:
            return 'Kindly complete all fields'
    else:
        return redirect('/login/') 
    
##MESSAGE REPLY    
@thc.route('/replymsg/',methods=['POST'])
def replymessage():
    if session.get('staff_no')!=None and session.get('staff_id')!=None and session.get('staff_name')!=None and session.get('staff_hospid')!=None:
        rsp=request.form.get('reply')
        msg_deets=request.form.get('msgID')
        timesent=datetime.utcnow()
        sender_deets=request.form.get('senderID')
        
        if rsp!='' and msg_deets!='':
            respondmsg=db.session.query(Messages).get(msg_deets)
            if respondmsg:
                respondmsg.response=rsp
                respondmsg.response_date_sent=timesent
                db.session.commit()
                flash('Reply Sent', category='replysent')
                return redirect('/doctor_dashboard/')
            else:
                flash('Reply Not Sent', category='replynotsent')
                return redirect('/doctor_dashboard/')
        else:
            flash('Fields can\'t be empty', category='bad_reply')
            return redirect('/doctor_dashboard/')
    else:
        return redirect('/login/')
    
##View REPLY    
@thc.route('/replies/')
def replies():
    if session.get('staff_no')!=None and session.get('staff_id')!=None and session.get('staff_name')!=None and session.get('staff_hospid')!=None:
        staffinfo=db.session.query(Staff).filter(Staff.staff_id==session.get('staff_id')).all()
        allreplies=db.session.query(Messages).filter(Messages.sender_staff_id==session.get('staff_id')).order_by(Messages.msg_id.desc()).all()
        
        
        #ASK HOW TO PAGINATE ON MONDAY
        
        # totalreplies=100
        # avg=totalreplies//3
        # pagenumbers=[]
        # offset_no=avg
        # num=0
        # for p in range (offset_no):
        #     num=num+1
        #     pagenumbers.append(num)
        
        return render_template('staff/replypage.html',reply=allreplies,staffinfo=staffinfo)
    else:
        return redirect('/login/')


### PATIENT CASE NOTES
@thc.route('/patientcase/',methods=['POST'])
def patientcase():
    complain=request.form.get('pcomplaint')
    diag=request.form.get('diagnose')
    actionplan=request.form.get('actionplan')
    csrf=request.form.get('csrf_token')
    staff=request.form.get('staff_id')
    patient=request.form.get('patient')
    
    
    if staff != None:
        stf=db.session.query(Appointment).filter(Appointment.apt_staff_id==staff,Appointment.apt_patient_id==patient,func.date(Appointment.date_of_appt)==date.today()).first()
        
        if stf:
            try:
                C=Consultation(con_apt_id=stf.appt_id, con_patient_id=patient, con_hosp_id=stf.apt_hosp_id,con_staff_id=staff,con_dept_id=stf.dept_of_appt,patient_complain=complain,diagnosis=diag,course_of_action=actionplan)
                db.session.add(C)
                db.session.commit()
                
                appt_status=db.session.query(Appointment).filter(Appointment.apt_staff_id==staff,func.date(Appointment.date_of_appt)==date.today()).first()
                appt_status.status='present'
                db.session.commit()
                return 'Case Successfully Added'
            except:
                return 'Not for Admin'
        else:
            return 'No record of appointment found'
    else:
        return 'Admin not allowed' 
    
   
   
   
##### CROSS HOSPITAL CASE NOTES  
@thc.route('/CHTcase/',methods=['POST'])
def cross_hospital():
    
    the_complain=request.form.get('p_cht_complaint')
    the_diagnosis=request.form.get('cht_diagnose')
    the_actionplan=request.form.get('cht_actionplan')
    the_csrf=request.form.get('csrf_token')
    the_staff=request.form.get('cht_staff_id')
    the_patient=request.form.get('cht_patient')
    the_hospital=request.form.get('cht_hospital')
    
    p_parent_clinic=db.session.query(Patient).filter(Patient.patient_id==the_patient).first()
    parent_clinic=p_parent_clinic.patient_hospitle_id
    
    
    
    
    if the_hospital == parent_clinic:
        return 'Sorry, this section is for out patients only. Kindly use the right section' 
    else:
        appt_cht=db.session.query(Staff).filter(Staff.staff_id==the_staff).first()
            
        if appt_cht:
            staffdept=appt_cht.stf_deptID
            staff_clinic=appt_cht.stf_hospID
            
            if staff_clinic==the_hospital:
                return 'Kindly use the right section' 
            else:
                Cross_Treat=Cross_hospital_Treatment(cht_patient_id=the_patient, cht_hosp_id=the_hospital, cht_staff_id=the_staff, cht_dept_id=staffdept, patient_complain=the_complain, diagnosis=the_diagnosis, course_of_action=the_actionplan)
                    
                db.session.add(Cross_Treat)
                db.session.commit()
                return 'Case Successfully Added'
        else:
            return 'No record of this staff found'


#### NURSE REGISTER PATIENT TEMPLATE
@thc.route('/Register/Patient/')
def nurse_register_patient():
    if session.get('staff_no')!=None and session.get('staff_id')!=None and session.get('staff_name')!=None and session.get('staff_hospid')!=None:
        nations=db.session.query(Country).all()
        clinics=db.session.query(Hospital).filter(Hospital.hosp_id==session.get('staff_hospid')).order_by(Hospital.hosp_name).all()
        Nigstates=db.session.query(States).all()
        staffinfo=db.session.query(Staff).filter(Staff.staff_id==session.get('staff_id')).all()
        return render_template('staff/nurseregisterpatient.html',nations=nations,clinics=clinics,Nigstates=Nigstates,staffinfo=staffinfo)
    else:
        return redirect('/login/')
 
##### NURSE REG PATIENT COMPLETION    
@thc.route('/nurseregisterpatient/',methods=['POST'])
def nurse_reg_patients():
    if session.get('staff_no')!=None and session.get('staff_id')!=None and session.get('staff_name')!=None and session.get('staff_hospid')!=None:
        thisyear=date.today().year
        Num=str(random.random() * 1000000)
        No=Num.split('.')
        unique=No[0]
        initials=db.session.query(Hospital).filter(Hospital.hosp_id==session.get('staff_hospid')).first()
        abv=initials.hosp_abv
        
        patientno=abv+'p-'+str(thisyear)+'-'+str(unique)
        pfirstname=request.form.get('firstname')
        plastname=request.form.get('lastname')
        pothername=request.form.get('othername')
        pDOB=request.form.get('DOB')
        pclinic=request.form.get('hospital')
        pphone=request.form.get('phone')
        paddress=request.form.get('address')
        pcountry=request.form.get('country')
        porigin=request.form.get('state')
        preg=request.form.get('Reg_Date')
        pgender=request.form.get('gender')
        pphone_num=re.search("^(080)|^(070)|^(090)|^(081)(([0-9]){8})$",pphone)
        
        
        if pphone_num:
            if pfirstname!="" and plastname!='' and pDOB!='' and pclinic!='' and pphone!='' and paddress!='' and pcountry!='' and porigin!='' and preg!='' and pgender!='':
                if pcountry!='153' and porigin!='38':
                    flash('Foreigners can\'t have a Nigerian state of origin. Please correct.',category='pnotregistered')
                    return redirect('/Register/Patient/')
                elif len(pphone) != 11:
                    flash('Invalid phone number length',category='pnotregistered')
                    return redirect('/Register/Patient/')
                elif pcountry=='153' and porigin=='#':
                    flash('Please select a valid state of origin',category='pnotregistered')
                    return redirect('/Register/Patient/')
                elif pcountry=='153' and porigin=='38':
                    flash('Please select a state of origin for this Nigerian Patient you are trying to register',category='pnotregistered')
                    return redirect('/Register/Patient/')
                else:
                    try:
                        regpatient=Patient(firstname=pfirstname,lname=plastname,othername=pothername,patient_hospitle_id=pclinic,patient_number=patientno,patient_dob=pDOB,patient_phone=pphone,patient_address=paddress,patient_nation=pcountry,patient_state_origin=porigin,patient_gender=pgender,date_reg=preg)
                        if session.get('staff_id')!=None and session.get('staff_no')!=None:
                            db.session.add(regpatient)
                            db.session.commit()
                            thepatientnum=re.sub('-','/',patientno)
                            flash(f'Successfully Registered {pfirstname}. Patient Number is {thepatientnum}',category='newpatient')
                            return redirect('/Register/Patient/')
                        else:
                            return redirect('/login/')
                    except:
                            flash('Sorry, one or more fields already exists and can\'t be repeated.',category='pnotregistered')
                            return redirect('/Register/Patient/')
            else:
                flash('Please fill out all required fields.',category='pnotregistered')
                return redirect('/Register/Patient/')
        else:
            flash('Please input a valid Nigerian phone number',category='pnotregistered')
            return redirect('/Register/Patient/') 
    else:
        return redirect('/login/')
 
 
    
#### ADD APPOINTMENT BY DOCTOR
@thc.route('/add_appts/',methods=['POST'])
def add_new_appointment():
    if session.get('staff_no')!=None and session.get('staff_id')!=None and session.get('staff_name')!=None and session.get('staff_hospid')!=None:
        id_patient=request.form.get('patientID')
        ddate=request.form.get('scheduled_date')
        dhospital=request.form.get('hosp_id')
        deptapt=request.form.get('deptofappt')
        dreason=request.form.get('reason')
        
        staff=request.form.get('doc')
        aptstaff=db.session.query(Staff).filter(Staff.staff_number==staff).all()
        if aptstaff:
            for i in aptstaff:
                staff_id=i.staff_id
        
            appointschedule=Appointment(apt_patient_id=id_patient, date_of_appt=ddate, dept_of_appt=deptapt, apt_hosp_id=dhospital, apt_staff_id=staff_id, purpose=dreason)
            if appointschedule:
                db.session.add(appointschedule)
                db.session.commit()
                flash("Successfully added appointment",category="add_appointment")
                return redirect("/doctor_dashboard/")
            else:
                return "Something went wrong"
        else:
            return "Something went wrong. No record of staff."
            
    elif session.get('admin_no')!=None and session.get('admin_id')!=None and session.get('admin_name')!=None and session.get('hospital_id')!=None:
        return 'Admin can\'t register a new appointment'
    else:
        return redirect('/login/')



##### ADD SURGERY ROUTE
@thc.route('/schedule_surgery/',methods=['POST'])
def add_new_surgery():
    if session.get('staff_no')!=None and session.get('staff_id')!=None and session.get('staff_name')!=None and session.get('staff_hospid')!=None:
        id_patient=request.form.get('patient_for_surg')
        ddate=request.form.get('date_for_surg')
        dhospital=request.form.get('hospital_for_surg')
        deptsurg=request.form.get('dept_for_surg')
        dreason=request.form.get('procedurename')
        
        staff=request.form.get('surgeon')
        
        aptstaff=db.session.query(Staff).filter(Staff.staff_number==staff).all()
        if aptstaff:
            for i in aptstaff:
                staff_id=i.staff_id
        
            surgeryschedule=Surgery(surg_patient_id=id_patient, date_of_surg=ddate, dept_of_surg=deptsurg, surg_hosp_id=dhospital, lead_surgeon_staff_id=staff_id, procedure_name=dreason)
            if surgeryschedule:
                db.session.add(surgeryschedule)
                db.session.commit()
                return "Successfully added surgery"
            else:
                return "Couldn't register surgery. Something went wrong. Please try again"
        else:
            return "Something went wrong. No record of staff."
            
    elif session.get('admin_no')!=None and session.get('admin_id')!=None and session.get('admin_name')!=None and session.get('hospital_id')!=None:
        return 'Admin can\'t register a new surgery'
    else:
        return redirect('/login/')

### Update Surgery by Uploading Test Sheet
@thc.route('/updatesurgery/',methods=['POST'])
def update_surgery():
    
    allowed=['.pdf','.jpeg','.jpg']
    
    attendance=request.form.get('surgical_status')
    patient_info=request.form.get('patient')
    result_sheet=request.files.get('test_sheet')
    IDsurgery=request.form.get('surgery_id')
    
    
    
    if session.get('staff_no')!=None and session.get('staff_id')!=None and session.get('staff_name')!=None and session.get('staff_hospid')!=None:
        if attendance!=None and patient_info!=None and result_sheet!=None:
            
            originalfilename=result_sheet.filename
            
            a, file_ext=os.path.splitext(originalfilename)
            
            if file_ext in allowed:
                originalfile = "finalpkg/static/fileupload/"+str(patient_info)+originalfilename
                result_sheet.save(originalfile)
                
                surgeryupdate=db.session.query(Surgery).get(IDsurgery)
                surgeryupdate.status=attendance
                surgeryupdate.test_results=str(patient_info)+originalfilename
                db.session.commit()
                return 'Update Successful'
            else:
                return 'Please select a file with a .jpg, .jpeg, or .pdf format'
        else:
            return 'Please complete all fields'
            
            
    elif session.get('admin_no')!=None and session.get('admin_id')!=None and session.get('admin_name')!=None and session.get('hospital_id')!=None:
        return 'Admin can\'t register a new surgery'
    else:
        return redirect('/login/')

#### DOWNLOAD TEST
@thc.route('/downloadfile/<filename>')
def download_testresult(filename):
    if session.get('staff_no')!=None and session.get('staff_id')!=None and session.get('staff_name')!=None and session.get('staff_hospid')!=None:
        return send_from_directory(thc.config['UPLOAD_FOLDER'],filename, as_attachment=True)
    else:
        return redirect('/login/')