# Quck and Dirty Tidal to playlist converter for MPD
#Copyright (c) <2018>, <Simon Donnellan, me@i-am.si>
#All rights reserved.
#
#Redistribution and use in source and binary forms, with or without
#modification, are permitted provided that the following conditions are met:
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#    * Neither the name of the <organization> nor the
#      names of its contributors may be used to endorse or promote products
#      derived from this software without specific prior written permission.
#
#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
#ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
#WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
#DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
#(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
#LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


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
        if 'token' in line.lower():
            l = line.split('"')[1::2]
            token=l[0]
        if 'username' in line.lower():
            l = line.split('"')[1::2]
            username=l[0]
        if 'quality' in line.lower():
            l = line.split('"')[1::2]
            quality=l[0]
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
