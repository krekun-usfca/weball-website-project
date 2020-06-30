from flask_login import UserMixin
from flask_wtf import FlaskForm
from werkzeug.security import check_password_hash, generate_password_hash
from wtforms import IntegerField, PasswordField, SelectField, \
    StringField, SubmitField, TextAreaField, BooleanField
from wtforms.fields.html5 import DateField, TimeField
from wtforms.validators import ValidationError, DataRequired, NumberRange, EqualTo
from wtforms.fields.html5 import DateField, TimeField
from app import db, login_manager
from app.user_def import apikey
import calendar
from datetime import datetime
import urllib
import simplejson
import pandas as pd
from sqlalchemy import or_, ForeignKey
from sqlalchemy.orm import relationship


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80),
                         unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    # preference = relationship('Preference')

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.set_password(password)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Preference(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(80))
    skill = db.Column(db.String(80))
    feet = db.Column(db.Integer)
    inches = db.Column(db.Integer)
    height = db.Column(db.Float(4))
    address = db.Column(db.String(80))
    city = db.Column(db.String(80))
    state = db.Column(db.String(2))
    zipcode = db.Column(db.String(5))
    court_type = db.Column(db.String(80))

    def __init__(self, username, age, gender, skill, feet, inches, height,
                 address, city, state, zipcode, court_type):
        self.age = age
        self.gender = gender
        self.skill = skill
        self.feet = feet
        self.inches = inches
        self.height = height
        self.address = address
        self.city = city
        self.state = state
        self.zipcode = zipcode
        self.court_type = court_type
        self.username = username


class Court:
    def __init__(self, court_name, distance, duration, rating, num_reviews,
                 indoor_outdoor, lat, long, link):
        self.court_name = court_name
        self.distance = distance
        self.duration = duration
        self.rating = rating
        self.num_reviews = num_reviews
        self.indoor_outdoor = indoor_outdoor
        self.lat = lat
        self.long = long
        self.link = link


class CourtInformation(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    court_id = db.Column(db.String(100))
    court_name = db.Column(db.String(100))
    rating = db.Column(db.Float)
    review_count = db.Column(db.Integer)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    address = db.Column(db.String(100))
    city = db.Column(db.String(100))
    zip_code = db.Column(db.String(5))
    country = db.Column(db.String(2))
    state = db.Column(db.String(2))
    display_address = db.Column(db.String(100))
    indoor_outdoor = db.Column(db.String(10))
    has_lights = db.Column(db.Boolean)
    private_public = db.Column(db.String(10))

    def __init__(self, court_id, court_name, rating, review_count,
                 latitude, longitude, address, city, zip_code, country, state,
                 display_address, indoor_outdoor, has_lights, private_public):
        self.court_id = court_id
        self.rating = rating
        self.review_count = review_count
        self.latitude = latitude
        self.longitude = longitude
        self.address = address
        self.city = city
        self.zip_code = zip_code
        self.country = country
        self.state = state
        self.display_address = display_address
        self.indoor_outdoor = indoor_outdoor
        self.has_lights = has_lights
        self.private_public = private_public
        self.court_name = court_name


class CourtAvailabilityHours(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    court_name = db.Column(db.String(100))
    day_of_week = db.Column(db.String(100))
    time_12hr = db.Column(db.String(100))
    availability_value = db.Column(db.Integer)
    availability_description = db.Column(db.String(100))

    def __init__(self, court_name, day_of_week, time12_hr,
                 availability_value, availability_description):
        self.day_of_week = day_of_week
        self.time_12hr = time12_hr
        self.availability_value = availability_value
        self.availability_description = availability_description
        self.court_name = court_name


class CourtTimings(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    court_name = db.Column(db.String(100))
    day_of_week = db.Column(db.String(20))
    hours = db.Column(db.String(30))
    open = db.Column(db.Integer)
    close = db.Column(db.Integer)

    def __init__(self, court_name, day_of_week, hours, open, close):
        self.day_of_week = day_of_week
        self.hours = hours
        self.open = open
        self.close = close
        self.court_name = court_name


class Match:
    def __init__(self, court_name, link, game_date, game_time, max_players,
                 skill_level, current_players, distance, game_id, username,
                 players, create_or_join):
        self.court_name = court_name
        self.game_date = game_date
        self.game_time = game_time
        self.link = link
        self.max_players = max_players
        self.skill_level = skill_level
        self.current_players = current_players
        self.distance = distance
        self.game_id = game_id
        self.username = username
        self.players = players
        self.create_or_join = create_or_join


class ScheduledGames(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer)
    username = db.Column(db.String(80), nullable=False) # creator of the game
    game_date = db.Column(db.DateTime)
    game_time = db.Column(db.String(20))
    skill_level = db.Column(db.String(20))
    max_players = db.Column(db.Integer)
    current_players = db.Column(db.Integer)
    court_name = db.Column(db.String(100), nullable=True)
    players = db.Column(db.String(100)) # players of the game(indcluding players enter by join)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    create_or_join = db.Column(db.Integer)

    def __init__(self, game_id, username, game_date, game_time, skill_level,
                 max_players, current_players, court_name, players, create_or_join):
        self.game_id = game_id
        self.username = username
        self.game_date = game_date
        self.game_time = game_time
        self.skill_level = skill_level
        self.max_players = max_players
        self.current_players = current_players
        self.court_name = court_name
        self.players = players
        self.create_or_join = create_or_join
        self.latitude = db.session.query(CourtInformation.latitude).\
            filter(CourtInformation.court_name == self.court_name).first()[0]
        self.longitude = db.session.query(CourtInformation.longitude). \
            filter(CourtInformation.court_name == self.court_name).first()[0]


class RegistrationForm(FlaskForm):
    username = StringField(label='Username:', validators=[DataRequired()])
    email = StringField(label='Email:', validators=[DataRequired()])
    password = PasswordField(label='Password:', validators=[DataRequired()])
    confirm_password = PasswordField(label='Confirm Password:',
                                     validators=[DataRequired(), EqualTo('password')])
    over_18 = BooleanField(label='I verify that I am over the age of 18',
                           validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class LogInForm(FlaskForm):
    username = StringField(label='Username:', validators=[DataRequired()])
    password = PasswordField(label='Password:', validators=[DataRequired()])
    submit = SubmitField('Login')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is None:
            raise ValidationError('Invalid username.')

    def validate_password(self, password):
        user = User.query.filter_by(username=self.username.data).first()
        if user is not None and not check_password_hash(user.password_hash, password.data):
            raise ValidationError('Invalid password.')


class FindCourtForm(FlaskForm):
    location = StringField('Location', validators=[DataRequired()])
    cities = ["Emeryville", "Oakland", "El Cerrito", "Alameda",
              "Kensington", "Berkeley", "Albany", "San Francisco",
              "Sausalito", "Millbrae", "Mill Valley",
              "South San Francisco", "San Bruno", "Daly City",
              "Brisbane","Pacifica"]

    city_choices = [(city, city) for city in cities]
    city = SelectField('City', validators=[DataRequired()], choices=city_choices)

    submit = SubmitField("Submit")


class UpdateProfileForm(FlaskForm):
    age = SelectField(label='Age:', choices=[(None, ' ')] + [(str(a), str(a)) for a in range(18, 120)],
                      validators=[DataRequired()])

    gender_choices = ['female', 'male', 'non-binary']
    gender = SelectField(label='Gender:',  choices=[(None, '')] + [(g, g) for g in gender_choices],
                        validators=[DataRequired()])

    skill_choices = ['beginner', 'intermediate', 'experienced', 'advanced']
    skill = SelectField(label=u'Basketball Skill Level:',
                        choices=[(None, '')] + [(s, s) for s in skill_choices],
                        validators=[DataRequired()])

    feet = SelectField(label='feet', choices=[(None, ' ')] + [(str(f), str(f)) for f in range(1, 10)],
                       validators=[DataRequired()])

    inches = SelectField(label='inches', choices=[(None, ' ')] + [(str(i), str(i)) for i in range(12)],
                         validators=[DataRequired()])

    address = StringField(label='Address:', validators=[DataRequired()])

    city = StringField(label='City:', validators=[DataRequired()])

    # Probably needs to be changed
    states = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
              'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
              'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
              'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
              'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY']
    state = SelectField(label='State', choices=[(None, ' ')] + [(s, s) for s in states], validators=[DataRequired()])

    zipcode = IntegerField(label="Zip Code:", validators=[DataRequired()])

    court_type_choices = ['indoor', 'outdoor', 'no preference']
    court_type = SelectField(label=u'Preferred Type of Basketball Court:',
                             choices=[(None, ' ')] + [(str(t), str(t)) for t in court_type_choices],
                             validators=[DataRequired()])

    submit = SubmitField('Update')


class FindGamesForm(FlaskForm):
    location = StringField(label="Enter your location", validators=[DataRequired()])
    cities = ["Emeryville", "Oakland", "El Cerrito", "Alameda",
              "Kensington", "Berkeley", "Albany", "San Francisco",
              "Sausalito", "Millbrae", "Mill Valley",
              "South San Francisco", "San Bruno", "Daly City",
              "Brisbane", "Pacifica"]

    city_choices = [(city, city) for city in cities]
    city = SelectField('City', validators=[DataRequired()],
                       choices=city_choices)
    game_date = DateField(label="Select a date", format='%Y-%m-%d',
                          validators=[DataRequired()])

    submit = SubmitField('Submit')


class CreateGamesForm(FlaskForm):
    game_date = DateField(label="Select a date", format='%Y-%m-%d',
                          validators=[DataRequired()])

    time_choices = ["7 AM", "8 AM", "9 AM", "10 AM", "11 AM", "12 PM", "1 PM",
                    "2 PM", "3 PM", "4 PM", "5 PM", "6 PM", "7 PM", "8 PM"]

    game_time = SelectField(label='Select a time', validators=[DataRequired()],
                            choices=[(t, t) for t in time_choices])

    skill_level_choices = ["beginner", "intermediate", "advanced"]
    skill_level = SelectField(label="Enter a skill level",
                              validators=[DataRequired()],
                              choices=[(c, c) for c in skill_level_choices])

    max_players_choices = [2, 4, 6, 8, 10]
    max_players = SelectField(label="Select the number of players",
                            validators=[DataRequired()],
                              coerce=str,
                              choices=[(str(c), str(c)) for c in
                                       max_players_choices])
    submit = SubmitField('Submit')


class CourtLocator:
    def _find_coordinates(self, user_location, city):
        """
        Finds the coordinates of a given address using the Google API
        Returns a tuple (lat, long)
        """
        full_address = self._create_full_address(user_location, city)

        url = (f"https://maps.googleapis.com/maps/api/geocode/json?address="
               f"{full_address}&key={apikey}")
        request = simplejson.load(urllib.request.urlopen(url))
        location_dict = request['results'][0]['geometry']['location']
        lat_long_tuple = (location_dict["lat"], location_dict["lng"])

        return lat_long_tuple

    def _lat_lng_converter(self, location_tuple):
        """
        Takes a tuple (lat, long) and converts it to a string "lat, long"
        """
        return f"{location_tuple[0]},{location_tuple[1]}"

    def _create_full_address(self, address, city):
        """
        Adds San Francisco, CA to an address and adds plus signs where there
        were spaces to be used in google maps
        """
        address_parts = [address, city, "CA"]
        full_address = ", ".join(address_parts)
        full_address = full_address.replace(" ", "+")

        return full_address

    def _to_minutes(self, hour_min):
        """
        Returns the minutes as an int from a string "x hours y minutes"
        """
        hour_min_split = hour_min.split(" ")
        time_parts = []
        for t in hour_min_split:
            if t.isdigit():
                time_parts.append(int(t))

        if len(time_parts) == 2:
            return (60 * time_parts[0]) + time_parts[1]

        return time_parts[0]


class FindCourt(CourtLocator):
    def __init__(self, location, city):
        self.location = location
        self.city = city

    def find_courts(self):
        courts = self._expanding_window()
        orig_coord = self._lat_lng_converter(self._find_coordinates
                                             (self.location, self.city))

        court_objects = []
        for c in courts:
            lat = c.latitude
            long = c.longitude
            dest_tup = (lat, long)
            dest_coord = self._lat_lng_converter(dest_tup)
            url = "https://maps.googleapis.com/maps/api/distancematrix/json?key=" \
                  "{0}&origins={1}&destinations={2}&mode={3}&departure_time=" \
                  "now&language=en-EN&sensor=false".format(
                str(apikey), str(orig_coord), str(dest_coord), str("driving"))
            result = simplejson.load(urllib.request.urlopen(url))

            dist = result['rows'][0]['elements'][0]['distance']['text']

            if "km" in dist:
                dist = round(float(dist.replace("km", "").strip()) * 0.62, 2)
            elif "m" in dist:
                dist = round(float(dist.replace("m", "").strip()) * .62 / 1000, 2)

            duration = result['rows'][0]['elements'][0]['duration']['text']

            C_obj = Court(court_name=c.court_name, distance=dist, duration=duration,
                          rating=c.rating, num_reviews=c.review_count,
                          indoor_outdoor=c.indoor_outdoor, lat=lat, long=long,
                          link=f"http://maps.google.com/maps?q={lat},{long}")

            court_objects.append(C_obj)

        court_objects = sorted(court_objects, key=lambda c: c.distance)[:5]

        return court_objects

    def _expanding_window(self):
        """
        Finds the closest courts using an expanding window of courts
        """
        user_lat, user_long = self._find_coordinates(self.location, self.city)
        window_size = 1e-2

        while True:
            lat_window = (user_lat - window_size, user_lat + window_size)
            long_window = (user_long - window_size, user_long + window_size)
            courts_in_window = db.session.query(CourtInformation)\
                .filter(CourtInformation.latitude.between(lat_window[0], lat_window[1]),
                        CourtInformation.longitude.between(long_window[0], long_window[1]))

            if courts_in_window.count() >= 5:
                break

            else:
                window_size += 5e-3

        return courts_in_window


class FindGame(CourtLocator):
    def __init__(self, location, city, game_date):
        self.location = location
        self.city = city
        self.game_date = game_date

    def calc_distances(self):
        games_query = self._query_date()
        match_objects = []
        if games_query.count() == 0:
            return match_objects

        else:
            orig_coord = self._lat_lng_converter(self._find_coordinates
                                                 (self.location, self.city))
            for q in games_query:
                lat = q.latitude
                long = q.longitude
                dest_tup = (lat, long)
                dest_coord = self._lat_lng_converter(dest_tup)

                url = "https://maps.googleapis.com/maps/api/distancematrix/json?key=" \
                      "{0}&origins={1}&destinations={2}&mode={3}&departure_time=" \
                      "now&language=en-EN&sensor=false".format(
                    str(apikey), str(orig_coord), str(dest_coord), str("driving"))
                result = simplejson.load(urllib.request.urlopen(url))

                dist = result['rows'][0]['elements'][0]['distance']['text']

                if "km" in dist:
                    dist = round(float(dist.replace("km", "").strip()) * 0.62, 2)
                elif "m" in dist:
                    dist = round(float(dist.replace("m", "").strip()) * .62 / 1000,
                                 2)
                M_obj = Match(court_name=q.court_name, distance=dist,
                              game_date=self.game_date, game_time=q.game_time,
                              skill_level=q.skill_level, max_players=q.max_players,
                              current_players=q.current_players, game_id = q.game_id,
                              username = q.username, players = q.players, create_or_join = 1,
                              link=f"http://maps.google.com/maps?q={lat},{long}")
                match_objects.append(M_obj)

            match_objects = sorted(match_objects, key=lambda c: c.distance)
            return match_objects

    def _query_date(self):
        games_query = db.session.query(ScheduledGames).filter(ScheduledGames.game_date == str(self.game_date), ScheduledGames.create_or_join == 1)
        return games_query


db.create_all()
db.session.commit()


# user_loader :
# This callback is used to reload the user object
# from the user ID stored in the session.
@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))
