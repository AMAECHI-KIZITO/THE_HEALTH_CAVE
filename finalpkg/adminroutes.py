import re,os,random
from datetime import datetime,date
from flask import Flask,render_template,abort,request,make_response,redirect,flash,session
from werkzeug.security import generate_password_hash, check_password_hash
from finalpkg import thc,db,csrf
from finalpkg.thc_models import *


# Admin Page Route
@thc.route('/adminpage/')
def adminhome():
    if session.get('admin_no')!=None and session.get('admin_id')!=None and session.get('admin_name')!=None and session.get('hospital_id')!=None:
        admininfo=db.session.query(Admin).filter(Admin.admin_id==session.get('admin_id')).all()
        
        totalstaff=db.session.query(Staff).filter(Staff.stf_hospID==session.get('hospital_id')).count()
        
        totalpatients=db.session.query(Patient).filter(Patient.patient_hospitle_id==session.get('hospital_id')).count()
        
        total_cross_patients=db.session.query(Cross_hospital_Treatment).filter(Cross_hospital_Treatment.cht_hosp_id==session.get('hospital_id')).count()
        
        return render_template('dashboard.html',totalstaff=totalstaff,totalpatients=totalpatients, CHT=total_cross_patients, admininfo=admininfo)
    else:
        return redirect('/login/')


@thc.route('/appointments/')
def appointments():
    if session.get('admin_no')!=None and session.get('admin_id')!=None and session.get('admin_name')!=None and session.get('hospital_id')!=None:
        admininfo=db.session.query(Admin).filter(Admin.admin_id==session.get('admin_id')).all()
        allappt=db.session.query(Appointment).filter(Appointment.apt_hosp_id==session.get('hospital_id')).all()
        return render_template('appointments.html',allappt=allappt,admininfo=admininfo)
    else:
        return redirect('/login/')



@thc.route('/staffsearch/')
def search_staff():
    if session.get('admin_no')!=None and session.get('admin_id')!=None and session.get('admin_name')!=None and session.get('hospital_id')!=None:
        admininfo=db.session.query(Admin).filter(Admin.admin_id==session.get('admin_id')).all()
        return render_template('searchstaff.html',admininfo=admininfo)
    else:
        return redirect('/login/')
    
@thc.route('/adminsearch/',methods=['POST'])
def admin_search_staff():
    if session.get('admin_no')!=None and session.get('admin_id')!=None and session.get('admin_name')!=None and session.get('hospital_id')!=None:
        admininfo=db.session.query(Admin).filter(Admin.admin_id==session.get('admin_id')).all()
        findthis=request.form.get('staffno')
        
        modified=re.sub('/','-',findthis)
        find=db.session.query(Staff).filter((Staff.staff_number==modified)|(Staff.fname==modified)|(Staff.lname==modified)|(Staff.othername==modified)).all()
        
        if findthis=="":
            flash('Please fill out the fields', category='no_staff_found')
            return render_template('searchstaff.html',admininfo=admininfo)
        elif find:
            return render_template('searchstaffresult.html',find=find,admininfo=admininfo)
        else:
            flash('No record match', category='no_record_found')
            return render_template('searchstaff.html',admininfo=admininfo)
    else:
        return redirect('/login/')


# ADD Staff ROUTE
@thc.route('/addstaff/')
def add_staff():
    if session.get('admin_no')!=None and session.get('admin_id')!=None and session.get('admin_name')!=None and session.get('hospital_id')!=None:
        admininfo=db.session.query(Admin).filter(Admin.admin_id==session.get('admin_id')).all()
        nations=db.session.query(Country).all()
        clinics=db.session.query(Hospital).filter(Hospital.hosp_id==session.get('hospital_id')).order_by(Hospital.hosp_name).all()
        role=db.session.query(Role).order_by(Role.role_name).all()
        Nigstates=db.session.query(States).all()
        units=db.session.query(Hospital_Depts).filter(Hospital_Depts.facilityID==session.get('hospital_id')).all()
        return render_template('addstaff.html',nation=nations,naijastates=Nigstates,units=units,clinics=clinics,role=role,admininfo=admininfo)
    else:
        return redirect('/login/')


# Addstaff validation ROUTE
@thc.route('/submitnewstaff/',methods=['POST'])
def submitnewstaff():
    thisyear=date.today().year
    Num=str(random.random() * 1000000)
    No=Num.split('.')
    unique=No[0]
    initials=db.session.query(Hospital).filter(Hospital.hosp_id==session.get('hospital_id')).first()
    abv=initials.hosp_abv
    
    staffno=abv+'s-'+str(thisyear)+'-'+str(unique)
    modifiedstaffno=re.sub('-','/',staffno)
    
    sfirstname=request.form.get('firstname')
    slastname=request.form.get('lastname')
    sothername=request.form.get('othername')
    semail=request.form.get('email')
    sDOB=request.form.get('DOB')
    sclinic=request.form.get('hosp_id')
    srole=request.form.get('role')
    sphone=request.form.get('phone')
    saddress=request.form.get('address')
    scountry=request.form.get('country')
    sorigin=request.form.get('state')
    sdept=request.form.get('wing')
    sgender=request.form.get('gender')
    defaultpassword="0000"
    formattedpwd=generate_password_hash(defaultpassword)
    phone_num=re.search("^(080)|^(070)|^(090)|^(081)(([0-9]){8})$",sphone)
    
    
    if phone_num:
        if sfirstname!='' and slastname!='' and semail!='' and sDOB!='' and sclinic!='' and srole!='' and sphone!='' and saddress!='' and scountry!='' and sorigin!='' and sdept!='' and sgender!='':
            
            if scountry!='153' and sorigin!='38':
                flash('Foreigners can\'t have a Nigerian state of origin. Please correct.',category='notregistered')
                return redirect('/addstaff/')
            elif len(sphone) != 11:
                flash('Invalid phone number length',category='notregistered')
                return redirect('/addstaff/')
            elif scountry=='153' and sorigin=='#':
                    flash('Please select valid state of origin',category='notregistered')
                    return redirect('/addstaff/')
            elif scountry=='153' and sorigin=='38':
                    flash('Please select a Nigerian state of origin for this Nigerian staff you are trying to register',category='notregistered')
                    return redirect('/addstaff/')
            else:
                try:
                    regstaff=Staff(fname=sfirstname,lname=slastname,othername=sothername,stf_hospID=sclinic,staff_number=staffno,staff_email=semail,staff_dob=sDOB,staff_role=srole,staff_phone=sphone,staff_address=saddress,stf_nationality=scountry,staff_s_origin=sorigin,stf_deptID=sdept,staff_gender=sgender,staff_password=formattedpwd)
                    if session.get('admin_id')!=None and session.get('admin_no')!=None:
                        db.session.add(regstaff)
                        db.session.commit()
                        with open("staffinfo.txt",'a')as file:
                            file.write(f"Staff number is {staffno}, default password is {defaultpassword}, staff email is {semail} \n")
                        flash(f"Successfully Registered {sfirstname} with staff number {modifiedstaffno}",category='newstaff')
                        return redirect('/addstaff/')
                    else:
                        return redirect('/login/')
                except:
                    flash('Sorry, one or more fields already exists and can\'t be repeated.',category='notregistered')
                    return redirect('/addstaff/')
        else:
            flash('Please fill out all required fields.',category='notregistered')
            return redirect('/addstaff/')        
    else:
        flash('Please input a valid Nigerian phone number',category='notregistered')
        return redirect('/addstaff/') 




# All Staff ROUTE
@thc.route('/allstaff/')
def all_staff():
    if session.get('admin_no')!=None and session.get('admin_id')!=None and session.get('admin_name')!=None and session.get('hospital_id')!=None:
        admininfo=db.session.query(Admin).filter(Admin.admin_id==session.get('admin_id')).all()
        
        totalstaff=db.session.query(Staff).filter(Staff.stf_hospID==session.get('hospital_id')).all()
        return render_template('stafflist.html',totalstaff=totalstaff,admininfo=admininfo)
    else:
        return redirect('/login/')



###UPDATE HOSPITAL INFO ADD DEPTS
@thc.route('/updatehospitalinfo/')
def update_hospital_profile():
    if session.get('admin_no')!=None and session.get('admin_id')!=None and session.get('admin_name')!=None and session.get('hospital_id')!=None:
        t=[]
        admininfo=db.session.query(Admin).filter(Admin.admin_id==session.get('admin_id')).all()
        
        existingdept=db.session.query(Hospital_Depts).filter(Hospital_Depts.facilityID==session.get('hospital_id')).all()
        for i in existingdept:
            exists=i.facility_dpt_id
            t.append(exists)
        
        alldepts=db.session.query(Department).filter(~Department.dept_id.in_(t)).order_by(Department.dept_name).all()
        
        return render_template('hospital_profile_update.html',alldepts=alldepts,admininfo=admininfo,t=t)
    else:
        return redirect('/login/')


@thc.route('/updatehospital/',methods=['POST'])
def update_hospital_submit():
    if session.get('admin_no')!=None and session.get('admin_id')!=None and session.get('admin_name')!=None and session.get('hospital_id')!=None:
        departs=request.form.getlist('depts')
        if departs:
            for dpt in departs:
                HD=Hospital_Depts(facilityID=session.get('hospital_id'),facility_dpt_id=dpt)
                
                db.session.add(HD)
                db.session.commit()
            flash ("Successfully added departments",category='added_dept')
            return redirect('/departments/')
        else:
            flash ("Please select departments",category='dept_not_added')
            return redirect('/updatehospitalinfo/')
    else:
        return redirect('/login/')
  
    
##### REGISTER LABORATORIES
@thc.route('/admin/register/labs/')
def register_hospital_labs():
    if session.get('admin_no')!=None and session.get('admin_id')!=None and session.get('admin_name')!=None and session.get('hospital_id')!=None:
        
        admininfo=db.session.query(Admin).filter(Admin.admin_id==session.get('admin_id')).all()
        
        departmentavailable=db.session.query(Hospital_Depts).filter(Hospital_Depts.facilityID==session.get("hospital_id"),Hospital_Depts.facility_dpt_id=='23').all()
        
        if departmentavailable:
            l=[]
            existinglabs=db.session.query(Hlab).filter(Hlab.hlab_hospital_id==session.get('hospital_id')).all()
            for i in existinglabs:
                exists=i.hlab_lab_id
                l.append(exists)
            
            all_labs=db.session.query(Laboratory).filter(~Laboratory.lab_id.in_(l)).all()
        
            return render_template('hospital_labs_update.html',admininfo=admininfo,labs=all_labs,l=l)
        else:
            flash ("You do not have Laboratory Science as a department in your facility. Ensure you have chosen it before adding laboratories ",category='labsciabsent')
            return redirect("/updatehospitalinfo/")
    else:
        return redirect('/login/')



@thc.route('/reg_hospital_labs/',methods=['POST'])
def register_hospital_labs_submit():
    if session.get('admin_no')!=None and session.get('admin_id')!=None and session.get('admin_name')!=None and session.get('hospital_id')!=None:
        
        labs=request.form.getlist('h_lab')
        if labs:
            for dlabs in labs:
                HL=Hlab(hlab_hospital_id=session.get('hospital_id'),hlab_lab_id=dlabs)
                
                db.session.add(HL)
                db.session.commit()
            flash ("Successfully added Laboratories",category='added_labs')
            return redirect('/admin/register/labs/')
        else:
            flash ("Please check the laboratores available in your facility",category='lab_not_added')
            return redirect('/admin/register/labs/')
    else:
        return redirect('/login/')   
    
#### ALL HOSPITAL DEPARTMENT LIST
@thc.route('/departments/')
def department():
    if session.get('admin_no')!=None and session.get('admin_id')!=None and session.get('admin_name')!=None and session.get('hospital_id')!=None:
        admininfo=db.session.query(Admin).filter(Admin.admin_id==session.get('admin_id')).all()
        hospdepts=db.session.query(Hospital_Depts).filter(Hospital_Depts.facilityID==session.get('hospital_id')).all()
        hosplabs=db.session.query(Hlab).filter(Hlab.hlab_hospital_id==session.get('hospital_id')).all()
        return render_template('department.html',HD=hospdepts,admininfo=admininfo,HL=hosplabs)
    else:
        return redirect('/login/')



@thc.route('/addpatients/')
def add_patient():
    if session.get('admin_no')!=None and session.get('admin_id')!=None and session.get('admin_name')!=None and session.get('hospital_id')!=None:
        admininfo=db.session.query(Admin).filter(Admin.admin_id==session.get('admin_id')).all()
        nations=db.session.query(Country).all()
        clinics=db.session.query(Hospital).filter(Hospital.hosp_id==session.get('hospital_id')).order_by(Hospital.hosp_name).all()
        Nigstates=db.session.query(States).all()
        return render_template('newpatients.html',nations=nations,clinics=clinics,Nigstates=Nigstates,admininfo=admininfo)
    else:
        return redirect('/login/')



#reg NEW PATIENT ROUTE
@thc.route('/registerpatient/',methods=['POST'])
def reg_patients():
    if session.get('admin_no')!=None and session.get('admin_id')!=None and session.get('admin_name')!=None and session.get('hospital_id')!=None:
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
        pphone_num=re.search("^(080)|^(070)|^(090)|^(081)|([0-9]{8})$",pphone)
        
        if pphone_num:
            if pfirstname!='' and plastname!='' and pDOB!='' and pclinic!='' and pphone!='' and paddress!='' and pcountry!='' and porigin!='' and preg!='' and pgender!='':
                
                if pcountry!='153' and porigin!='38':
                    flash('Foreigners can\'t have a Nigerian state of origin. Please correct.',category='pnotregistered')
                    return redirect('/addpatients/')
                elif pcountry=='153' and porigin=='#':
                    flash('Please select a valid state of origin',category='pnotregistered')
                    return redirect('/addpatients/')
                elif pcountry=='153' and porigin=='38':
                    flash('Please select a state of origin for this Nigerian Patient you are trying to register',category='pnotregistered')
                    return redirect('/addpatients/')
                else:
                    try:
                        regpatient=Patient(firstname=pfirstname,lname=plastname,othername=pothername,patient_hospitle_id=pclinic,patient_number=patientno,patient_dob=pDOB,patient_phone=pphone,patient_address=paddress,patient_nation=pcountry,patient_state_origin=porigin,patient_gender=pgender,date_reg=preg)
                        if session.get('admin_id')!=None and session.get('admin_no')!=None:
                            db.session.add(regpatient)
                            db.session.commit()
                            thepatientnum=re.sub('-','/',patientno)
                            flash(f'Successfully Registered {pfirstname}. Patient Number is {thepatientnum}',category='newpatient')
                            return redirect('/addpatients/')
                        else:
                            return redirect('/login/')
                    except:
                            flash('Sorry, one or more fields already exists and can\'t be repeated.',category='pnotregistered')
                            return redirect('/addpatients/')
            else:
                flash('Please fill out all required fields.',category='pnotregistered')
                return redirect('/addpatients/')
        else:
            flash('Please input a valid Nigerian phone number',category='pnotregistered')
            return redirect('/addpatients/') 
    else:
        return redirect('/login/')


##### All PATIENTS LIST
@thc.route('/allpatients/')
def all_patients():
    if session.get('admin_no')!=None and session.get('admin_id')!=None and session.get('admin_name')!=None and session.get('hospital_id')!=None:
        admininfo=db.session.query(Admin).filter(Admin.admin_id==session.get('admin_id')).all()
        all=db.session.query(Patient).filter(Patient.patient_hospitle_id==session.get('hospital_id')).all()
        return render_template('allpatients.html',allp=all,admininfo=admininfo)
    else:
        return redirect('/login/')
    
    
    
#ADMIN PASSWORD CHANGE TEMPLATE  
@thc.route('/adminchangepassword/')
def adminpasswordchange():
    if session.get('admin_no')!=None and session.get('admin_id')!=None and session.get('admin_name')!=None and session.get('hospital_id')!=None:
        admininfo=db.session.query(Admin).filter(Admin.admin_id==session.get('admin_id')).all()
        
        return render_template('adminchangepassword.html',admininfo=admininfo)
    else:
        return redirect('/login/')
    
@thc.route('/adminpswdchange/',methods=['POST'])
def adminpassword_modify():
    if session.get('admin_no')!=None and session.get('admin_id')!=None and session.get('admin_name')!=None and session.get('hospital_id')!=None:
        oldpwd=request.form.get('oldpswd')
        newpwd=request.form.get('newpswd')
        confamnewpwd=request.form.get('confamnewpswd')
        
        id=request.form.get('stfff')
        changes=db.session.query(Admin).get(id)
        if changes:
            if changes.password==oldpwd and newpwd==confamnewpwd:
                changes.password=confamnewpwd
                db.session.commit()
                flash('Password Reset Successful',category='password_reset')
                return redirect('/adminchangepassword/')
            else:
                flash('Password Reset Not Successful',category='password_not_reset')
                return redirect('/adminchangepassword/')
        else:
            flash('Something went wrong',category='password_not_reset')
            return redirect('/adminchangepassword/')
    else:
        return redirect('/login/')
    
    
    
##ADMIN PHONE CHANGE
@thc.route('/adminchangephone/')
def adminphonechange():
    if session.get('admin_no')!=None and session.get('admin_id')!=None and session.get('admin_name')!=None and session.get('hospital_id')!=None:
        admininfo=db.session.query(Admin).filter(Admin.admin_id==session.get('admin_id')).all()
        return render_template('adminchangephone.html',admininfo=admininfo)
    else:
        return redirect('/login/')
    
@thc.route('/adminphonechange/',methods=['POST'])
def admin_modify_phone():
    if session.get('admin_no')!=None and session.get('admin_id')!=None and session.get('admin_name')!=None and session.get('hospital_id')!=None:
        old_digits=request.form.get('oldnumber')
        new_no=request.form.get('newnumber')
        confam_no=request.form.get('confam_new_number')
        
        id=request.form.get('stfff')
        changes=db.session.query(Admin).get(id)
        if changes:
            if changes.Phone==old_digits and new_no==confam_no:
                try:
                    changes.Phone=confam_no
                    db.session.commit()
                    flash('Phone Number Successfully Changed',category='phone_changed')
                    return redirect('/adminchangephone/')
                except:
                    flash('Phone Number Already Exists',category='phone_not_changed')
                    return redirect('/adminchangephone/')
            else:
                flash('Password Reset Not Successful',category='phone_not_changed')
                return redirect('/adminchangephone/')
        else:
            flash('Something went wrong',category='phone_not_changed')
            return redirect('/adminchangephone/')
    else:
        return redirect('/login/')