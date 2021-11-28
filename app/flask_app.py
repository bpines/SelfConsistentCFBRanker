from flask import Flask
from config import Config

server = Flask(__name__)
server.config.from_object(Config)

from flask import Blueprint, render_template, redirect, request, url_for
from flask_bootstrap import Bootstrap

bootstrap = Bootstrap(server)
server_bp = Blueprint('main', __name__)

from app.forms import selectTeam
import pandas as pd
from app.functions import \
    (
    general as gen
    )

db = "ncaafb"
d= pd.read_pickle(db+".p")

@server_bp.route('/',methods=['GET', 'POST'])
def index():
    table = d["analysis"]["teamRankings"].copy()
    table = gen.formatDf(table)

    week = d["analysis"]["week"]
    return render_template('index.html', title = "Index", table=table, week=week)

@server_bp.route('/team_stats',methods=['GET', 'POST'])
def team_stats():
    form = selectTeam()
    team = form.myField.data
    data = d["analysis"]["byTeam"][team]

    if request.method == "POST":
        team = form.myField.data
        data = d["analysis"]["byTeam"][team]

    return render_template('teamStats.html', data=data,  form = form)

server.register_blueprint(server_bp)