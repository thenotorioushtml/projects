from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from vsapp.models import User
from flask_login import current_user

# The registration form and the requirements for each field during the registration
class RegistrationForm(FlaskForm):
    email = StringField(label='Email', validators=[DataRequired(), Email()])
    username = StringField(label='Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField(label='Password', validators=[DataRequired()])
    confirm_password = PasswordField(label='Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(label='Sign Up')
    
    # checks if the username is already used
    def validate_username(self, username):
        user = User.query.filter_by(username = username.data).first()
        if user:
            raise ValidationError('The useranme already exists')
    
    # checks if the email is already used
    def validate_email(self, email):
        user = User.query.filter_by(email = email.data).first()
        if user:
            raise ValidationError('The account already exists')
    
# The login is done by using the username instead of the email    
class LoginForm(FlaskForm):
    username = StringField(label='Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField(label='Password', validators=[DataRequired()])
    remember = BooleanField(label='Remember Me')
    submit = SubmitField(label='Login')
    
# Update the profile picture and the username
class UpdateAccountForm(FlaskForm):
    username = StringField(label='Username', validators=[DataRequired(), Length(min=2, max=20)])
    submit = SubmitField(label='Update')
    picture = FileField('Change Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    
    # checks if the username is already used
    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username = username.data).first()
            if user:
                raise ValidationError('The useranme already exists')

# Form fot the posts
class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content =  FileField('Upload Post Picture', validators=[FileAllowed(['jpg', 'png']), DataRequired()])
    public = BooleanField('Public', default=True)
    submit = SubmitField('Post')