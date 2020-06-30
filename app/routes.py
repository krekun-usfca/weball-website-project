from app import application, classes, db
from flask import flash, redirect, render_template, url_for, jsonify, request
from flask_login import current_user, login_user, login_required, logout_user
from flask_googlemaps import Map
from werkzeug.urls import url_parse


@application.context_processor
def utility_processor():
    login_form = classes.LogInForm()
    registration_form = classes.RegistrationForm()
    create_games_form = classes.CreateGamesForm()
    return dict(login_form=login_form, registration_form=registration_form,
                create_games_form=create_games_form)


@application.errorhandler(404)
def not_found(e):
  return render_template("404.html")


@application.route('/')
@application.route('/index')
def index():
    return render_template('index.html', authenticated_user=current_user.is_authenticated)


@application.route('/about')
def about():
    return render_template('about.html')


@application.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    else:
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc!='':
            next_page = 'login'

        login_form = classes.LogInForm()

        if login_form.validate_on_submit():
            username = login_form.username.data
            password = login_form.password.data
            user = classes.User.query.filter_by(username=username).first()

            if user is not None and user.check_password(password):
                login_user(user)
                return redirect(next_page)

        return render_template('index.html', form=login_form, login_form=login_form,
                               next_page=next_page)


@application.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@application.route('/register', methods=('GET', 'POST'))
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    else:
        registration_form = classes.RegistrationForm()
        next_page = 'register'

        if registration_form.validate_on_submit():
            username = registration_form.username.data
            password = registration_form.password.data
            confirm_password = registration_form.confirm_password.data
            email = registration_form.email.data
            user = classes.User(username, email, password)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for('index'))

        return render_template('index.html', form=registration_form, registration_form=registration_form,
                               next_page=next_page)


@application.route('/schedule_game', methods=['GET', 'POST'])
@login_required
def schedule_game():
    create_games_form = classes.CreateGamesForm()
    if create_games_form.validate_on_submit():
        username = current_user.username
        game_date = create_games_form.game_date.data
        game_time = create_games_form.game_time.data
        skill_level = create_games_form.skill_level.data
        max_players = create_games_form.max_players.data
        court_name = request.form['court_name']
        players = current_user.username

        game_id = db.session.query(db.func.max(classes.ScheduledGames.id)).scalar()
        if game_id is None:
            game_id = 1
        else:
            game_id+=1
        scheduled_game = classes.ScheduledGames(game_id=game_id,
                                                username=username,
                                                game_date=game_date,
                                                game_time=game_time,
                                                skill_level=skill_level,
                                                max_players=max_players,
                                                current_players=1,
                                                court_name=court_name,
                                                players = players,
                                                create_or_join = 1)

        db.session.add(scheduled_game)
        db.session.commit()
        return redirect(url_for("scheduled_games", court_name=court_name))
    return render_template('scheduled_games.html', create_games_form =create_games_form)


@application.route('/scheduled_games', methods=['GET', 'POST'])
@login_required
def scheduled_games():
    court_name = request.args.get('court_name')
    user_now = current_user.username

    if court_name is not None:
        game_info = classes.ScheduledGames.query.filter_by(court_name=court_name, create_or_join = 1).all()
        return render_template('scheduled_games.html', court_name=court_name, game_info=game_info, list_games=True, user_now = user_now)
    else:
        return redirect(url_for('court_locator'))


@application.route('/my_profile', methods=('GET', 'POST'))
@login_required
def my_profile():
    username = current_user.username
    pref_count = classes.Preference.query.filter_by(username=username).count()

    # if preferences already exist load them
    if pref_count > 0:
        user_pref = classes.Preference.query.filter_by(username=username).first()
        update_form = classes.UpdateProfileForm(obj=user_pref)
        if update_form.validate_on_submit():
            update_form.populate_obj(obj=user_pref)
            feet = update_form.feet.data
            inches = update_form.inches.data
            user_pref.height = int(feet) + (int(inches) / 12)
            db.session.commit()
            return redirect(url_for('my_profile'))

    else:
        update_form = classes.UpdateProfileForm()
        if update_form.validate_on_submit():
            age = int(update_form.age.data)
            gender = update_form.gender.data
            skill = update_form.skill.data
            feet = update_form.feet.data
            inches = update_form.inches.data
            address = update_form.address.data
            city = update_form.city.data
            state = update_form.state.data
            zipcode = str(update_form.zipcode.data)
            zipcode = zipcode.rjust(5, '0')
            court_type = update_form.court_type.data
            height = int(feet) + (int(inches) / 12)

            user_pref = classes.Preference(username=username, age=age, gender=gender, skill=skill,
                                           feet=feet, inches=inches, height=height,
                                           address=address, city=city, state=state, zipcode=zipcode,
                                           court_type=court_type)

            db.session.add(user_pref)
            db.session.commit()
            return redirect(url_for('my_profile'))
    return render_template('my_profile.html', form=update_form)


@application.route('/my_games', methods=('GET', 'POST'))
@login_required
def my_games():
    username = current_user.username
    active_games = db.session.query(classes.ScheduledGames).\
        filter(classes.ScheduledGames.create_or_join == 1)

    match_objects = []
    for game in active_games:
        if username in game.players:

            M = classes.Match(court_name=game.court_name,
                              game_date=str(game.game_date).split(" ")[0],
                              game_time=game.game_time,
                              skill_level=game.skill_level,
                              max_players=game.max_players,
                              current_players=game.current_players,
                              game_id = game.game_id,
                              username = game.username,
                              players = game.players,
                              create_or_join = game.create_or_join,
                              link=f"http://maps.google.com/maps?q={game.latitude},{game.longitude}",
                              distance=None)
            match_objects.append(M)
    if len(match_objects) == 0:
        has_games = False
    else:
        has_games = True
    return render_template('my_games.html', game_info=match_objects,
                           has_games=has_games)


@application.route('/find_court', methods=['GET', 'POST'])
@login_required
def court_locator():
    username = current_user.username
    pref_count = classes.Preference.query.filter_by(username=username).count()
    locator = classes.CourtLocator()
    find_court_form = classes.FindCourtForm()
    show_table = False

    if pref_count > 0:
        user_pref = classes.Preference.query.filter_by(username=username).first()
        location = user_pref.address
        city = user_pref.city
        centered_lat, centered_long = locator._find_coordinates(location, city)
    else:
        location = '443 Burnett Ave'
        city = 'San Francisco'
        centered_lat, centered_long = 37.7749, -122.4194

    if find_court_form.validate_on_submit():
        location = find_court_form.location.data
        city = find_court_form.city.data
        centered_lat, centered_long = locator._find_coordinates(location, city)
        show_table = True

    markers = [(centered_lat, centered_long)]
    find_courts = classes.FindCourt(location, city)
    court_objects = find_courts.find_courts()

    #Get court info from database
    for c in court_objects:
        pop_up = render_template('info_box.html', court_object=c)
        markers.append((c.lat, c.long, pop_up, 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png'))

    display_map = Map(identifier='courts',
                      lat=centered_lat,
                      lng=centered_long,
                      zoom=13,
                      markers=markers,
                      style='height:450px;width:700px;margin:75')

    return render_template('find_court.html', form=find_court_form, court_objects=court_objects,
                           show_table=show_table, map=display_map)


@application.route('/find_game', methods=['GET', 'POST'])
@login_required
def find_game():
    find_game_form = classes.FindGamesForm()
    user_now = current_user.username
    if find_game_form.validate_on_submit():
        location = find_game_form.location.data
        city = find_game_form.city.data
        game_date = find_game_form.game_date.data

        find_games = classes.FindGame(location=location, city=city,
                                      game_date=game_date)
        match_objects = find_games.calc_distances()
        if len(match_objects) == 0:
            return render_template('available_games.html', form=find_game_form,
                               games_found=False, game_date=game_date,
                               form_submitted=True, user_now = user_now)

        else:
            return render_template('available_games.html', form=find_game_form,
                                   games_found=True, match_objects=match_objects,
                                   game_date=game_date, form_submitted=True, user_now = user_now)

    return render_template('available_games.html', form=find_game_form,
                           form_submitted=False)


@application.route('/join', methods=['GET', 'POST'])
@login_required
def join():
   if request.method == 'POST':
        players = current_user.username # current user will join
        game_id = request.form['game_id']
        game_date = request.form['game_date']
        game_time = request.form['game_time']
        max_players = request.form['max_players']
        skill_level =request.form['skill_level']
        court_name = request.form['court_name']
        creator = request.form['username']
        players_str = request.form['players']
        current_players = int(request.form['current_players']) + 1

        current_game = classes.ScheduledGames.query.filter_by(game_id = game_id, create_or_join = 1).first()
        current_game.game_id = game_id
        current_game.game_date = game_date
        current_game.game_time = game_time
        current_game.max_players = max_players
        current_game.skill_level = skill_level
        current_game.court_name = court_name
        current_game.current_players = current_players
        current_game.players = players_str + ',' + players
        new_join_game = classes.ScheduledGames(game_id=game_id,
                                                username=creator,
                                                game_date=game_date,
                                                game_time=game_time,
                                                skill_level=skill_level,
                                                max_players=max_players,
                                                current_players= current_players,
                                                court_name=court_name,
                                                players = players,
                                                create_or_join = 0
                                                )
        db.session.add(new_join_game)
        db.session.commit()
        return redirect(url_for('my_games'))

@application.route('/left', methods=['GET', 'POST'])
@login_required
def left():
    if request.method == 'POST':
        game_id = request.form['game_id']
        players = request.form['players'] # long str of all players
        current_players = request.form['current_players'] # current number of players
        username = request.form['username'] # creators
        player = current_user.username
        if player == username:
            left_game = classes.ScheduledGames.query.filter_by(game_id = game_id, players = players, username = username).first()
            db.session.delete(left_game)
            players = players.split(',')
            players.remove(player)
            if players != []:
                new_creator = players[0]
                players = ','.join(players)
                new_main_game = classes.ScheduledGames.query.filter_by(game_id = game_id, players = new_creator).first()
                new_main_game.current_players = int(current_players) - 1
                new_main_game.players = players
                new_main_game.create_or_join = 1
                update_all_game = classes.ScheduledGames.query.filter_by(game_id = game_id, username = username).all()
                for row in update_all_game:
                    row.username = new_creator
        else:
            left_game = classes.ScheduledGames.query.filter_by(game_id = game_id, players = player).first()
            db.session.delete(left_game)
            main_game = classes.ScheduledGames.query.filter_by(game_id = game_id, create_or_join = 1).first()
            main_game.current_players = int(current_players) - 1
            players = players.split(',')
            players.remove(player)
            players = ','.join(players)
            main_game.players = players
        
        db.session.commit()
        return redirect(url_for('my_games'))

def main():
    application.run()


if __name__=="__main__":
    main()
