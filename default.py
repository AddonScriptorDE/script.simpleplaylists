#!/usr/bin/python
# -*- coding: utf-8 -*-
import xbmc, xbmcplugin, xbmcgui, xbmcaddon, locale, sys, urllib, urllib2, re, os, datetime, base64
from operator import itemgetter

pluginhandle=int(sys.argv[1])
addonID = "plugin.video.watch.it.later"
addon_work_folder=xbmc.translatePath("special://profile/addon_data/"+addonID)
settings = xbmcaddon.Addon(id=addonID)
translation = settings.getLocalizedString
cat = xbmc.getInfoLabel('Container.FolderPath')
catFile=xbmc.translatePath("special://profile/addon_data/"+addonID+"/lastContentType")

if cat=="addons://sources/video/":
  cat="Video"
elif cat=="addons://sources/audio/":
  cat="Audio"
elif cat=="addons://sources/image/":
  cat="Image"

if not os.path.isdir(addon_work_folder):
  os.mkdir(addon_work_folder)

if cat=="Video" or cat=="Audio" or cat=="Image":
  fh=open(catFile, 'w')
  fh.write(cat)
  fh.close()

useAlternatePlaylistPath=settings.getSetting("useAlternatePlDir")
showKeyboard=settings.getSetting("showKeyboard")

if useAlternatePlaylistPath=="true":
  playListFile=xbmc.translatePath(settings.getSetting("alternatePlDir")+"/SimplePlaylists.pl")
else:
  playListFile=xbmc.translatePath("special://profile/addon_data/"+addonID+"/SimplePlaylists.pl")

myPlaylists=[]
playlistsTemp=[]
for i in range(0,20,1):
  playlistsTemp.append(settings.getSetting("pl_video_"+str(i)))
for pl in playlistsTemp:
  if pl!="":
    myPlaylists.append("Video: "+pl)
playlistsTemp=[]
for i in range(0,20,1):
  playlistsTemp.append(settings.getSetting("pl_audio_"+str(i)))
for pl in playlistsTemp:
  if pl!="":
    myPlaylists.append("Audio: "+pl)
playlistsTemp=[]
for i in range(0,20,1):
  playlistsTemp.append(settings.getSetting("pl_image_"+str(i)))
for pl in playlistsTemp:
  if pl!="":
    myPlaylists.append("Image: "+pl)

def addCurrentUrl():
        url = xbmc.getInfoLabel('ListItem.FileNameAndPath')
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
        if url!="":
          fanart=""
          plot=""
          genre=""
          year=""
          runtime=""
          json_result = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovies", "params": {"properties": ["file", "fanart", "genre", "year", "runtime", "plot"]}, "id": 1}' )
          if json_result.find('"fanart":')>=0:
            spl=json_result.split('"fanart":')
            for i in range(1,len(spl),1):
                entry=spl[i]
                match=re.compile('"(.+?)"', re.DOTALL).findall(entry)
                fanartNew=match[0]
                match=re.compile('"file":"(.+?)"', re.DOTALL).findall(entry)
                urlNew=match[0].replace("\\\\","\\")
                match=re.compile('"genre":(.+?)"', re.DOTALL).findall(entry)
                genreNew=match[0].replace("\"","")
                match=re.compile('"year"(.+?)}', re.DOTALL).findall(entry)
                yearNew=match[0].replace(":","")
                match=re.compile('"runtime":(.+?)"', re.DOTALL).findall(entry)
                runtimeNew=match[0].replace("\"","")
                match=re.compile('"plot":(.+?)"', re.DOTALL).findall(entry)
                plotNew=match[0].replace("\"","")
                if url==urlNew:
                  fanart=fanartNew
                  plot=plotNew
                  genre=genreNew
                  year=yearNew
                  runtime=runtimeNew
          if fanart=="":
            json_result = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetEpisodes", "params": {"properties": ["file", "fanart", "showtitle", "plot"]}, "id": 1}' )
            if json_result.find('"fanart":')>=0:
              spl=json_result.split('"episodeid":')
              for i in range(1,len(spl),1):
                  entry=spl[i]
                  match=re.compile('"fanart":"(.+?)"', re.DOTALL).findall(entry)
                  fanartNew=match[0]
                  match=re.compile('"showtitle":"(.+?)"', re.DOTALL).findall(entry)
                  showtitleNew=match[0]
                  match=re.compile('"file":"(.+?)"', re.DOTALL).findall(entry)
                  urlNew=match[0].replace("\\\\","\\")
                  match=re.compile('"plot":(.+?)"}', re.DOTALL).findall(entry)
                  plotNew=match[0].replace("\"","")
                  if url==urlNew:
                    fanart=fanartNew
                    plot=plotNew
                    title=showtitleNew+" - "+title
          if title.find("////")>=0:
            title = title[:title.find("////")]
          if showKeyboard=="true":
            kb = xbmc.Keyboard(title, "Title")
            kb.doModal()
            if kb.isConfirmed():
              title = kb.getText()
          date=str(datetime.datetime.now())
          date=date[:date.find(".")]
          title =  date + ":::" + title
          dialog = xbmcgui.Dialog()
          pl = myPlaylists[dialog.select(translation(30004), myPlaylists)]
          if plot=="":
            plot=date
          playlistEntry="###TITLE###="+title+"###URL###="+url+"###FANART###="+fanart+"###PLOT###="+plot+"###GENRE###="+genre+"###YEAR###="+year+"###RUNTIME###="+runtime+"###PLAYLIST###="+pl+"###END###"
          if os.path.exists(playListFile):
            fh = open(playListFile, 'r')
            content=fh.read()
            fh.close()
            if content.find(playlistEntry[playlistEntry.find(":::"):])==-1:
              fh=open(playListFile, 'a')
              fh.write(playlistEntry+"\n")
              fh.close()
            else:
              xbmc.executebuiltin('XBMC.Notification(Info:,'+str(translation(30016))+'!,5000)')
          else:
            fh=open(playListFile, 'a')
            fh.write(playlistEntry+"\n")
            fh.close()

def playListMain():
        xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
        playlists=[]
        if os.path.exists(playListFile):
          fh = open(playListFile, 'r')
          for line in fh:
            pl=line[line.find("###PLAYLIST###=")+15:]
            pl=pl[:pl.find("###END###")]
            if not pl in playlists:
              if os.path.exists(catFile):
                fh = open(catFile, 'r')
                lastCat=fh.read()
                fh.close()
                if pl.find(lastCat)==0:
                  playlists.append(pl)
              else:
                playlists.append(pl)
          fh.close()
          for pl in playlists:
            addDir(pl.replace(lastCat+": ",""),pl,'showPlaylist',"")
        xbmcplugin.endOfDirectory(pluginhandle)

def showPlaylist(playlist):
        allEntrys=[]
        fh = open(playListFile, 'r')
        all_lines = fh.readlines()
        for line in all_lines:
          pl=line[line.find("###PLAYLIST###=")+15:]
          pl=pl[:pl.find("###END###")]
          url=line[line.find("###URL###=")+10:]
          url=url[:url.find("###")]
          fanart=line[line.find("###FANART###=")+13:]
          fanart=fanart[:fanart.find("###")]
          plot=line[line.find("###PLOT###=")+11:]
          plot=plot[:plot.find("###")]
          genre=line[line.find("###GENRE###=")+12:]
          genre=genre[:genre.find("###")]
          year=line[line.find("###YEAR###=")+11:]
          year=year[:year.find("###")]
          runtime=line[line.find("###RUNTIME###=")+14:]
          runtime=runtime[:runtime.find("###")]
          title=line[line.find("###TITLE###=")+12:]
          date=translation(30012)+": "+title[:title.find(":::")]
          title=title[title.find(":::")+3:title.find("###URL###")]
          if pl==playlist:
            entry=[title,url,date,pl,fanart,plot,genre,year,runtime]
            allEntrys.append(entry)
        fh.close()
        allEntrys=sorted(allEntrys, key=itemgetter(2), reverse=True)
        for entry in allEntrys:
          addLink(entry[0],entry[1],'playVideoFromPlaylist',"",entry[5],entry[3],entry[4],entry[6],entry[7],entry[8])
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

def addLink(name,url,mode,iconimage,plot,pl,fanart,genre,year,runtime):
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        type="Video"
        if pl.find("Image:")==0:
          type="Image"
        if year!="":
          year=int(year)
        liz.setInfo( type=type, infoLabels={ "Title": name, "plot": plot, "genre": genre, "year": year, "duration": runtime } )
        liz.setProperty('IsPlayable', 'true')
        liz.setProperty('fanart_image', fanart)
        liz.addContextMenuItems([(translation(30013), 'XBMC.RunScript(special://home/addons/'+addonID+'/remove.py,removeFromPlaylist:::'+urllib.quote_plus(name)+')')])
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
        return ok

def addDir(name,url,mode,iconimage):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        liz.addContextMenuItems([(translation(30014), 'XBMC.RunScript(special://home/addons/'+addonID+'/remove.py,removePlaylist:::'+urllib.quote_plus(name)+')'),(translation(30015), 'XBMC.RunScript(special://home/addons/'+addonID+'/remove.py,removeAllPlaylists:::ALL)')])
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
else:
    playListMain()