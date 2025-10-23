from flask import Flask
from monApp.app import app
from flask import render_template, request
from flask import render_template


@app.route('/')
@app.route('/importer/')
def importer():
    return render_template("importer.html",title ="R3.01 Dev Web avec yannnis ")

@app.route('/configuration/')
def configuration():
    return render_template("configuration.html",title ="R3.01 Dev Web avec yannnis ")

@app.route('/repartition/')
def repartition():
    return render_template("repartition.html",title ="R3.01 Dev Web avec yannnis ")

@app.route('/exporter/')
def exporter():
    return render_template("exporter.html",title ="R3.01 Dev Web avec yannnis ")