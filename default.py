#!/usr/bin/python
# -*- coding: utf-8 -*-
import xbmc, xbmcplugin, xbmcgui, xbmcaddon, locale, sys, urllib, urllib2, re, os, datetime, base64
from operator import itemgetter

useJson=True

pluginhandle=int(sys.argv[1])
addonID = "script.simpleplaylists"
addon_work_folder=xbmc.translatePath("special://profile/addon_data/"+addonID)
settings = xbmcaddon.Addon(id=addonID)
translation = settings.getLocalizedString
contentType = xbmc.getInfoLabel('Container.Property(addoncategory)')
lastContentTypeFile=xbmc.translatePath("special://profile/addon_data/"+addonID+"/lastContentType")

if contentType=="addons://sources/video/":
  contentType="Video"
elif contentType=="addons://sources/audio/":
  contentType="Audio"
elif contentType=="addons://sources/image/":
  contentType="Image"

if not os.path.isdir(addon_work_folder):
  os.mkdir(addon_work_folder)

if contentType=="Video" or contentType=="Audio" or contentType=="Image":
  fh=open(lastContentTypeFile, 'w')
  fh.write(contentType)
  fh.close()

useAlternatePlaylistPath=settings.getSetting("useAlternatePlDir")
showKeyboard=settings.getSetting("showKeyboard")
showConfirmation=settings.getSetting("showConfirmation")

if useAlternatePlaylistPath=="true":
  playListFile=xbmc.translatePath(settings.getSetting("alternatePlDir")+"/SimplePlaylists.pl")
  playListNames=xbmc.translatePath(settings.getSetting("alternatePlDir")+"/playlists")
  playListCats=xbmc.translatePath(settings.getSetting("alternatePlDir")+"/subfolders")
else:
  playListFile=xbmc.translatePath("special://profile/addon_data/"+addonID+"/SimplePlaylists.pl")
  playListNames=xbmc.translatePath("special://profile/addon_data/"+addonID+"/playlists")
  playListCats=xbmc.translatePath("special://profile/addon_data/"+addonID+"/subfolders")

myPlaylists=[]
if os.path.exists(playListNames):
  fh = open(playListNames, 'r')
  for line in fh:
    plType=line[:line.find("=")]
    names=line[line.find("=")+1:]
    spl=names.split(";")
    for name in spl:
      if name!="" and name!="\n":
        myPlaylists.append(plType+": "+name)
  fh.close()
myPlaylists.append("- "+translation(30017))
myPlaylists.append("- "+translation(30019))

myPlaylistsCats=[]
if os.path.exists(playListCats):
  fh = open(playListCats, 'r')
  for line in fh:
    plType=line[:line.find("=")]
    names=line[line.find("=")+1:]
    spl=names.split(";")
    for name in spl:
      if name!="" and name!="\n":
        myPlaylistsCats.append(plType+": "+name)
  fh.close()

def managePlaylists():
        dialog = xbmcgui.Dialog()
        typeArray = [translation(30026),translation(30027)]
        nr=dialog.select(translation(30025), typeArray)
        if nr>=0:
          type = typeArray[nr]
          if type==translation(30026):
            if os.path.exists(playListNames):
              types=[]
              fh = open(playListNames, 'r')
              for line in fh:
                types.append(line[:line.find("=")])
              fh.close()
              dialog = xbmcgui.Dialog()
              nr=dialog.select(type, types)
              if nr>=0:
                fullTemp=""
                type = types[nr]
                fh = open(playListNames, 'r')
                for line in fh:
                  temp=line
                  if line.find(type)==0:
                    temp=line[line.find("=")+1:].replace("\n","")
                    kb = xbmc.Keyboard(temp[:len(temp)-1], type)
                    kb.doModal()
                    if kb.isConfirmed():
                      temp = type+"="+kb.getText()
                      if temp[len(temp)-1:]!=";":
                        temp+=";"
                      temp+="\n"
                    else:
                      temp=line
                  fullTemp+=temp
                fh.close()
                fh=open(playListNames, 'w')
                fh.write(fullTemp)
                fh.close()
            else:
              xbmc.executebuiltin('XBMC.Notification(Info:,'+str(translation(30023))+'!,5000)')
          elif type==translation(30027):
            if os.path.exists(playListCats):
              pls=[]
              fh = open(playListCats, 'r')
              for line in fh:
                pls.append(line[:line.find("=")])
              fh.close()
              dialog = xbmcgui.Dialog()
              nr=dialog.select(translation(30026), pls)
              if nr>=0:
                fullTemp=""
                playlistTemp = pls[nr]
                fh = open(playListCats, 'r')
                for line in fh:
                  temp=line
                  if line.find(playlistTemp)==0:
                    temp=line[line.find("=")+1:].replace("\n","")
                    kb = xbmc.Keyboard(temp[:len(temp)-1], translation(30029)+" "+playlistTemp)
                    kb.doModal()
                    if kb.isConfirmed():
                      temp = playlistTemp+"="+kb.getText()
                      if temp[len(temp)-1:]!=";":
                        temp+=";"
                      temp+="\n"
                    else:
                      temp=line
                  fullTemp+=temp
                fh.close()
                fh=open(playListCats, 'w')
                fh.write(fullTemp)
                fh.close()
            else:
              xbmc.executebuiltin('XBMC.Notification(Info:,'+str(translation(30028))+'!,5000)')

def showPlaylists():
        dialog = xbmcgui.Dialog()
        plTypes=[translation(30001),translation(30002),translation(30003)]
        nr=dialog.select("SimplePlaylists", plTypes)
        if nr >=0:
          plType = plTypes[nr]
          if plType==translation(30001):
            fh=open(lastContentTypeFile, 'w')
            fh.write("Video")
            fh.close()
            xbmc.executebuiltin('XBMC.ActivateWindow(10025,plugin://script.simpleplaylists)')
          elif plType==translation(30002):
            fh=open(lastContentTypeFile, 'w')
            fh.write("Audio")
            fh.close()
            xbmc.executebuiltin('XBMC.ActivateWindow(10502,plugin://script.simpleplaylists)')
          elif plType==translation(30003):
            fh=open(lastContentTypeFile, 'w')
            fh.write("Image")
            fh.close()
            xbmc.executebuiltin('XBMC.ActivateWindow(10002,plugin://script.simpleplaylists)')

def addCurrentUrl():
        addModePlaying="false"
        url = xbmc.getInfoLabel('ListItem.FileNameAndPath')
        title = xbmc.getInfoLabel('Listitem.Label')
        plot = xbmc.getInfoLabel('Listitem.Plot')
        genre = xbmc.getInfoLabel('Listitem.Genre')
        year = xbmc.getInfoLabel('Listitem.Year')
        runtime = xbmc.getInfoLabel('Listitem.Duration')
        director = xbmc.getInfoLabel('Listitem.Director')
        rating = xbmc.getInfoLabel('Listitem.Rating')
        tvshowTitle = xbmc.getInfoLabel('Listitem.TVShowTitle')
        fanart = xbmc.getInfoLabel("Listitem.Property(Fanart_Image)")
        artist = xbmc.getInfoLabel('ListItem.Artist')
        picPath = xbmc.getInfoLabel('ListItem.PicturePath')
        if tvshowTitle!="":
          title=tvshowTitle+" - "+title
        if url=="":
          addModePlaying="true"
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
        if url!="" and addModePlaying=="true":
          if useJson==True:
              json_result = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovies", "params": {"properties": ["file", "fanart", "director", "genre", "rating", "year", "runtime", "plot"]}, "id": 1}' )
              if json_result.find('"director":')>=0:
                spl=json_result.split('"director":')
                for i in range(1,len(spl),1):
                    entry=spl[i]
                    match=re.compile('"(.+?)"', re.DOTALL).findall(entry)
                    directorNew=match[0]
                    match=re.compile('"file":"(.+?)"', re.DOTALL).findall(entry)
                    urlNew=match[0].replace("\\\\","\\")
                    match=re.compile('"fanart":(.+?)"', re.DOTALL).findall(entry)
                    fanartNew=match[0].replace("\"","")
                    match=re.compile('"genre":(.+?)"', re.DOTALL).findall(entry)
                    genreNew=match[0].replace("\"","")
                    match=re.compile('"rating":(.+?)"', re.DOTALL).findall(entry)
                    ratingNew=match[0].replace("\"","").replace(",","")
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
                      director=directorNew
                      rating=ratingNew
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
        if url!="":
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
          plType=""
          if director=="" and artist=="" and picPath=="":
            dialog = xbmcgui.Dialog()
            plTypes=[translation(30001),translation(30002),translation(30003)]
            nr=dialog.select(translation(30022), plTypes)
            if nr>=0:
              plType = plTypes[nr]
              if plType==translation(30001):
                plType="Video"
              elif plType==translation(30002):
                plType="Audio"
              elif plType==translation(30003):
                plType="Image"
          elif artist!="":
            plType="Audio"
          elif picPath!="":
            plType="Image"
          elif director!="":
            plType="Video"
          if plType!="":
            myPlaylistsTemp=[]
            for plTemp in myPlaylists:
              if plTemp.find(plType)==0 or plTemp.find("- "+translation(30017))==0 or plTemp.find("- "+translation(30019))==0:
                myPlaylistsTemp.append(plTemp)
            myPlaylistsTemp2=[]
            for plTemp in myPlaylistsTemp:
              myPlaylistsTemp2.append(plTemp.replace(plType+": ",""))
            dialog = xbmcgui.Dialog()
            nr=dialog.select(translation(30004), myPlaylistsTemp2)
            if nr>=0:
              pl = myPlaylistsTemp[nr]
              if pl=="- "+translation(30017):
                kb = xbmc.Keyboard("", translation(30017))
                kb.doModal()
                if kb.isConfirmed():
                  kbText=kb.getText()
                  pl = plType+": "+kbText
                  if os.path.exists(playListNames):
                    fh = open(playListNames, 'r')
                    content=fh.read()
                    fh.close()
                    if content.find(plType+"=")>=0:
                      fh = open(playListNames, 'r')
                      newPl=""
                      for line in fh:
                        newLine=line
                        if line.find(plType)==0:
                          newLine=line.replace("\n",kbText+";\n")
                        newPl+=newLine
                      fh.close()
                      fh = open(playListNames, 'w')
                      fh.write(newPl)
                      fh.close()
                    else:
                      fh = open(playListNames, 'a')
                      fh.write(plType+"="+kbText+";"+"\n")
                      fh.close()
                  else:
                    fh = open(playListNames, 'w')
                    fh.write(plType+"="+kbText+";"+"\n")
                    fh.close()
              elif pl=="- "+translation(30019):
                myPlaylistsTemp=[]
                for plTemp in myPlaylists:
                  if plTemp.find(plType)==0:
                    myPlaylistsTemp.append(plTemp)
                myPlaylistsTemp2=[]
                for plTemp in myPlaylistsTemp:
                  myPlaylistsTemp2.append(plTemp.replace(plType+": ",""))
                if len(myPlaylistsTemp2)>0:
                  dialog = xbmcgui.Dialog()
                  nr=dialog.select(translation(30004), myPlaylistsTemp2)
                  if nr>=0:
                    plForCat = myPlaylistsTemp[nr]
                    kb = xbmc.Keyboard("", translation(30020))
                    kb.doModal()
                    if kb.isConfirmed():
                      kbText=kb.getText()
                      pl = plForCat+";"+kbText
                      if os.path.exists(playListCats):
                        fh = open(playListCats, 'r')
                        content=fh.read()
                        fh.close()
                        if content.find(plForCat)>=0:
                          fh = open(playListCats, 'r')
                          newPl=""
                          for line in fh:
                            newLine=line
                            if line.find(plForCat)==0:
                              newLine=line.replace("\n",kbText+";\n")
                            newPl+=newLine
                          fh.close()
                          fh = open(playListCats, 'w')
                          fh.write(newPl)
                          fh.close()
                        else:
                          fh = open(playListCats, 'a')
                          fh.write(plForCat+"="+kbText+";"+"\n")
                          fh.close()
                      else:
                        fh = open(playListCats, 'w')
                        fh.write(plForCat+"="+kbText+";"+"\n")
                        fh.close()
                else:
                  xbmc.executebuiltin('XBMC.Notification(Info:,'+str(translation(30023))+'!,5000)')
              elif os.path.exists(playListCats):
                cats=[]
                fh = open(playListCats, 'r')
                for line in fh:
                  if line.find(pl)==0:
                    temp=line[line.find("=")+1:]
                    spl=temp.split(";")
                    for cat in spl:
                      if cat!="\n":
                        if not cat in cats:
                          cats.append(cat)
                cats.append("- "+translation(30024))
                fh.close()
                if len(cats)>1:
                  dialog = xbmcgui.Dialog()
                  nr=dialog.select(pl.replace(plType+": ",""), cats)
                  if nr>=0:
                    if cats[nr]!="- "+translation(30024):
                      pl = pl+";"+cats[nr]
                  else:
                    pl=""
              pl=str(pl)
              if pl!="" and pl!="- "+translation(30017) and pl!="- "+translation(30019):
                playlistEntry="###TITLE###="+title+"###URL###="+url+"###FANART###="+fanart+"###PLOT###="+plot+"###GENRE###="+genre+"###DIRECTOR###="+director+"###RATING###="+rating+"###YEAR###="+year+"###RUNTIME###="+runtime+"###PLAYLIST###="+pl+"###END###"
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
                if showConfirmation=="true":
                  xbmc.executebuiltin('XBMC.Notification(Info:,'+str(translation(30030))+'!,2000)')

def playListMain():
        lastContentType=""
        xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
        playlists=[]
        if os.path.exists(playListFile):
          fh = open(playListFile, 'r')
          for line in fh:
            pl=line[line.find("###PLAYLIST###=")+15:]
            pl=pl[:pl.find("###END###")]
            if pl.find(";")>=0:
              pl=pl[:pl.find(";")]
            if not pl in playlists:
              if os.path.exists(lastContentTypeFile):
                fh = open(lastContentTypeFile, 'r')
                lastContentType=fh.read()
                fh.close()
                if pl.find(lastContentType)==0:
                  playlists.append(pl)
              else:
                playlists.append(pl)
          fh.close()
          for pl in playlists:
            titleNew=pl;
            if lastContentType!="":
              titleNew=pl.replace(lastContentType+": ","")
            if os.path.exists(playListCats):
              fh = open(playListCats, 'r')
              content=fh.read()
              fh.close()
              if content.find(pl)>=0:
                addDir(titleNew,pl,'showPlayListCats',"")
              else:
                addDir(titleNew,pl,'showPlaylist',"")
            else:
              addDir(titleNew,pl,'showPlaylist',"")
        xbmcplugin.endOfDirectory(pluginhandle)

def showPlayListCats(playlist):
        xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
        cats=[]
        fh = open(playListFile, 'r')
        for line in fh:
          if line.find("###PLAYLIST###="+playlist+";")>=0:
            pl=line[line.find("###PLAYLIST###="+playlist+";")+len(playlist)+16:]
            pl=pl[:pl.find("###")]
            if not pl in cats:
              cats.append(pl)
        fh.close()
        for cat in cats:
          addDir(cat,playlist+";"+cat,'showPlaylist',"")
        showPlaylist(playlist)
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
          director=line[line.find("###DIRECTOR###=")+15:]
          director=director[:director.find("###")]
          genre=line[line.find("###GENRE###=")+12:]
          genre=genre[:genre.find("###")]
          rating=line[line.find("###RATING###=")+11:]
          rating=rating[:rating.find("###")]
          year=line[line.find("###YEAR###=")+11:]
          year=year[:year.find("###")]
          runtime=line[line.find("###RUNTIME###=")+14:]
          runtime=runtime[:runtime.find("###")]
          title=line[line.find("###TITLE###=")+12:]
          date=translation(30012)+": "+title[:title.find(":::")]
          title=title[title.find(":::")+3:title.find("###URL###")]
          if plot=="":
            plot=date
          if pl==playlist:
            entry=[title,url,date,pl,fanart,plot,genre,year,runtime,director,rating]
            allEntrys.append(entry)
        fh.close()
        allEntrys=sorted(allEntrys, key=itemgetter(2), reverse=True)
        for entry in allEntrys:
          addLink(entry[0],entry[1],'playMediaFromPlaylist',"",entry[5],entry[3],entry[4],entry[6],entry[7],entry[8],entry[9],entry[10])
        xbmcplugin.endOfDirectory(pluginhandle)

def playMediaFromPlaylist(url):
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

def addLink(name,url,mode,iconimage,plot,pl,fanart,genre,year,runtime,director,rating):
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        type="Video"
        if pl.find("Image:")==0:
          type="Image"
        if year!="":
          year=int(year)
        liz.setInfo( type=type, infoLabels={ "Title": name, "plot": plot, "genre": genre, "year": year, "director": director, "rating": rating, "duration": runtime } )
        liz.setProperty('IsPlayable', 'true')
        liz.setProperty('fanart_image', fanart)
        liz.addContextMenuItems([(translation(30013), 'XBMC.RunScript(special://home/addons/'+addonID+'/remove.py,removeFromPlaylist:::'+urllib.quote_plus(name+";;;"+pl)+')')])
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
        return ok

def addDir(name,url,mode,iconimage):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        liz.addContextMenuItems([(translation(30014), 'XBMC.RunScript(special://home/addons/'+addonID+'/remove.py,removePlaylist:::'+urllib.quote_plus(name)+')'),(translation(30015), 'XBMC.RunScript(special://home/addons/'+addonID+'/remove.py,removeAllPlaylists:::'+urllib.quote_plus(name[:name.find(":")])+')'),(translation(30025), 'RunPlugin(plugin://script.simpleplaylists/?mode=managePlaylists)')])
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok

params=parameters_string_to_dict(sys.argv[2])
mode=params.get('mode')
url=params.get('url')
if type(url)==type(str()):
  url=urllib.unquote_plus(url)

if mode == 'addCurrentUrl':
    addCurrentUrl()
elif mode == 'showPlaylists':
    showPlaylists()
elif mode == 'showAllPlaylists':
    showAllPlaylists()
elif mode == 'showPlaylist':
    showPlaylist(url)
elif mode == 'showPlayListCats':
    showPlayListCats(url)
elif mode == 'playMediaFromPlaylist':
    playMediaFromPlaylist(url)
elif mode == 'managePlaylists':
    managePlaylists()
else:
    playListMain()