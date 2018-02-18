#!/usr/bin/env python
# Quck and Dirty Tidal to playlist converter for MPD

# pip install tidal-api
# pip install slugify
import io
import os
import tidalapi
from slugify import slugify

#we parse /etc/mpd.conf to get the tidal login details:

inTidal=False
password=username=quality=token=folder=None

with io.open("/etc/mpd.conf","r",encoding="utf-8") as f:
    for line in f:
        ll=line.lower()
        if "playlist_directory" in ll:
            l = line.split('"')[1::2]
            folder=l[0]
        if "tidal" in ll:
            inTidal=True
        if "password" in ll and inTidal:
            l = line.split('"')[1::2]
            password=l[0]
            next
        if "token" in ll and inTidal:
            l = line.split('"')[1::2]
            token=l[0]
            next
        if "username" in ll and inTidal:
            l = line.split('"')[1::2]
            username=l[0]
            next
        if "quality" in ll and inTidal:
            l = line.split('"')[1::2]
            quality=l[0]
            next
        if "}" in line and inTidal:
            break

if quality == None:
    quality = "High"

if username == None or password == None or token == None:
    print "Please configure /etc/mpd.conf with your tidal settings"
    raise SystemExit


# check we can write to the folder
if folder == None:
    folder = "."

if not os.access(folder, os.W_OK):
    print "Can't write to "+folder+" aborting\n"
    raise SystemExit

config = tidalapi.Config()
config.quality = quality
config.api_token = token

# log in to tidal
session = tidalapi.Session(config)
session.login(username, password)

# grab a list of the users playlists:
playlists = session.get_user_playlists(session.user.id)

# for each playlist make a extended .m3u file, extended are used here to work round some issues in my front end.
# we don't remove deleted playlists but that could be done.

for playlist in playlists:
    print playlist.name
    fh = io.open(folder+"/Tidal-"+slugify(playlist.name)+".m3u","w",encoding="utf-8")
    fh.write(u"#EXTM3U\n")
    tracks=session.get_playlist_tracks(playlist.id)
    for track in tracks:
        fh.write(u"#EXTINF:"+str(track.duration) + "," + track.artist.name + " - "+ track.name+"\n")
        fh.write(u"tidal://track/"+str(track.id)+"\n")
    fh.close()
# thats it :)
