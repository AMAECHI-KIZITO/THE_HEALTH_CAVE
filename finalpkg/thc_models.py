from datetime import datetime
from finalpkg import db

class Admin(db.Model):
    admin_id=db.Column(db.Integer(),primary_key=True, autoincrement=True, nullable=False)
    fname=db.Column(db.String(50),nullable=False)
    lname=db.Column(db.String(50),nullable=False)
    other_name=db.Column(db.String(50),nullable=False)
    admin_hospID=db.Column(db.Integer(),db.ForeignKey('hospital.hosp_id')) #fk
    address=db.Column(db.Text(),nullable=False)
    Phone=db.Column(db.String(11),nullable=False,unique=True)
    DOB=db.Column(db.Date(),nullable=False)
    gender=db.Column(db.String(10),nullable=False)
    admin_nation=db.Column(db.Integer(),db.ForeignKey('country.country_id')) #fk
    admin_state_of_origin=db.Column(db.Integer(),db.ForeignKey('states.state_id')) #fk
    email=db.Column(db.String(100),nullable=False,unique=True)
    password=db.Column(db.String(20),nullable=False,unique=True)
    admin_no=db.Column(db.String(15),nullable=False,unique=True)

class Hospital(db.Model):
    hosp_id=db.Column(db.Integer(),primary_key=True,autoincrement=True,nullable=False)
    hosp_name=db.Column(db.String(255),nullable=False)
    hosp_abv=db.Column(db.String(5),nullable=False)
    hosp_address=db.Column(db.Text(),nullable=False)
    date_hosp_reg=db.Column(db.DateTime(),nullable=False,default=datetime.utcnow())
    hosp_phone=db.Column(db.String(11),nullable=False,unique=True)
    hosp_email=db.Column(db.String(100),nullable=False,unique=True)
    CMD_fullname=db.Column(db.String(100),nullable=True)
    nation=db.Column(db.Integer(),db.ForeignKey('country.country_id')) #fk
    
    staffhosp=db.relationship('Staff',backref='stf_hospitle')
    adminhosp=db.relationship('Admin',backref='admin_hospitle')
    Hospital_dpts=db.relationship('Hospital_Depts',backref='dhospital')
    Hospital_surgeries=db.relationship('Surgery',backref='hospital_deets')
    
class Bookdemo(db.Model):
    bookdemo_id=db.Column(db.Integer(),primary_key=True, autoincrement=True, nullable=False)
    firstname=db.Column(db.String(50),nullable=False)
    lname=db.Column(db.String(50),nullable=False)
    org_name=db.Column(db.String(255),nullable=False)
    employee_range=db.Column(db.Integer(),nullable=False)
    email=db.Column(db.String(100),nullable=False,unique=True)
    Phone=db.Column(db.String(11),nullable=False)
    message=db.Column(db.Text(),nullable=False)
    
class Contact_us(db.Model):
    contact_us_id=db.Column(db.Integer(),primary_key=True, autoincrement=True, nullable=False)
    firstname=db.Column(db.String(50),nullable=False)
    lname=db.Column(db.String(50),nullable=False)
    org_name=db.Column(db.String(255),nullable=False)
    email=db.Column(db.String(100),nullable=False,unique=True)
    Phone=db.Column(db.String(11),nullable=False)
    message=db.Column(db.Text(),nullable=False)
    
class Staff(db.Model):
    staff_id=db.Column(db.Integer(),primary_key=True, autoincrement=True)
    fname=db.Column(db.String(50),nullable=False)
    lname=db.Column(db.String(50),nullable=False)
    othername=db.Column(db.String(50),nullable=True)
    stf_hospID=db.Column(db.Integer(),db.ForeignKey('hospital.hosp_id')) #fk
    staff_number=db.Column(db.String(20),unique=True,nullable=False)
    staff_email=db.Column(db.String(100),unique=True,nullable=False)
    staff_dob=db.Column(db.Date(),nullable=False)
    staff_date_registered=db.Column(db.Date(),nullable=False,default=datetime.utcnow())
    staff_role=db.Column(db.Integer(),db.ForeignKey('role.role_id')) #fk
    staff_phone=db.Column(db.String(11),unique=True,nullable=False)
    staff_address=db.Column(db.Text(),nullable=False)
    stf_nationality=db.Column(db.Integer(),db.ForeignKey('country.country_id')) #fk
    staff_s_origin=db.Column(db.Integer(),db.ForeignKey('states.state_id')) #fk
    stf_deptID=db.Column(db.Integer(),db.ForeignKey('department.dept_id')) #fk
    staff_gender=db.Column(db.String(6),nullable=False)
    staff_password=db.Column(db.String(200),nullable=False)
    
    staff_dept=db.relationship('Department',backref='staff_deets')
    staff_Appointment=db.relationship('Appointment',backref='apt_staff_deets')
    
    
    
    

class Patient(db.Model):
    patient_id=db.Column(db.Integer(),primary_key=True, autoincrement=True)
    firstname=db.Column(db.String(50),nullable=False)
    lname=db.Column(db.String(50),nullable=False)
    othername=db.Column(db.String(50),nullable=True)
    patient_hospitle_id=db.Column(db.Integer(),db.ForeignKey('hospital.hosp_id')) #fk
    patient_number=db.Column(db.String(20),unique=True,nullable=False)
    date_reg=db.Column(db.Date(),nullable=False,default=datetime.utcnow())
    patient_dob=db.Column(db.Date(),nullable=False)
    patient_phone=db.Column(db.String(11),nullable=False)
    patient_address=db.Column(db.Text(),nullable=False)
    patient_nation=db.Column(db.Integer(),db.ForeignKey('country.country_id')) #fk
    patient_state_origin=db.Column(db.Integer(),db.ForeignKey('states.state_id')) #fk
    patient_gender=db.Column(db.String(6),nullable=False)
    
    patientapts=db.relationship('Appointment',backref='patient_deets')
    patienthospital=db.relationship('Hospital',backref='Hospital_patient')
    patient_surgery=db.relationship("Surgery",backref="surgery_patient_info")

class Laboratory(db.Model):
    lab_id=db.Column(db.Integer(),primary_key=True,autoincrement=True)
    lab_name=db.Column(db.String(70),nullable=False)
    
class Test(db.Model):
    test_id=db.Column(db.Integer(),primary_key=True,autoincrement=True)
    test_name=db.Column(db.String(70),nullable=False)
    
class Country(db.Model):
    country_id=db.Column(db.Integer(),primary_key=True,autoincrement=True)
    country_name=db.Column(db.String(70),nullable=False)
    
    country_patient=db.relationship('Patient',backref='patientcountry')
    
class States(db.Model):
    state_id=db.Column(db.Integer(),nullable=False,primary_key=True,autoincrement=True)
    state_name=db.Column(db.String(70),nullable=False)
    
    state_of_patient=db.relationship('Patient',backref='patientstate')
    
class Department(db.Model):
    dept_id=db.Column(db.Integer(),primary_key=True,autoincrement=True)
    dept_name=db.Column(db.String(70),nullable=False)
    
    
    hospdepts=db.relationship('Hospital_Depts',backref='facility')
    deptsappts=db.relationship('Appointment',backref='departmentofappointment')
    staffdepts=db.relationship('Staff',backref='staffdpt')
    
class Hospital_Depts(db.Model):
    hd_id=db.Column(db.Integer(),primary_key=True,autoincrement=True)
    facilityID=db.Column(db.Integer(),db.ForeignKey('hospital.hosp_id'))#fk
    facility_dpt_id=db.Column(db.Integer(),db.ForeignKey('department.dept_id'))#fk


class Hlab(db.Model):
    hlabs_id=db.Column(db.Integer(),primary_key=True,autoincrement=True)
    hlab_hospital_id=db.Column(db.Integer(),db.ForeignKey('hospital.hosp_id'))#fk
    hlab_lab_id=db.Column(db.Integer(),db.ForeignKey('laboratory.lab_id'))#fk
    Hospital_Labs=db.relationship("Laboratory",backref="hosp_lab")
    
class Hospital_Tests(db.Model):
    htest_id=db.Column(db.Integer(),primary_key=True,autoincrement=True)
    hsplab_id=db.Column(db.Integer(),db.ForeignKey('hlab.hlabs_id'))#fk
    htest_test_id=db.Column(db.Integer(),db.ForeignKey('test.test_id'))#fk
    amount=db.Column(db.Float(),nullable=False)
    
    
class Appointment(db.Model):
    appt_id=db.Column(db.Integer(),primary_key=True,autoincrement=True)
    apt_patient_id=db.Column(db.Integer(),db.ForeignKey('patient.patient_id'))
    date_of_appt=db.Column(db.Date(),nullable=False)
    dept_of_appt=db.Column(db.Integer(),db.ForeignKey('department.dept_id'))
    apt_hosp_id=db.Column(db.Integer(),db.ForeignKey('hospital.hosp_id'))
    apt_staff_id=db.Column(db.Integer(),db.ForeignKey('staff.staff_id'))
    purpose=db.Column(db.String(255),nullable=False)
    status=db.Column(db.String(7),nullable=True) #present,absent values can be updated
    
class Consultation(db.Model):
    consult_id=db.Column(db.Integer(),primary_key=True,autoincrement=True)
    con_apt_id=db.Column(db.Integer(),db.ForeignKey('appointment.appt_id')) #fk
    con_patient_id=db.Column(db.Integer(),db.ForeignKey('patient.patient_id')) #fk
    con_hosp_id=db.Column(db.Integer(),db.ForeignKey('hospital.hosp_id')) #fk
    con_staff_id=db.Column(db.Integer(),db.ForeignKey('staff.staff_id')) #fk
    con_dept_id=db.Column(db.Integer(),db.ForeignKey('department.dept_id')) #fk
    patient_complain=db.Column(db.Text(),nullable=False)
    diagnosis=db.Column(db.Text(),nullable=False)
    course_of_action=db.Column(db.Text(),nullable=False)
    
    conappt=db.relationship("Appointment",backref="apptconsults")
    conpatient=db.relationship("Patient",backref="patient_consult")
    con_staff=db.relationship("Staff",backref="staff_consults")
    con_dept=db.relationship("Department",backref="dept_consult")
    con_hosp=db.relationship("Hospital",backref="Hospital_consult")
    
    
    
class Role(db.Model):
    role_id=db.Column(db.Integer(),primary_key=True,autoincrement=True)
    role_name=db.Column(db.String(70),nullable=False)
    staffroles=db.relationship('Staff',backref='staffduty')
    
class Messages(db.Model):
    msg_id=db.Column(db.Integer(),primary_key=True,autoincrement=True)
    sender_staff_id=db.Column(db.Integer(),db.ForeignKey('staff.staff_id')) #fk
    sender_hosp_id=db.Column(db.Integer(),db.ForeignKey('hospital.hosp_id')) #fk
    topic=db.Column(db.String(255),nullable=False)
    message=db.Column(db.Text(),nullable=False)
    date_sent=db.Column(db.Date(),nullable=False,default=datetime.utcnow())
    receiver_staff_id=db.Column(db.Integer(),db.ForeignKey('staff.staff_id')) #fk
    response=db.Column(db.Text(),nullable=True)
    response_date_sent=db.Column(db.Date(),nullable=True)
    
    sender=db.relationship("Staff",backref="staffmsg",foreign_keys=[sender_staff_id])
    recipient=db.relationship("Staff",backref="staffinfo",foreign_keys=[receiver_staff_id])
    sender_facility=db.relationship("Hospital",backref="hospmsgs")
    
class Cross_hospital_Treatment(db.Model):
    CHT_id=db.Column(db.Integer(),primary_key=True,autoincrement=True)
    cht_patient_id=db.Column(db.Integer(),db.ForeignKey('patient.patient_id')) #fk
    cht_hosp_id=db.Column(db.Integer(),db.ForeignKey('hospital.hosp_id')) #fk
    cht_staff_id=db.Column(db.Integer(),db.ForeignKey('staff.staff_id')) #fk
    cht_dept_id=db.Column(db.Integer(),db.ForeignKey('department.dept_id')) #fk
    cht_date_received=db.Column(db.Date(),nullable=False,default=datetime.utcnow())
    patient_complain=db.Column(db.Text(),nullable=False)
    diagnosis=db.Column(db.Text(),nullable=False)
    course_of_action=db.Column(db.Text(),nullable=False)
    
    
    CHT_patient=db.relationship("Patient",backref="patient_cht_cases")
    cht_staff=db.relationship("Staff",backref="staff_cht_cases")
    cht_dept=db.relationship("Department",backref="dept_cht-cases")
    cht_hosp=db.relationship("Hospital",backref="hospital_cht-cases")
    

class Surgery(db.Model):
    surg_id=db.Column(db.Integer(),primary_key=True,autoincrement=True)
    surg_patient_id=db.Column(db.Integer(),db.ForeignKey('patient.patient_id'))#FK
    date_of_surg=db.Column(db.Date(),nullable=False)
    lead_surgeon_staff_id=db.Column(db.Integer(),db.ForeignKey('staff.staff_id'))#fk
    procedure_name=db.Column(db.String(255),nullable=False)
    dept_of_surg=db.Column(db.Integer(),db.ForeignKey('department.dept_id'))#fk
    surg_hosp_id=db.Column(db.Integer(),db.ForeignKey('hospital.hosp_id'))#fk
    test_results=db.Column(db.String(255),nullable=True)
    status=db.Column(db.Enum('Pending', 'Present', 'Missed'), nullable=True, default="Pending")
    
    surgeon_deets=db.relationship("Staff",backref="surgeon_surgeries")
    
    