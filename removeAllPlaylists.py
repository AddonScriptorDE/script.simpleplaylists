#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys,os,re,urllib,xbmcplugin,xbmcaddon,xbmcgui

addonID = "plugin.video.watch.it.later"
settings = xbmcaddon.Addon(id=addonID)
useAlternatePlaylistPath=settings.getSetting("useAlternatePlDir")

if useAlternatePlaylistPath=="true":
  playListFile=xbmc.translatePath(settings.getSetting("alternatePlDir")+"/"+addonID+".playlist")
else:
  playListFile=xbmc.translatePath("special://profile/addon_data/"+addonID+".playlist")

fh=open(playListFile, 'w')
fh.write("")
fh.close()
xbmc.executebuiltin("Container.Refresh")