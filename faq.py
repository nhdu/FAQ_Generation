from xml.dom import ValidationErr
from flask import Flask, render_template, session, redirect, url_for, flash
from flask_navigation import Navigation
from api.amazon_review import AmazonAPI
from api.twitter_feeds import TwitterFeeds
from forms.input_form import AmazonForm, TwitterForm, FileUploadForm, LoginForm, RegisterForm
from model.T5_base_question_gen import T5Model
from model.questGen import QuestGen
from model.textsimilarity import TextSimilarity
from itertools import chain
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
import os
import pandas as pd

ALLOWED_EXTENSIONS = {'xlsx'}
app = Flask(__name__, template_folder='template')
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:\\Users\\duong\\Desktop\\gita2i2\\automaticFAQ_NHAT\\databases\\db.sqlite3'
app.config['SECRET_KEY'] = "mykey"
app.config['UPLOAD_FOLDER'] ='static/uploaded_files'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "index"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def validate_username(username):
    existing_username = User.query.filter_by(username=username).first()
    return existing_username
    


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False, unique=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('amazon_inputs'))
    return render_template("index.html", form=form)

@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    
    if form.validate_on_submit():
        if (validate_username(form.username.data)):
            flash('The provided username already exists. Please choose a different one.', 'duplicate_username')
            return render_template('register.html', form=form)
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('register.html', form=form)    

@app.route('/logout', methods=["POST", "GET"])
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/amazon_inputs', methods=["GET", "POST"])
@login_required
def amazon_inputs():
    form = AmazonForm()
    if form.validate_on_submit():
        session["pages"] = form.pages.data
        session["asin"] = form.asin.data
        session["country"] = form.country.data
        session["variants"] = form.variants.data
        session["top"] = form.top.data
        return redirect(url_for("amazon"))
    return render_template('amazon_inputs.html', form = form)

@app.route('/twitter_input', methods=["GET", "POST"])
@login_required
def twitter_input():
    form = TwitterForm()
    if form.validate_on_submit():
        session["num_tweets"] = form.numTweets.data
        session["query"] = form.query.data
        return redirect(url_for("twitter"))
    return render_template('twitter_inputs.html', form =  form)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload_file', methods=["GET", "POST"])
@login_required
def upload_file():
    form = FileUploadForm()
    if form.validate_on_submit():
        file_upload = form.file.data
        if (allowed_file(file_upload.filename)):
            file_secure_name = secure_filename(file_upload.filename)
            file_upload.save(os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'], file_secure_name))
            session["path"] = os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'], file_secure_name)
            return redirect(url_for("corpus"))
        else:
            flash('Only accepts .xlsx format', 'input_format_error')
    return render_template('file_upload_inputs.html', form = form)
        

@app.route('/amazon')
@login_required
def amazon():
    api = AmazonAPI()
    reviews = api.get_reviews(session["pages"], session["asin"], session["country"], session["variants"], session["top"])
    print(reviews)
    model = QuestGen()
    questions = []
    answers = []
    questionable_reviews = []
    for item in reviews:
        result = model.get_questions(item)
        if (len(result[0]) == 0): 
            continue
        print(result)
        questionable_reviews.append(item)
        questions.append(result[0])
        answers.append(result[1])
        
    frequency_rank = TextSimilarity()
    rank = frequency_rank.get_similarity_matrix(list(chain.from_iterable(questions)))
    faq_list_amazon = frequency_rank.get_faq_list(list(chain.from_iterable(questions)), rank, list(chain.from_iterable(answers)))
    print(faq_list_amazon)
       
    # questions[:] = [question.replace("<pad> question: ", "") for question in questions]
    # questions[:] = [question.replace("</s>", "") for question in questions]
    
    session["reviews"] = questionable_reviews
    session["questions"] = questions
    session["answers"] = answers
    session["faq_amazon"] = faq_list_amazon
    
    return render_template('amazon.html', reviews = session["reviews"], questions = session["questions"], answers = session["answers"], faq_list = session["faq_amazon"], zip = zip)

@app.route('/twitter')
@login_required
def twitter():
    tweets_API = TwitterFeeds()
    feeds = tweets_API.get_feeds(session["query"], session["num_tweets"])
    model = QuestGen()
    questions = []
    answers = []
    questionable_feeds = []
    for item in feeds:
        result = model.get_questions(item)
        if (len(result[0]) == 0):
            print("THIS REVIEW HAS ZERO QUESTION" + item)
            continue
        print(result)
        questionable_feeds.append(item)
        questions.append(result[0])
        answers.append(result[1])
        
    frequency_rank = TextSimilarity()
    rank = frequency_rank.get_similarity_matrix(list(chain.from_iterable(questions)))
    faq_list_twitter = frequency_rank.get_faq_list(list(chain.from_iterable(questions)), rank, list(chain.from_iterable(answers)))
    print(faq_list_twitter)
    
    # questions[:] = [question.replace("<pad> question: ", "") for question in questions]
    # questions[:] = [question.replace("</s>", "") for question in questions]
    session["twitter_feeds"] = questionable_feeds
    session["questions_twitter"] = questions
    session["answers_twitter"] = answers
    session["faq_twitter"] = faq_list_twitter
    return render_template('twitter.html', feeds = session["twitter_feeds"], questions_twitter = session["questions_twitter"], answers_twitter = session["answers_twitter"], faq_list = session["faq_twitter"], zip = zip)

@app.route('/corpus')
@login_required
def corpus():
    dataframe = pd.read_excel(session["path"])
    error = False
    if (len(dataframe.columns) == 0 or len(dataframe.columns) > 1):
        flash('Only accepts files with 1 column', 'input_format_error')
        error = True
    if ("Amazon Reviews" not in dataframe.columns and "Twitter Feeds" not in dataframe.columns):
        flash('There is no \"Amazon Reviews \" or \"Twitter Feeds\" column in the uploaded file', 'input_format_error')
        error = True
    if (error):
        return render_template('file_upload_inputs.html')
        
    if ("Amazon Reviews" in dataframe.columns):
        uploaded_data = list(dataframe["Amazon Reviews"])
    elif ("Twitter Feeds" in dataframe.columns):
        uploaded_data = list(dataframe["Twitter Feeds"])
    
    model = QuestGen()
    questions = []
    answers = []
    questionable_data = []
    for item in uploaded_data:
        result = model.get_questions(item)
        if (len(result[0]) == 0):
            print("THIS REVIEW HAS ZERO QUESTION" + item)
            continue
        print(result)
        questionable_data.append(item)
        questions.append(result[0])
        answers.append(result[1])
        
    frequency_rank = TextSimilarity()
    rank = frequency_rank.get_similarity_matrix(list(chain.from_iterable(questions)))
    faq_list_upload = frequency_rank.get_faq_list(list(chain.from_iterable(questions)), rank, list(chain.from_iterable(answers)))
    print(faq_list_upload)
    
    # questions[:] = [question.replace("<pad> question: ", "") for question in questions]
    # questions[:] = [question.replace("</s>", "") for question in questions]
    session["upload_data"] = questionable_data
    session["questions_upload"] = questions
    session["answers_upload"] = answers
    session["faq_upload"] = faq_list_upload
    return render_template('file_upload.html', uploads = session["upload_data"], questions_upload = session["questions_upload"], answers_upload = session["answers_upload"], faq_list = session["faq_upload"], zip = zip)        
              
if __name__ == '__main__':
    app.run(debug=True) 