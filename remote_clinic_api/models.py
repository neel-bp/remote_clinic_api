from remote_clinic_api import db
<<<<<<< HEAD
from mongoengine import StringField, EmailField, DateTimeField, BooleanField, DictField, EmbeddedDocument, EmbeddedDocumentField, Document, FloatField, ReferenceField, ObjectIdField, EmbeddedDocumentListField, GenericReferenceField
=======
from mongoengine import StringField, EmailField, DateTimeField, BooleanField, DictField, EmbeddedDocument, EmbeddedDocumentField, Document, FloatField, ReferenceField, ObjectIdField, EmbeddedDocumentListField, ListField
>>>>>>> 4038889a35acd8478d1adee81bff5e17c6c7679b


from marshmallow_mongoengine import ModelSchema
from datetime import datetime

class Address(EmbeddedDocument):
    latitude = FloatField()
    longitude = FloatField()
    country = StringField()
    city = StringField()
    street = StringField()

class AddressSchema(ModelSchema):
    class Meta:
        model = Address

class Patient(db.Document):
    username = StringField()
    password = StringField()
    name = StringField()
    surname = StringField()
    email = EmailField()
    phone = StringField()
    gender = StringField()
    image_path = StringField()
    signup_date = DateTimeField(default=datetime.utcnow)
    online = BooleanField()
    address = EmbeddedDocumentField(Address)


# defining schema for json serialization
class PatientSchema(ModelSchema):
    class Meta:
        model = Patient




class Drug(EmbeddedDocument):
    name = StringField()
    dose = StringField()
    time = StringField()
    description = StringField()

class DrugSchema(ModelSchema):
    class Meta:
        model = Drug



class Reports(db.Document):
    title = StringField()
    report_type = StringField()
    description = StringField()
    issued_by_org = StringField()
    issued_date = DateTimeField(default=datetime.utcnow)
    file_path = StringField()
    report_of = ReferenceField('Patient')

class ReportSchema(ModelSchema):
    class Meta:
        model = Reports

class Operator(db.Document):
    name = StringField()
    surname = StringField()
    phone = StringField()
    dob = DateTimeField()
    email = EmailField()
    address = EmbeddedDocumentField(Address)
    password = StringField()
    doj = DateTimeField()


# defining schema for json serialization
class OperatorSchema(ModelSchema):
    class Meta:
        model = Operator


class Doctor(db.Document):
    name = StringField(max_length=255, required=True)
    surname = StringField(max_length=255, required=True)
    email = EmailField(required=True)
    password = StringField(required=True)
    tags = ListField(StringField(), default=list) # List of String TAGS 
    phone = StringField(max_length=255)
    gender = StringField(max_length=32,required=True)
    address = EmbeddedDocumentField(Address)
    image_path = StringField()
    signup_date = DateTimeField(default=datetime.utcnow)
    online = BooleanField(default=False)
    specialization = StringField(max_length=255,required=True)
    about = StringField(max_length=255,required=True)
<<<<<<< HEAD
    experience = StringField()
    pmdc_verified = BooleanField(default=False)
    pmdc_reg_num = StringField()
    verification_status = StringField(default='Pending')
    verified_by = ReferenceField('Operator')
=======
    experience = StringField(max_length=255)
    pmdc_verified = BooleanField(required=True)
    pmdc_reg_num = StringField(required=True)
    verification_status = StringField(required=True)
    verified_by = ObjectIdField()
>>>>>>> 4038889a35acd8478d1adee81bff5e17c6c7679b
    verification_date = DateTimeField()

# defining schema for json serialization
class DoctorSchema(ModelSchema):
    class Meta:
        model = Doctor

## patient prescriptions
class Prescription(db.Document):
    prescribed_by = StringField()
    doctor_id = ReferenceField('Doctor') 
    notes = StringField()
    drugs = EmbeddedDocumentListField(Drug)
    prescription_date = DateTimeField(datetime.utcnow)
    prescribed_for = ReferenceField('Patient')

class PrescriptionSchema(ModelSchema):
    class Meta:
        model = Prescription

# patient interactions with doctors
class Interaction(db.Document):
    patient_id = ReferenceField('Patient')
    doctor_id = ReferenceField('Doctor')
    doctor_name = StringField()
    medium = StringField()
    date = DateTimeField(default=datetime.utcnow)
    interaction_type = StringField() # didnt use type because type is a reserved word in python

class InteractionSchema(ModelSchema):
    class Meta:
        model = Interaction



class DDocuments(db.Document):
    owner = ReferenceField('Doctor', required=True)
    title = StringField(max_length=255, required=True)
    document_type = StringField(max_length=64, required=True)
    description = StringField(max_length=255, required=True)
    issued_by_org = StringField(max_length=255, required=True)
    issued_date = DateTimeField(default=datetime.utcnow)
    img_path = StringField()
    verification_status = StringField(max_length=64, required=True)
    verified_by = ReferenceField('Operator')
    verification_date = DateTimeField()
    rejection_cause = StringField()

# defining schema for json serialization
class DDcoumentsSchema(ModelSchema):
    class Meta:
        model = DDocuments  

<<<<<<< HEAD
class Reviews(db.Document):
    rating = FloatField(max_value=5)
    review_by = GenericReferenceField() # Reviewer could be any
    reviewer_name = StringField(max_length=255)
    review_for = GenericReferenceField() # Reviewed For could be any
    for_name = StringField(max_length=255)
    review_date = DateTimeField(default=datetime.utcnow)
    comment = StringField()
=======
class Operator(Document):
    name = StringField(max_length=255, required=True)
    surname = StringField(max_length=255)
    phone = StringField(max_length=255)
    avatar = StringField()
    dob = DateTimeField()
    email = EmailField(unique=True, required=True)
    address = DictField()
    password = StringField(required=True)
    doj = DateTimeField(default=datetime.utcnow)

>>>>>>> 4038889a35acd8478d1adee81bff5e17c6c7679b

class ReviewsSchema(ModelSchema):
    class Meta:
<<<<<<< HEAD
        model = Reviews
=======
        model = Operator


class Permissions(EmbeddedDocument):
    title = StringField(required=True)

# defining schema for json serialization
class PermisstionSchema(ModelSchema):
    class Meta:
        model = Permissions


# Note: One Role can have multiple permissions: one to many relationship
# Note: When creating new Role permissions should be already defined.
class Roles(Document):
    title = StringField(required=True)
    permissions = EmbeddedDocumentListField(Permissions, required=True) # List of permissions


# defining schema for json serialization
class RolesSchema(ModelSchema):
    class Meta:
        model = Roles

# Note: One Operator have one Role - one to one relationship.
class OperatorRoles(Document):
    operator = ObjectIdField(required=True)
    role = ObjectIdField(required=True)


# defining schema for json serialization
class OperatorRolesSchema(ModelSchema):
    class Meta:
        model = OperatorRoles


>>>>>>> 4038889a35acd8478d1adee81bff5e17c6c7679b
