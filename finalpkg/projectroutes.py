"""This route is for what the admin and staff share in common"""

import re
from flask import Flask,render_template,abort,request,make_response,redirect,flash,session
from werkzeug.security import generate_password_hash, check_password_hash
from finalpkg import thc,db,csrf
from finalpkg.thc_models import *


# HOMEPAGE ROUTE
@thc.route('/THChomepage/')
@thc.route('/')
def homepage():
    return render_template('healthcavehome.html')

# Bookdemo ROUTE
@thc.route('/bookdemorequest/',methods=['POST'])
def bookdemo():
    fname=request.form.get('firstname')
    lstname=request.form.get('lastname')
    email_ad=request.form.get('email')
    org=request.form.get('organization_name')
    range_emp=request.form.get('range_of_employees')
    phoneno=request.form.get('phone')
    phonenum=re.search("^(080)|^(070)|^(090)|^(081)(([0-9]){8})$",phoneno)
    msg=request.form.get('demomessage')
    # msg=re.sub("'","\\'",msg)
    
    if fname!=None and lstname!=None and email_ad!= None and org!=None and range_emp!=None and phoneno!=None and msg!=None:
        if phonenum and len(phoneno)==11:
            demo=Bookdemo(firstname=fname,email=email_ad,lname=lstname,org_name=org,employee_range=range_emp,Phone=phoneno,message=msg)
            db.session.add(demo)
            db.session.commit()
            return "Message Sent"
        else:
            return "Sorry, Invalid Phone number. Please enter a valid Nigerian number or ensure that the length of phone number is complete"           
    else:
        return "Please fill out all fields"
    
    
# contactusform submit ROUTE
@thc.route('/submitcontact/',methods=['POST','GET'])
def submitcontact():
    if request.method=='GET':
        return redirect('/contact_us')
    else:
        fname=request.form.get('firstname')
        lstname=request.form.get('lastname')
        email_ad=request.form.get('email')
        org=request.form.get('orgname')
        msg=request.form.get('message')
        phoneno=request.form.get('phone')
        phonenum=re.search("^(080)|^(070)|^(090)|^(081) ([0-9]{8})$",phoneno)
        if phonenum:
            if fname!='' and lstname!='' and email_ad!='' and org!='' and phoneno!='' and msg!='':
                try:
                    reachout=Contact_us(firstname=fname,email=email_ad,lname=lstname,org_name=org,Phone=phoneno,message=msg)
                    db.session.add(reachout)
                    db.session.commit()
                    flash(f'Thank you {fname}. Successfully Sent',category='contact')
                    return redirect('/contact_us/')
                except:
                    flash('Sorry, this email already exists',category='notsent')
                    return redirect('/contact_us/')
            else:
                flash(f'Please ensure all fields are completed',category='notsent')
                return redirect('/contact_us/')
        else:
            flash('Sorry, Invalid Phone number. Please enter a valid Nigerian number',category='notsent')
            return redirect('/contact_us/')
   
   
    
# Contact us ROUTE
@thc.route('/contact_us/')
def contact_us():
    return render_template('contactTHC.html')



#  Log In Page Route
@thc.route('/login/')
def loginpage():
    return render_template('THClogin.html')


#  Verify Log In Submission Route
@thc.route('/THCentryportal/',methods=['POST','GET'])
def entryportal():
    emailprovided=request.form.get('email')
    passwordprovided=request.form.get('pswd')
    loginas=request.form.get('cliententry')
    
    
    if request.method=='GET':
        return render_template('THClogin.html')
    elif emailprovided==None and passwordprovided==None:
        flash('Please Input All Fields',category='Invalid')
        return redirect('/login/')
    else:
        if loginas=='admin':
            allow=db.session.query(Admin).filter(Admin.email==emailprovided,Admin.password==passwordprovided).first()
            if allow:
                adminNAME=allow.fname
                adminNUM=allow.admin_no
                adminhospID=allow.admin_hospID
                adminID=allow.admin_id
                session['admin_no']=adminNUM
                session['admin_id']=adminID
                session['admin_name']=adminNAME
                session['hospital_id']=adminhospID
                return redirect('/adminpage/')
            else:
                flash('Incorrect Details',category='Invalid')
                return redirect('/login/')
            
        elif loginas=='staff':
            verify=db.session.query(Staff).filter(Staff.staff_email==emailprovided).first()
            staffhashed=verify.staff_password
            if verify and check_password_hash(staffhashed, passwordprovided):
                thestaffrole=verify.staff_role
                session['staff_no']=verify.staff_number
                session['staff_id']=verify.staff_id
                session['staff_hospid']=verify.stf_hospID
                session['staff_role']=thestaffrole
                session['staff_name']=verify.fname
                session['staff_dept']=verify.stf_deptID
                if thestaffrole==1:
                    return redirect('/doctor_dashboard/')
                elif thestaffrole==2:
                     return redirect('/nurse_dashboard/')    
                else:
                   return "No dashboard yet for this role."          
            else:
                flash('Incorrect Details',category='Invalid')
                return redirect('/login/')


@thc.after_request
def clearcache(response):
    response.headers['Cache-Control']='no-cache, no store, must-revalidate'
    return response

       
# Staff Logout ROUTE
@thc.route('/stafflogout/')
def stafflogout():
    session.pop("staff_no",None)
    session.pop("staff_id",None)
    session.pop("staff_hospid",None)
    session.pop("staff_role",None)
    return redirect('/login/')


# Admin Logout ROUTE
@thc.route('/adminlogout/')
def adminlogout():
    session.pop("admin_no",None)
    session.pop("admin_id",None)
    session.pop("admin_name",None)
    session.pop("hospital_id",None)
    return redirect('/login/')





#### PATIENT PROFILE ROUTE

@thc.route('/patientprofile/<patient_number>')
def patient_profile(patient_number):
    if session.get('admin_no')!=None and session.get('admin_id')!=None and session.get('admin_name')!=None and session.get('hospital_id')!=None:
        thispatient=db.session.query(Patient).filter(Patient.patient_number==patient_number).all()
        for Pid in thispatient:
            patientid=Pid.patient_id
            
        hspdpt=db.session.query(Hospital_Depts).filter((Hospital_Depts.facilityID==session.get('staff_hospid'))|(Hospital_Depts.facilityID==session.get('hospital_id'))).all()
        
        healthfacility=db.session.query(Hospital).filter((Hospital.hosp_id==session.get('staff_hospid'))|(Hospital.hosp_id==session.get('hospital_id'))).all()
        
        allappt=db.session.query(Appointment).filter(Appointment.apt_patient_id==patientid).all()
        
        consults=db.session.query(Consultation).filter(Consultation.con_patient_id==patientid).all()
        
        operations=db.session.query(Surgery).filter(Surgery.surg_patient_id==patientid).all()
        
        treatment=db.session.query(Cross_hospital_Treatment).filter(Cross_hospital_Treatment.cht_patient_id==patientid).all()
        
        for ails in thispatient:
            if ails.patient_gender=='female':
                return render_template('fpatientprofile.html',thispatient=thispatient,hspdpt=hspdpt,healthfacility=healthfacility,allappt=allappt,consults=consults,surgery=operations,treatment=treatment)
            else:
                return render_template('mpatientprofile.html',thispatient=thispatient,hspdpt=hspdpt,healthfacility=healthfacility,allappt=allappt,consults=consults,surgery=operations,treatment=treatment)
      
            
    elif session.get('staff_no')!=None and session.get('staff_id')!=None and session.get('staff_name')!=None and session.get('staff_hospid')!=None:
        thispatient=db.session.query(Patient).filter(Patient.patient_number==patient_number).all()
        for Pid in thispatient:
            patientid=Pid.patient_id
        
        hspdpt=db.session.query(Hospital_Depts).filter((Hospital_Depts.facilityID==session.get('staff_hospid'))|(Hospital_Depts.facilityID==session.get('hospital_id'))).all()
        
        healthfacility=db.session.query(Hospital).filter((Hospital.hosp_id==session.get('staff_hospid'))|(Hospital.hosp_id==session.get('hospital_id'))).all()
        
        allappt=db.session.query(Appointment).filter(Appointment.apt_patient_id==patientid).all()
        
        consults=db.session.query(Consultation).filter(Consultation.con_patient_id==patientid).all()
        
        staffdeets=db.session.query(Staff).filter(Staff.staff_id==session.get('staff_id')).all()
        
        operations=db.session.query(Surgery).filter(Surgery.surg_patient_id==patientid).all()
        treatment=db.session.query(Cross_hospital_Treatment).filter(Cross_hospital_Treatment.cht_patient_id==patientid).all()
        
        for ails in thispatient:
            if ails.patient_gender=='female':
                return render_template('fpatientprofile.html',thispatient=thispatient,hspdpt=hspdpt,healthfacility=healthfacility,allappt=allappt,consults=consults,staffdeets=staffdeets,surgery=operations,treatment=treatment)
            else:
                return render_template('mpatientprofile.html',thispatient=thispatient,hspdpt=hspdpt,healthfacility=healthfacility,allappt=allappt,consults=consults,staffdeets=staffdeets,surgery=operations,treatment=treatment)
    else:
        return redirect('/login/')
    #return render_template('fpatientprofile.html')



## View Cases of patient
@thc.route('/cases/<id>')
def viewcase(id):
    if session.get('staff_no')!=None and session.get('staff_id')!=None and session.get('staff_name')!=None and session.get('staff_hospid')!=None:
        casenote=db.session.query(Consultation).filter(Consultation.consult_id==id).first()
        return render_template('cases.html',casenote=casenote)
    
    elif session.get('admin_no')!=None and session.get('admin_id')!=None and session.get('admin_name')!=None and session.get('hospital_id')!=None:
        casenote=db.session.query(Consultation).filter(Consultation.consult_id==id).first()
        return render_template('cases.html',casenote=casenote)
    else:
        return redirect('/login/')





@thc.errorhandler(404)
def page_missing(error):
    return render_template('THCerror404.html'),404

@thc.errorhandler(500)
def server_error(error):
    return render_template('THCerror500.html'),500

@thc.route('/gynecology/')
def dept_gyne():
    return render_template('obgyn.html')

@thc.route('/paediatrics/')
def dept_paeds():
    return render_template('paediatrics.html')

@thc.route('/physiotherapy/')
def dept_physio():
    return render_template('physiotherapy.html')


