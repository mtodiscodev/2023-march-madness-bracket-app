from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pandas as pd
from pred_dict_2022 import preds as preds_dict
from uuid import uuid4

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///winners.db'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://nlavwjdwgcxeyg:0d2d99ddbae0886aec120f4239222d15aee55f2b2cf48f4a19d663c443fe6c49@ec2-54-158-26-89.compute-1.amazonaws.com:5432/d50p3glj8p4gtu'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://cbznbzdwmiytrq:900b3078c5e923a597e16924b47a0cc031b7ec91a9d8fc5fdc9d27ad20c084f3@ec2-3-219-63-251.compute-1.amazonaws.com:5432/d8j5j8obr43fn'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://diomqnthrtotfn:948703e978e213f7f8846e70f70863e13690f412b7778d67f434ae9aefa16fdb@ec2-44-213-228-107.compute-1.amazonaws.com:5432/d3kqv1ci7pjudp'
app.secret_key = '_wqe8nFuwV8sP*ijEn46kJVb'

db = SQLAlchemy(app)

#Create db model
class Winners(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	session_id = db.Column(db.String(200), nullable=False)
	game_id = db.Column(db.String(10), nullable=False)
	name = db.Column(db.String(200), nullable=False)
	seed = db.Column(db.Integer, nullable=False)
	created_at = db.Column(db.DateTime, default=datetime.utcnow())

	#Function to return string when adding
	def __repr__(self):
		#return '<Name %r>' % self.id
		return f"<id={self.id}, name={self.name}>, game_id={self.game_id}, seed={self.seed}"

preds = pd.read_csv('predictions_with_seeds.csv')
teams = list(preds['TeamName_1'].unique())
game_map = {1:9, 2:9, 3:10, 4:10, 5:11, 6:11, 7:12, 8:12, 9:13, 10:13, 11:14, 12:14, 13:15, 14:15, 15:16}

@app.route('/', methods=['GET', 'POST'])
def index():

	session['session_id'] = str(uuid4())

	session_id = session.get('session_id')

	if request.method == 'GET':
		db.session.query(Winners).delete()
		db.session.commit()
		return render_template('index.html', teams=teams, preds_dict=preds_dict)

	elif request.method == 'POST':
		game_winner = request.form.get('matchup', 'world')
		game_id = game_winner.split('||')[1]
		name = game_winner.split('||')[0]
		seed = game_winner.split('||')[2]
		winner = Winners(session_id=session_id, game_id=game_id, name=name, seed=seed)

		#Push to Database
		# try:
		db.session.add(winner)
		db.session.commit()
		redirect('/predict')
		# except:
			# return 'There was an error adding a winner to the db'

		return render_template('predict.html', winners=winners)

@app.route('/top-bracket', methods=['GET', 'POST'])
def top_predict():
	session_id = session.get('session_id')

	if request.method == 'POST':
		game_winner = request.form.get('matchup', 'world')
		game_id = game_winner.split('||')[1]
		name = game_winner.split('||')[0]
		seed = game_winner.split('||')[2]

		data = Winners.query.all()
		filtered_data = [x for x in data if (x.game_id==game_id) & (x.session_id==session_id)]

		if len(filtered_data) > 0:
			winner_to_update = Winners.query.get_or_404(filtered_data[0].id)
			winner_to_update.name = name
			winner_to_update.seed = seed
			try:
				db.session.commit()
				return redirect('/top-bracket')
				
			except:
				return "There was a problem updating"
		else:
			#Push to Database
			winner = Winners(session_id=session_id, game_id=game_id, name=name, seed=seed)

			# try:
			db.session.add(winner)
			db.session.commit()
			return redirect('/top-bracket')
			# except:
				# return 'There was an error adding a winner to the db'
	else:
		winners = Winners.query.filter(Winners.session_id == session_id).order_by(Winners.created_at)
		game_ids = [winner.game_id for winner in winners]
		winner_dict = {winner.game_id: winner.name for winner in winners}
		seed_dict = {winner.name: winner.seed for winner in winners}

		return render_template('top_bracket.html', session_id=session_id, winners=winners, game_ids=game_ids, seed_dict=seed_dict, winner_dict=winner_dict, game_map=game_map, preds_dict=preds_dict)

@app.route('/bottom-bracket', methods=['GET', 'POST'])
def bottom_predict():

	session_id = session.get('session_id')

	if request.method == 'POST':
		game_winner = request.form.get('matchup', 'world')
		game_id = game_winner.split('||')[1]
		name = game_winner.split('||')[0]
		seed = game_winner.split('||')[2]

		data = Winners.query.all()
		filtered_data = [x for x in data if (x.game_id==game_id) & (x.session_id==session_id)]

		if len(filtered_data) > 0:
			#winner_to_update = Winners.query.filter(Winners.session_id == session_id).get_or_404(filtered_data[0].id)
			winner_to_update = Winners.query.get_or_404(filtered_data[0].id)
			winner_to_update.name = name
			winner_to_update.seed = seed
			try:
				db.session.commit()
				return redirect('/bottom-bracket')
				
			except:
				return "There was a problem updating"
		else:

			#Push to Database
			winner = Winners(session_id=session_id, game_id=game_id, name=name, seed=seed)

			try:
				db.session.add(winner)
				db.session.commit()
				return redirect('/bottom-bracket')
			except:
				return 'There was an error adding a winner to the db'
	else:
		winners = Winners.query.filter(Winners.session_id == session_id).order_by(Winners.created_at)
		game_ids = [winner.game_id for winner in winners]
		winner_dict = {winner.game_id: winner.name for winner in winners}
		seed_dict = {winner.name: winner.seed for winner in winners}

		return render_template('bottom_bracket.html', session_id=session_id, winners=winners, game_ids=game_ids, seed_dict=seed_dict, winner_dict=winner_dict, game_map=game_map, preds_dict=preds_dict)


@app.route('/final-four', methods=['GET', 'POST'])
def ff_predict():

	session_id = session.get('session_id')

	if request.method == 'POST':
		game_winner = request.form.get('matchup', 'world')
		game_id = game_winner.split('||')[1]
		name = game_winner.split('||')[0]
		seed = game_winner.split('||')[2]

		data = Winners.query.all()
		filtered_data = [x for x in data if (x.game_id == game_id) & (x.session_id==session_id)]

		if len(filtered_data) > 0:
			#winner_to_update = Winners.query.filter(Winners.session_id == session_id).get_or_404(filtered_data[0].id)
			winner_to_update = Winners.query.get_or_404(filtered_data[0].id)
			winner_to_update.name = name
			winner_to_update.seed = seed
			try:
				db.session.commit()
				return redirect('/final-four')
				
			except:
				return "There was a problem updating"
		else:

			#Push to Database
			winner = Winners(session_id=session_id, game_id=game_id, name=name, seed=seed)

			try:
				db.session.add(winner)
				db.session.commit()
				return redirect('/final-four')
			except:
				return 'There was an error adding a winner to the db'
	else:
		winners = Winners.query.filter(Winners.session_id == session_id).order_by(Winners.created_at)
		game_ids = [winner.game_id for winner in winners]
		winner_dict = {winner.game_id: winner.name for winner in winners}
		seed_dict = {winner.name: winner.seed for winner in winners}


		return render_template('final_four.html', session_id=session_id, winners=winners, game_ids=game_ids, seed_dict=seed_dict, winner_dict=winner_dict, game_map=game_map, preds_dict=preds_dict)

