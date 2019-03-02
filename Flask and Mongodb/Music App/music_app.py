from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
import pandas as pd

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'Music'
app.config['MONGO_URI'] = "mongodb://localhost:27017/Music"

mongo = PyMongo(app)

######## Adding and Searching ##########
@app.route('/artist', methods=['GET','POST'])
def add_artist_details():
	artist_col = mongo.db.Artist
	artistid = request.json['ArtistID']
	name = request.json['Name']

	if request.method == 'POST':
		exist_id = artist_col.find_one({'ArtistID': artistid})
		if exist_id is None:
			artist_idd = artist_col.insert({'ArtistID' : artistid, 'Name' : name})
			return 'Artist successfully Added..!'
		return 'ID already exist!'
	
@app.route('/artist/<name>', methods=['GET', 'POST'])
def search_artist(name):
	artist_col = mongo.db.Artist
	album_col = mongo.db.Album

	output = {}
	if request.method == 'GET':
		exist_id = artist_col.find_one({'Name': name})
		if exist_id:
			artist_id = exist_id['ArtistID']
			artist_name = exist_id['Name']
			output['ArtistID'] = artist_id
			output['Artist Name'] = artist_name

			album_exist = album_col.find({'ArtistID': artist_id}).count()
			output['Number of Albums'] = album_exist

			
			return jsonify({'result': output})
		return 'Artist Not Found'



@app.route('/album', methods=['GET', 'POST'])
def add_album_details():
	album_col = mongo.db.Album
	albumid = request.json['AlbumID']
	title = request.json['Title']
	artistid = request.json['ArtistID']

	if request.method == 'POST':
		exist_id = album_col.find_one({'AlbumID': albumid})
		if exist_id is None:
			album_idd = album_col.insert({'AlbumID' : albumid, 'Title' : title, 'ArtistID': artistid})
			return 'Album successfully Added..!'
		return 'ID already exist!'

@app.route('/album/<name>', methods=['GET', 'POST'])
def search_album(name):
	album_col = mongo.db.Album
	artist_col = mongo.db.Artist
	track_col = mongo.db.Track

	output = {}
	if request.method == 'GET':
		exist_id = album_col.find_one({'Title': name})
		if exist_id:
			album_id = exist_id['AlbumID']
			album_name = exist_id['Title']
			artist_id = exist_id['ArtistID']
			output['Album Name'] = album_name
			output['Album ID'] = album_id
			output['Artist ID'] = artist_id
			
			artist_exist = artist_col.find_one({'ArtistID': artist_id})
			if artist_exist:
				artist_name = artist_exist['Name']
				output['Artist Name'] = artist_name

			track_count = track_col.find({'AlbumID': album_id}).count()
			output['Number of Tracks'] = track_count


			return jsonify({'result': output})
		return 'Album Not Found'





@app.route('/track', methods=['GET', 'POST'])
def add_track_details():
	track_col = mongo.db.Track
	trackid = request.json['TrackID']
	trackname = request.json['TrackName']
	albumid = request.json['AlbumID']

	if request.method == 'POST':
		exist_id = track_col.find_one({'TrackID': trackid})
		if exist_id is None:
			track_idd = track_col.insert({'TrackID' : trackid, 'TrackName' : trackname, 'AlbumID': albumid})
			return 'Track successfully Added..!'
		return 'ID already exist!'


@app.route('/track/<name>', methods=['GET', 'POST'])
def search_track(name):
	track_col = mongo.db.Track
	album_col = mongo.db.Album
	artist_col = mongo.db.Artist

	output = {}
	if request.method == 'GET':
		exist_id = track_col.find_one({'Title': name})
		if exist_id:
			track_id = exist_id['TrackID']
			album_id = exist_id['AlbumID']
			output['Track ID'] = track_id
			output['Track Name'] = name
			output['Album ID'] = album_id
			
			exist_album = album_col.find_one({"AlbumID": album_id})
			if exist_album:
				artist_id = exist_album['ArtistID']
				album_name = exist_album['Title']
				output['Artist ID'] = artist_id
				output['Album Name'] = album_name
				
				exist_artist = artist_col.find_one({"ArtistID": artist_id})
				if exist_artist:
					artist_name = exist_artist['Name']
					output['Artist Name'] = artist_name

		return jsonify({'result': output})
		


######## Deleting items #########

#1. Delete only from "Track" table...
@app.route('/track', methods=['DELETE'])
def delete_track():
	track_col = mongo.db.Track
	trackid = request.json['TrackID']
	trackname = request.json['TrackName']
	if request.method == 'DELETE':
		exist_id = track_col.find_one({'TrackID': trackid, 'TrackName': trackname})
		if exist_id:
			del_track = track_col.remove({'TrackID': trackid, 'TrackName': trackname})
			return 'Track deleted succesfully'
		return 'Track Not Found'


#2. Delete from "Album" table - which will delete songs from "Track" table for respective Album.
@app.route('/album', methods=['DELETE'])
def delete_album():
	album_col = mongo.db.Album
	track_col = mongo.db.Track
	albumid = request.json['AlbumID']
	if request.method == 'DELETE':
		exist_id = album_col.find_one({'AlbumID': albumid})
		if exist_id:
			del_album = album_col.remove({'AlbumID': albumid})
			del_tracks = track_col.remove({'AlbumID': albumid})
			return 'Album deleted succesfully'
		return 'Album Not Found'


#3. Delete from "Artist" table - which will delete albums of respective albums, tracks of that artist.
@app.route('/artist', methods=['DELETE'])
def delete_artists():
	artist_col = mongo.db.Artist
	album_col = mongo.db.Album
	track_col = mongo.db.Track
	artistid = request.json['ArtistID']

	list_album_ids = []
	if request.method == 'DELETE':
		exist_id = artist_col.find_one({'ArtistID': artistid})
		if exist_id:
			del_artist = artist_col.remove({'ArtistID': artistid})

			find_artist_album = album_col.find({'ArtistID': artistid})
			for i in find_artist_album:
				output = {'AlbumID': i['AlbumID']}
				list_album_ids.append(output['AlbumID'])

			del_album = album_col.remove({'ArtistID': artistid})

			for i in list_album_ids:
				exist_id = track_col.find_one({'AlbumID': i})
				if exist_id:
					del_tracks = track_col.remove({'AlbumID': i})
				else:
					continue

			return 'Artist deleted succesfully'
		return 'Artist Not Found'
 

if __name__ == '__main__':
	app.run(debug=True)