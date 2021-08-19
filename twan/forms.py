from flask_wtf import FlaskForm
from wtforms import validators, StringField, DateField, SubmitField, SelectField
from wtforms.fields.core import IntegerField
from wtforms.validators import ValidationError
from wtforms.validators import Length, DataRequired, ValidationError
from datetime import datetime, timedelta

class SearchInputForm(FlaskForm):
    
    def validate_enddate(form, field):
        if field.data < form.startdate.data:
            raise ValidationError("End date must not be earlier than start date.")

    search_text = StringField(label='Enter Search Text Here:', validators=[Length(min=2, max=300), DataRequired()])
    startdate = DateField('Start Date', format='%Y-%m-%d', default=(datetime.today() - timedelta(days=3)) , validators=(DataRequired(),))
    enddate = DateField('End Date', format='%Y-%m-%d', default=datetime.today(), validators=(DataRequired(),))
    max_tweets = IntegerField(label='Maximum tweet count to be collected:', default=10000, validators=[DataRequired()])
    lang = SelectField(u'Select Language', choices=[('en', 'English'), ('tr', 'Turkish')] )
    submit = SubmitField(label='Collect Tweets')


class TargetWordsForm(FlaskForm):
    target_words = StringField(label='Enter Target Words Here as Comma Seperated:', validators=[Length(min=2, max=300), DataRequired()])
    word_count2keep = IntegerField(label='Enter Number of Words for Correlation Computation:', default=10, validators=[DataRequired()])
    submit = SubmitField(label='Compute Correlation with Target Words')

class SentimentForm(FlaskForm):
    submit = SubmitField(label='Start Sentiment Analysis')

class WordCoocForm(FlaskForm):
    top_n_words = IntegerField(label='Enter Number of Words for Co-occurence Analysis:', default=20, validators=[DataRequired()])
    submit = SubmitField(label='Start Word Co-occurance Analysis')

class EmailDownloadForm(FlaskForm):
    email = StringField(label='Enter Your Email:', validators=[DataRequired(), validators.Email()])
    submit = SubmitField(label='Sent download link')