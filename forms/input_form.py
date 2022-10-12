from wsgiref.validate import validator
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, RadioField, FileField, PasswordField
from wtforms.validators import DataRequired, NumberRange, InputRequired, Length 

class AmazonForm(FlaskForm):
    pages = IntegerField("Number of review pages: ", validators=[DataRequired(), NumberRange(min=1)])
    asin = StringField(u"Product\'s ASIN number: ", validators=[DataRequired()])
    country = StringField(u"Amazon marketplace country code: ", validators=[DataRequired()])
    variants = RadioField("Please choose a review type: ", 
                          choices=[("0", "Only reviews for the specified product ASIN"), 
                                   ("1", "Reviews for all product variants")], validators=[DataRequired()])
    top = RadioField("Please choose a review sorting method", 
                     choices=[("0", "Reviews sorted by Most recent"), 
                              ("1", "Reviews sorted by Top review")], validators=[DataRequired()])
    submit = SubmitField("Submit")

class TwitterForm(FlaskForm):
    numTweets = IntegerField("Number of tweets: ", validators=[DataRequired(), NumberRange(min=1)])
    query = StringField(u"Search query: ", validators=[DataRequired()])
    submit = SubmitField("Submit")
    
class FileUploadForm(FlaskForm):
    file = FileField("Corpus of feeds or reviews: ", validators=[InputRequired()])
    submit = SubmitField("Submit")
    

class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField("Register")
    
    
class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField("Login")
