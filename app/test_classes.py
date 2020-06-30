from app import classes
from sqlalchemy import Integer, String, DateTime, Float

def UserFromDB(username):
    user = classes.User.query.filter_by(username=username).first()
    return user

def PreferenceFromB(username):
    pref = classes.Preference.query.filter_by(username=username).first()
    return pref

def GameFromB(username):
    game = classes.ScheduledGames.query.filter_by(username=username).first()
    return game

def test_User():
    '''
    Tests if master account is in the database.
    '''
    user = UserFromDB("master")
    assert user.email == "weball"
    assert user.username == "master"
    assert user.check_password("test") == True

def test_CourtInformation():
    '''
    Check CourtInformation db is not null
    Verify all columns have correct types
    '''
    assert len(classes.CourtInformation.query.all()) > 0
    assert type(classes.CourtInformation.court_id.type) == String
    assert type(classes.CourtInformation.court_name.type) == String
    assert type(classes.CourtInformation.rating.type) == Float
    assert type(classes.CourtInformation.latitude.type) == Float
    assert type(classes.CourtInformation.longitude.type) == Float
    assert type(classes.CourtInformation.address.type) == String
    assert type(classes.CourtInformation.city.type) == String
    assert type(classes.CourtInformation.zip_code.type) == String
    assert type(classes.CourtInformation.country.type) == String
    assert type(classes.CourtInformation.state.type) == String
    assert type(classes.CourtInformation.display_address.type) == String

def test_CourtAvailabilityHours():
    '''
    Check CourtAvailabilityHours db is not null
    Verify all columns have correct types
    '''
    assert len(classes.CourtAvailabilityHours.query.all()) > 0
    assert type(classes.CourtAvailabilityHours.court_name.type) == String
    assert type(classes.CourtAvailabilityHours.day_of_week.type) == String
    assert type(classes.CourtAvailabilityHours.time_12hr.type) == String
    assert type(classes.CourtAvailabilityHours.availability_value.type) == Integer
    assert type(classes.CourtAvailabilityHours.availability_description.type) == String

def test_Preference():
    '''
    Check types of Preferences
    Check if valid preferences for master account
    '''
    assert type(classes.Preference.username.type) == String
    assert type(classes.Preference.age.type) == Integer
    assert type(classes.Preference.gender.type) == String
    assert type(classes.Preference.skill.type) == String
    assert type(classes.Preference.feet.type) == Integer
    assert type(classes.Preference.inches.type) == Integer
    assert type(classes.Preference.height.type) == Float
    assert type(classes.Preference.address.type) == String
    assert type(classes.Preference.city.type) == String
    assert type(classes.Preference.state.type) == String
    assert type(classes.Preference.zipcode.type) == String
    assert type(classes.Preference.court_type.type) == String

    pref = PreferenceFromB('master')
    assert pref.age == 18
    assert pref.gender == 'male'
    assert pref.skill == 'beginner'
    assert pref.feet == 1
    assert pref.inches == 0
    assert pref.height == 1.0
    assert pref.address == '101 Howard'
    assert pref.city == 'San Francisco'
    assert pref.zipcode == '94105'
    assert pref.court_type == 'indoor'

def test_CourtTimings():
    '''
    Check CourtTimings db is not null
    Verify all columns have correct types
    '''
    assert len(classes.CourtTimings.query.all()) > 0
    assert type(classes.CourtTimings.court_name.type) == String
    assert type(classes.CourtTimings.day_of_week.type) == String
    assert type(classes.CourtTimings.hours.type) == String
    assert type(classes.CourtTimings.open.type) == Integer
    assert type(classes.CourtTimings.close.type) == Integer

def test_ScheduledGames():
    '''
    Check types of ScheduledGames
    Check if valid scheduled game for master account
    '''
    assert type(classes.ScheduledGames.game_id.type) == Integer
    assert type(classes.ScheduledGames.username.type) == String
    assert type(classes.ScheduledGames.game_date.type) == DateTime
    assert type(classes.ScheduledGames.game_time.type) == String
    assert type(classes.ScheduledGames.skill_level.type) == String
    assert type(classes.ScheduledGames.max_players.type) == Integer
    assert type(classes.ScheduledGames.current_players.type) == Integer
    assert type(classes.ScheduledGames.court_name.type) == String
    assert type(classes.ScheduledGames.players.type) == String
    assert type(classes.ScheduledGames.latitude.type) == Float
    assert type(classes.ScheduledGames.longitude.type) == Float
    assert type(classes.ScheduledGames.create_or_join.type) == Integer

    game = GameFromB('master')
    assert game.game_id == 5
    assert game.game_time == '12 PM'
    assert game.skill_level == 'beginner'
    assert game.max_players == 4
    assert game.court_name == 'Embarcadero YMCA'
