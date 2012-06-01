#!/usr/bin/python
# -*- coding: utf-8 -*-
import xbmc, xbmcplugin, xbmcgui, xbmcaddon, locale, sys, urllib, urllib2, re, os, datetime, base64
from operator import itemgetter

pluginhandle=int(sys.argv[1])
addonID = "plugin.video.watch.it.later"
addon_work_folder=xbmc.translatePath("special://profile/addon_data/"+addonID)
settings = xbmcaddon.Addon(id=addonID)
translation = settings.getLocalizedString

if not os.path.isdir(addon_work_folder):
  os.mkdir(addon_work_folder)

useAlternatePlaylistPath=settings.getSetting("useAlternatePlDir")

if useAlternatePlaylistPath=="true":
  playListFile=xbmc.translatePath(settings.getSetting("alternatePlDir")+"/playlist")
else:
  playListFile=xbmc.translatePath("special://profile/addon_data/"+addonID+"/playlist")

playlistsTemp=[]
for i in range(0,19,1):
  playlistsTemp.append(settings.getSetting("pl_offline_"+str(i)))
myLocalPlaylists=[]
for pl in playlistsTemp:
  if pl!="":
    myLocalPlaylists.append(pl)
playlistsTemp=[]
for i in range(0,19,1):
  playlistsTemp.append(settings.getSetting("pl_online_"+str(i)))
myOnlinePlaylists=[]
for pl in playlistsTemp:
  if pl!="":
    myOnlinePlaylists.append(pl)

def addCurrentUrl():
        path = xbmc.getInfoLabel('ListItem.Path')
        filenameAndPath = xbmc.getInfoLabel('ListItem.FileNameAndPath')
        filename = filenameAndPath.replace(path,"")
        url = filenameAndPath#path+urllib.quote_plus(filename)
        title = xbmc.getInfoLabel('Listitem.Label')
        if url=="":
          try:
            playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
            if playlist.getposition()>=0:
              title = playlist[playlist.getposition()].getdescription()
              url = playlist[playlist.getposition()].getfilename()
            else:
              xbmc.executebuiltin('XBMC.Notification(Info:,'+str(translation(30005))+'!,5000)')
          except:
            try:
              playlist = xbmc.PlayList(xbmc.PLAYLIST_MUSIC)
              if playlist.getposition()>=0:
                title = playlist[playlist.getposition()].getdescription()
                url = playlist[playlist.getposition()].getfilename()
              else:
                xbmc.executebuiltin('XBMC.Notification(Info:,'+str(translation(30005))+'!,5000)')
            except:
              pass
        title = str(datetime.date.today()).replace("-",".") + " - " + title
        if url.find("http://")==0 or url.find("rtmp://")==0 or url.find("rtmpe://")==0 or url.find("rtmps://")==0 or url.find("rtmpt://")==0 or url.find("rtmpte://")==0 or url.find("mms://")==0 or url.find("plugin://")==0:
          dialog = xbmcgui.Dialog()
          pl = "Online: "+myOnlinePlaylists[dialog.select(translation(30004), myOnlinePlaylists)]
        else:
          dialog = xbmcgui.Dialog()
          pl = str(translation(30003))+": "+myLocalPlaylists[dialog.select(translation(30004), myLocalPlaylists)]
        playlistEntry="###TITLE###="+title+"###URL###="+url+"###PLAYLIST###="+pl+"###END###"
        if os.path.exists(playListFile):
          fh = open(playListFile, 'r')
          content=fh.read()
          fh.close()
          if content.find(playlistEntry)==-1:
            fh=open(playListFile, 'a')
            fh.write(playlistEntry+"\n")
            fh.close()
        else:
          fh=open(playListFile, 'a')
          fh.write(playlistEntry+"\n")
          fh.close()

def playListMain():
        playlists=[]
        if os.path.exists(playListFile):
          fh = open(playListFile, 'r')
          for line in fh:
            pl=line[line.find("###PLAYLIST###=")+15:]
            pl=pl[:pl.find("###END###")]
            if not pl in playlists:
              playlists.append(pl)
          fh.close()
          for pl in playlists:
            addDir(pl,pl,'showPlaylist',"")
        xbmcplugin.endOfDirectory(pluginhandle)

def showPlaylist(playlist):
        allEntrys=[]
        fh = open(playListFile, 'r')
        all_lines = fh.readlines()
        for line in all_lines:
          pl=line[line.find("###PLAYLIST###=")+15:]
          pl=pl[:pl.find("###END###")]
          url=line[line.find("###URL###=")+10:]
          url=url[:url.find("###PLAYLIST###")]
          title=line[line.find("###TITLE###=")+12:]
          title=title[:title.find("###URL###")]
          if pl==playlist:
            entry=[title,urllib.quote_plus(url)]
            allEntrys.append(entry)
        fh.close()
        allEntrys=sorted(allEntrys, key=itemgetter(0), reverse=True)
        for entry in allEntrys:
          addRemovableLink(entry[0],entry[1],'playVideoFromPlaylist',"",pl)
        xbmcplugin.endOfDirectory(pluginhandle)

def playVideoFromPlaylist(url):
        listitem = xbmcgui.ListItem(path=urllib.unquote_plus(url))
        return xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)

def parameters_string_to_dict(parameters):
        ''' Convert parameters encoded in a URL to a dict. '''
        paramDict = {}
        if parameters:
            paramPairs = parameters[1:].split("&")
            for paramsPair in paramPairs:
                paramSplits = paramsPair.split('=')
                if (len(paramSplits)) == 2:
                    paramDict[paramSplits[0]] = paramSplits[1]
        return paramDict

def addRemovableLink(name,url,mode,iconimage,playlist):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        liz.setProperty('IsPlayable', 'true')
        playlistEntry="###TITLE###="+name+"###URL###="+urllib.unquote_plus(url)+"###PLAYLIST###="+playlist+"###END###"
        liz.addContextMenuItems([('Remove from Playlist', 'XBMC.RunScript(special://home/addons/'+addonID+'/removeFromPlaylist.py,'+urllib.quote_plus(playlistEntry)+')',)])
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz)
        return ok

def addDir(name,url,mode,iconimage):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok

params=parameters_string_to_dict(sys.argv[2])
mode=params.get('mode')
url=params.get('url')
if type(url)==type(str()):
  url=urllib.unquote_plus(url)

if mode == 'addCurrentUrl':
    addCurrentUrl()
elif mode == 'showAllPlaylists':
    showAllPlaylists()
elif mode == 'showPlaylist':
    showPlaylist(url)
elif mode == 'playVideoFromPlaylist':
    playVideoFromPlaylist(url)
elif mode == 'managePlaylist':
    managePlaylist()
else:
    playListMain()