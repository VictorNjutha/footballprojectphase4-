# app
from flask import Flask,make_response,request
from flask_migrate import Migrate
from flask_cors import CORS
from flask_restful import Api,Resource
from models import db,Team,Game,UpcomingGames
from flask import jsonify
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI']  = 'sqlite:///football.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app) # to allow cross-origin requests
migrate = Migrate(app,db)

db.init_app(app)
api = Api(app)

class Teams(Resource):
    def get(self):
        teams =[team.serialize() for team in  Team.query.all()]
        response = make_response(jsonify(teams),200)
        return response
    
    def post(self):
        data = request.get_json()
        team_name = data['team_name']
        location = data['location']
        start_year_str = data['start_year']
        coach = data['coach']

        # Convert the start_year string to a date object
        start_year = datetime.strptime(start_year_str, '%Y-%m-%d').date()

        get_name = Team.query.filter_by(team_name=team_name).first()
        if get_name:
            return {'error': 'team already exists'}, 404
        else:
            new_team = Team(team_name=team_name,location=location,start_year=start_year, coach = coach)
            db.session.add(new_team)
            db.session.commit()

            response = make_response(jsonify(new_team.serialize()), 201)
            return response

api.add_resource(Teams, '/teams')

class TeamsByID(Resource):
    def get(self,id):
        team = Team.query.get(id)
        if not team:
            return {'error':'team does not exist'},404
        else:
            response = make_response(jsonify(team.serialize()), 200)
            return response
    
    def delete(self, id):
        team = Team.query.get(id)
        if not team:
            return {'error':'team does not exist'},404
        else:
            db.session.delete(team)
            db.session.commit()
            response = make_response(jsonify({'message':'team deleted'}), 200)
            return response
        
    def patch(self, id):
        data = request.get_json()
        name = data['name']
        location = data['location']
        start_year_str = data['start_year']
        start_year = datetime.strptime(start_year_str, '%Y-%m-%d').date()

        existing_team = Team.query.get(id)
        if not existing_team:
            return {'error':'team does not exist'},404
        else:
            existing_team.name = name
            existing_team.location = location
            existing_team.start_year = start_year
            db.session.commit()

            response = make_response(jsonify(existing_team.serialize()), 200)
            return response
        
api.add_resource(TeamsByID, '/teams/<int:id>')


class Games(Resource):
    def get(self):
        games = [game.serialize() for game in Game.query.all()]
        response = make_response(jsonify(games), 200)
        return response

    def post(self):
        data = request.get_json()
        name = data['name']
        team_id = data['team_id']
        coach_id = data['coach_id']
        game_time_str = data['game_time']
        game_time = datetime.strptime(game_time_str, '%Y-%m-%d, %I:%M %p')

        new_game = Game(name=name, team_id=team_id, coach_id=coach_id, game_time=game_time)
        db.session.add(new_game)
        db.session.commit()

        response = make_response(jsonify(new_game.serialize()), 201)
        return response
    
api.add_resource(Games, '/games')

class GameByID(Resource):
    def get(self, id):
        game = Game.query.get(id)
        if not game:
            return {'error':'game does not exist'},404
        else:
            response = make_response(jsonify(game.serialize()), 200)
            return response
        
    def delete(self, id):
        game = Game.query.get(id)
        if not game:
            return {'error':'game does not exist'},404
        else:
            db.session.delete(game)
            db.session.commit()
            response = make_response(jsonify({'message':'game deleted'}), 200)
            return response
        
    def patch(self, id):
        data = request.get_json()
        name = data['name']
        team_id = data['team_id']
        coach_id = data['coach_id']
        game_time_str = data['game_time']
        game_time = datetime.strptime(game_time_str, '%Y-%m-%d, %I:%M %p')

        existing_id = Game.query.get(id)
        if not existing_id:
            return {'error':'game does not exist'},404
        else:
            existing_id.name = name
            existing_id.team_id = team_id
            existing_id.coach_id = coach_id
            existing_id.game_time = game_time
            db.session.commit()
            response = make_response(jsonify(existing_id.serialize()), 200)
            return response
        
api.add_resource(GameByID, '/games/<int:id>')

class UpcomingGame(Resource):
    def get(self):
        games = [game.serialize() for game in UpcomingGames.query.all()]
        response = make_response(jsonify(games), 200)
        return response
    
    def post(self):
        data = request.get_json()
        league = data['league']
        home_team = data['home_team']
        away_team = data['away_team']
        game_time_str = data['game_time']
        game_time = datetime.strptime(game_time_str, '%Y-%m-%dT%H:%M')

        current_date = datetime.now()
        if game_time < current_date:
            return {'error': 'cannot create game in the past'}, 400 
        else:
            new_game = UpcomingGames(league_name = league, home_team = home_team, away_team = away_team, game_time=game_time)
            db.session.add(new_game)
            db.session.commit()

        response = make_response(jsonify(new_game.serialize()), 201)
        return response
    
api.add_resource(UpcomingGame, '/upcoming_games')







if __name__ == '__main__':
    app.run(port=5555, debug=True)

    # current_date = datetime.now().date()