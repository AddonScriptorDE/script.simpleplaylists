#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys,os,re,urllib,xbmcplugin,xbmcaddon,xbmcgui

addonID = "plugin.video.watch.it.later"
settings = xbmcaddon.Addon(id=addonID)
useAlternatePlaylistPath=settings.getSetting("useAlternatePlDir")

if useAlternatePlaylistPath=="true":
  myPlaylist=xbmc.translatePath(settings.getSetting("alternatePlDir")+"/"+addonID+".playlist")
else:
  myPlaylist=xbmc.translatePath("special://profile/addon_data/"+addonID+".playlist")

playlistToRemove=urllib.unquote_plus(sys.argv[1])

newContent=""
fh = open(myPlaylist, 'r')
for line in fh:
  if line.find(playlistToRemove)==-1:
      newContent+=line
fh.close()
fh=open(myPlaylist, 'w')
fh.write(newContent)
fh.close()
xbmc.executebuiltin("Container.Refresh")