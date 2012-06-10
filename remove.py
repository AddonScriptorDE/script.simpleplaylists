#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys,os,re,urllib,xbmcplugin,xbmcaddon,xbmcgui

addonID = "script.simpleplaylists"
settings = xbmcaddon.Addon(id=addonID)
useAlternatePlaylistPath=settings.getSetting("useAlternatePlDir")

if useAlternatePlaylistPath=="true":
  myPlaylist=xbmc.translatePath(settings.getSetting("alternatePlDir")+"/SimplePlaylists.pl")
else:
  myPlaylist=xbmc.translatePath("special://profile/addon_data/"+addonID+"/SimplePlaylists.pl")

spl=urllib.unquote_plus(sys.argv[1]).split(":::")
pl=""
mode=spl[0]
playlistEntry=spl[1]
if playlistEntry.find(";;;")>=0:
  pl=playlistEntry.split(";;;")[1]
  playlistEntry=playlistEntry.split(";;;")[0]

newContent=""
fh = open(myPlaylist, 'r')
for line in fh:
  if mode=="removePlaylist":
    if line.find(playlistEntry+"###")==-1:
       newContent+=line
  elif mode=="removeFromPlaylist":
    if line.find(playlistEntry)>=0 and line.find("###PLAYLIST###="+pl+"###END###")>=0:
      pass
    else:
      newContent+=line
  elif mode=="removeAllPlaylists":
    if line.find("###PLAYLIST###="+playlistEntry)==-1:
       newContent+=line
fh.close()
fh=open(myPlaylist, 'w')
fh.write(newContent)
fh.close()
xbmc.executebuiltin("Container.Refresh")