# import packgaes
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

load_dotenv() ## LOAD THIS COMMAND FIRST

mysql_username = os.getenv("MYSQL_USERNAME")
mysql_password = os.getenv("MYSQL_PASSWORD")
mysql_host = os.getenv("MYSQL_HOST")

db = SQLAlchemy()
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqldb://' + mysql_username + ':' + mysql_password + '@' + mysql_host + ':3306/patient_portal'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'sdf#$#dfjkhdf0SDJH0df9fd98343fdfu34rf'

db.init_app(app)


### Models ###
class Patients(db.Model):
    __tablename__ = 'patients'

    id = db.Column(db.Integer, primary_key=True)
    mrn = db.Column(db.String(255))
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    dob = db.Column(db.String(255), nullable=True)
    zip_code = db.Column(db.String(255), nullable=True)
    gender = db.Column(db.String(255), nullable=True)
    contact_mobile = db.Column(db.String(255), nullable=True)
    contact_home = db.Column(db.String(255), nullable=True)
    


    # this first function __init__ is to establish the class for python GUI
def __init__(self, mrn, first_name, last_name, zip_code, dob, gender, contact_mobile, contact_home):
        self.mrn = mrn
        self.first_name = first_name
        self.last_name = last_name
        self.zip_code = zip_code
        self.dob = dob
        self.gender = gender
        self.contact_mobile = contact_mobile
        self.contact_home = contact_home
     

    # this second function is for the API endpoints to return JSON 
def to_json(self):
        return {
            'id': self.id,
            'mrn': self.mrn,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'zip_code': self.zip_code,
            'dob': self.dob,
            'gender': self.gender,
            'contact_mobile': self.contact_mobile,
            'contact_home': self.contact_home
        }


class Medications_patient(db.Model):
    __tablename__ = 'patient_medications'

    id = db.Column(db.Integer, primary_key=True)
    mrn = db.Column(db.String(255), db.ForeignKey('patients.mrn'))
    med_ndc = db.Column(db.String(255), db.ForeignKey('prod_medications.med_ndc'))

    # this first function __init__ is to establish the class for python GUI
    def __init__(self, mrn, med_ndc):
        self.mrn = mrn
        self.med_ndc = med_ndc

    # this second function is for the API endpoints to return JSON
    def to_json(self):
        return {
            'id': self.id,
            'mrn': self.mrn,
            'med_ndc': self.med_ndc
        }
    
class Medications(db.Model):
    __tablename__ = 'prod_medications'

    id = db.Column(db.Integer, primary_key=True)
    med_ndc = db.Column(db.String(255))
    med_human_name = db.Column(db.String(255))

    # this first function __init__ is to establish the class for python GUI
    def __init__(self, med_ndc, med_human_name):
        self.med_ndc = med_ndc
        self.med_human_name = med_human_name

    # this second function is for the API endpoints to return JSON
    def to_json(self):
        return {
            'id': self.id,
            'med_ndc': self.med_ndc,
            'med_human_name': self.med_human_name
        }

class Procedure_patient(db.Model):
    __tablename__ = 'patient_procedure'

    id = db.Column(db.Integer, primary_key=True)
    mrn = db.Column(db.String(255), db.ForeignKey('patients.mrn'))
    proc_cpt = db.Column(db.String(255), db.ForeignKey('treatment_procedure.proc_cpt'))

    # this first function __init__ is to establish the class for python GUI
    def __init__(self, mrn, proc_cpt):
        self.mrn = mrn
        self.proc_cpt = proc_cpt

    # this second function is for the API endpoints to return JSON
    def to_json(self):
        return {
            'id': self.id,
            'mrn': self.mrn,
            'proc_cpt': self.proc_cpt
        }

class Procedure(db.Model):
    __tablename__ = 'treatment_procedure'

    id = db.Column(db.Integer, primary_key=True)
    proc_cpt = db.Column(db.String(255))
    proc_desc = db.Column(db.String(255))

    # this first function __init__ is to establish the class for python GUI
    def __init__(self, proc_cpt, proc_desc):
        self.proc_cpt = proc_cpt
        self.proc_desc = proc_desc

    # this second function is for the API endpoints to return JSON
    def to_json(self):
        return {
            'id': self.id,
            'proc_cpt': self.proc_cpt,
            'proc_desc': self.proc_desc
        }


#### BASIC ROUTES WITHOUT DATA PULSL FOR NOW ####
@app.route('/')
def index():
    return render_template('landing.html')

@app.route('/signin')
def signin():
    return render_template('/signin.html')



##### CREATE BASIC GUI FOR CRUD #####
@app.route('/patients', methods=['GET'])
def get_gui_patients():
    returned_Patients = Patients.query.all() # documentation for .query exists: https://docs.sqlalchemy.org/en/14/orm/query.html
    return render_template("patient_all.html", patients = returned_Patients)

# this endpoint is for inserting in a new patient
@app.route('/insert', methods = ['POST'])
def insert(): # note this function needs to match name in html form action 
    if request.method == 'POST':
        mrn = request.form['mrn']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        zip_code = request.form['zip_code']
        dob = request.form['dob']
        gender = request.form['gender']
        contact_mobile = request.form['contact_mobile']
        contact_home = request.form['contact_home']
        new_patient = Patients(mrn, first_name, last_name,
                               zip_code, dob, gender, contact_mobile, contact_home)
        db.session.add(new_patient)
        db.session.commit()
        flash("Patient Inserted Successfully")
        return redirect(url_for('get_gui_patients'))
    else:
        flash("Something went wrong")
        return redirect(url_for('get_gui_patients'))

# this endpoint is for updating our patients basic info 
@app.route('/update', methods = ['GET', 'POST'])
def update(): # note this function needs to match name in html form action
    if request.method == 'POST':
        ## get mrn from form
        form_mrn = request.form.get('mrn')
        patient = Patients.query.filter_by(mrn=form_mrn).first()
        patient.first_name = request.form.get('first_name')
        patient.last_name = request.form.get('last_name')
        patient.gender = request.form.get('gender')
        db.session.commit()
        flash("Patient Updated Successfully")
        return redirect(url_for('get_gui_patients'))

#This route is for deleting our patients
@app.route('/delete/<string:mrn>', methods = ['GET', 'POST'])
def delete(mrn): # note this function needs to match name in html form action
    patient = Patients.query.filter_by(mrn=mrn).first()
    print('Found patient: ', patient)
    db.session.delete(patient)
    db.session.commit()
    flash("Patient Deleted Successfully")
    return redirect(url_for('get_gui_patients'))


#This route is for getting patient details
@app.route('/details/<string:mrn>', methods = ['GET'])
def get_patient_details(mrn):
    patient_details = Patients.query.filter_by(mrn=mrn).first()
    patient_medications = Medications_patient.query.filter_by(mrn=mrn).all()
    patient_procedure = Procedure_patient.query.filter_by(mrn=mrn).all()


    db_medications = Medications.query.all()
    db_procedures = Procedure.query.all()
    return render_template("patient_details.html", patient_details = patient_details, patient_medications = patient_medications, patient_procedure = patient_procedure, db_medications = db_medications, db_procedures = db_procedures)




@app.route('/update_medications', methods=['GET', 'POST'])
def update_medications():  # note this function needs to match name in html form action
    if request.method == 'POST':
        # get mrn from form
        form_id = request.form.get('id')
        print('form_id', form_id)
        form_med_ndc = request.form.get('med_ndc')
        print('form_med_ndc', form_med_ndc)
        patients_medications = Medications_patient.query.filter_by(
            id=form_id).first()
        print('patients_medications', patients_medications)
        patients_medications.med_ndc = request.form.get('med_ndc')
        db.session.commit()
        flash("Patient Medication Updated Successfully")
        # then return to patient details page
        return redirect(url_for('get_patient_details', mrn=patients_medications.mrn))


@app.route('/update_procedures', methods=['GET', 'POST'])
def update_procedures():  # note this function needs to match name in html form action
    if request.method == 'POST':
        # get mrn from form
        form_id = request.form.get('id')
        print('form_id', form_id)
        form_proc_cpt = request.form.get('proc_cpt')
        print('form_proc_cpt', form_proc_cpt)
        patient_procedure = Procedure_patient.query.filter_by(
            id=form_id).first()
        print('patient_procedure', patient_procedure)
        patient_procedure.proc_cpt = request.form.get('proc_cpt')
        db.session.commit()
        flash("Patient Procedure Updated Successfully")
        # then return to patient details page
        return redirect(url_for('get_patient_details', mrn=patient_procedure.mrn))





##### CREATE BASIC API ENDPOINTS #####
# get all Patients
@app.route("/api/patients/list", methods=["GET"])
def get_patients():
    patients = Patients.query.all()
    return jsonify([patient.to_json() for patient in patients])

# get specific Patient by MRN 
@app.route("/api/patients/<string:mrn>", methods=["GET"])
def get_patient(mrn):
    ## get patient by mrn column
    patient = Patients.query.filter_by(mrn=mrn).first()
    if patient is None:
        abort(404)
    return jsonify(patient.to_json())

##### BASIC POST ROUTES ##### [isnert new data into the database]
# new patient 
@app.route('/api/patient', methods=['POST'])
def create_patient():
    if not request.json:
        abort(400)
    patient = Patients(
        mrn=request.json.get('mrn'),
        first_name=request.json.get('first_name'),
        last_name=request.json.get('last_name'),
        zip_code=request.json.get('zip_code'),
        dob=request.json.get('dob'),
        gender=request.json.get('gender'),
        contact_mobile=request.json.get('contact_mobile'),
        contact_home=request.json.get('contact_home')
    )
    db.session.add(patient)
    db.session.commit()
    return jsonify(patient.to_json()), 201

##### BASIC PUT ROUTES ##### [updating existing data]
# update patient 
@app.route('/api/patient/<string:mrn>', methods=['PUT'])
def update_patient(mrn):
    if not request.json:
        abort(400)
    patient = Patients.query.filter_by(mrn=mrn).first()
    if patient is None:
        abort(404)
    patient.first_name = request.json.get('first_name', patient.first_name)
    patient.last_name = request.json.get('price', patient.last_name)
    db.session.commit()
    return jsonify(patient.to_json())


##### BASIC DELETE ROUTES #####
# delete patient
@app.route("/api/patient/<string:mrn>", methods=["DELETE"])
def delete_patient(mrn):
    patient = Patients.query.filter_by(mrn=mrn).first()
    if patient is None:
        abort(404)
    db.session.delete(patient)
    db.session.commit()
    return jsonify({'result': True})










if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
