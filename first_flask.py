from flask import Flask, request, render_template
import numpy as np
import pandas as pd
from bokeh.plotting import figure, output_file, show
from bokeh.resources import INLINE
from bokeh.embed import components
from bokeh.util.string import encode_utf8
from bs4 import BeautifulSoup
import requests

app = Flask(__name__)

def make_fancy_plot(Team, Stat):
    # Get Fancy Stats
    source = requests.get('http://hkref.com/tiny/LMtAx').text
    soup = BeautifulSoup(source, 'lxml')

    data = []
    for i in soup.find_all('tr'):
        temp = []
        for j in i.find_all('td'):
            temp.append(j.text)
        data.append(temp)

    data = [i for i in data if len(i) > 1]
    
    # Make dataframe
    columns=['Team', 'Season', 'Corsi For', 'Corsi Against', 'Corsi For %', 'Fenwick For', 'Fenwick Against', 'Fenwick For %', 'Shooting %', 'Save %', 'PDO (S% + SV%)', 'Offensive Zone Start', 'Defensive Zone Start', 'FOW', 'FOL', 'FO%', 'Hits', 'Blocks']
    df = pd.DataFrame(data, columns=columns)
    df.replace('MDA', 'ANA', inplace=True)
    df.replace('PHX', 'ARI', inplace=True)
    df.replace('ATL', 'WPG', inplace=True)
    df.Season = df.Season.str.slice(0,2) + df.Season.str.slice(5,7)
    df = df.apply(pd.to_numeric, errors='ignore')
    df.sort_values(by=['Team', 'Season'], inplace=True)
    
    team_data = df[df.Team == Team]
    
    X = team_data.Season
    
    Y = team_data[Stat]
    
    # output to static HTML file
    #output_file("lines.html")

    # create a new plot with a title and axis labels
    p = figure(title="{} {}".format(Team, Stat), x_axis_label='Season', y_axis_label=Stat)

    # add a line renderer with legend and line thickness
    p.line(X, Y, line_width=2)

    # show the results
    #show(p)
    script, div = components(p)
    return script, div

@app.route("/", methods=['POST', 'GET'])

def index():
    if request.method =='POST':
        Team = request.form['Team']
        Stat = request.form['Stat']
        script, div = make_fancy_plot(Team, Stat)
        js_resources = INLINE.render_js()
        css_resources = INLINE.render_css()
        html = render_template('index.html', plot_script=script,plot_div=div,js_resources=js_resources,css_resources=css_resources)
        return encode_utf8(html)
    else: 
        return render_template('index.html', plot_script='',plot_div='',js_resources='',css_resources='')




    
