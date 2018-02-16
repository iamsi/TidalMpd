#!/usr/bin/python
# Quck and Dirty Tidal to playlist converter for MPD

# pip install tidal-api
# pip install slugify
import tidalapi
from slugify import slugify
import codecs
import os

#we parse /etc/mpd.conf to get the tidal login details:

intidal=0
password=""
username=""
quality=""
token=""
folder=""

with open('/etc/mpd.conf') as f:
    for line in f:
        if 'playlist_directory' in line.lower():
            l = line.split('"')[1::2]
            folder=l[0]
        if 'tidal' in line.lower():
            intidal=1
        if 'password' in line.lower():
            l = line.split('"')[1::2]
            password=l[0]
            next
        if 'token' in line.lower():
            l = line.split('"')[1::2]
            token=l[0]
            next
        if 'username' in line.lower():
            l = line.split('"')[1::2]
            username=l[0]
            next
        if 'quality' in line.lower():
            l = line.split('"')[1::2]
            quality=l[0]
            next
        if '}' in line and intidal == 1:
            break

if quality == "":
    quality = "High"

if username == "" or password == "" or token == "":
    print "Please configure /etc/mpd.conf with your tidal settings"
    raise SystemExit


#check we can write to the folder
if folder == "":
    folder="."

if os.access(folder, os.W_OK) is not True:
    print "Can't write to "+folder+" aborting\n"
    raise SystemExit

config = tidalapi.Config()
config.quality = quality
config.api_token = token

# log in to tidal
session = tidalapi.Session(config)
session.login(username, password)

# grab a list of the users playlists:
playlists=session.get_user_playlists(session.user.id)

# for each playlist make a extended .m3u file, extended are used here to work round some issues in my front end.
# we don't remove deleted playlists but that could be done.

for playlist in playlists:
    print playlist.name
    fh = codecs.open(folder+"/Tidal-"+slugify(playlist.name)+".m3u",encoding="utf-8", mode="w")
    fh.write("#EXTM3U\n")
    tracks=session.get_playlist_tracks(playlist.id)
    for track in tracks:
        fh.write("#EXTINF:"+str(track.duration) + "," + track.artist.name + " - "+ track.name+"\n")
        fh.write("tidal://track/"+str(track.id)+"\n")
    fh.close()
#thats it :)
