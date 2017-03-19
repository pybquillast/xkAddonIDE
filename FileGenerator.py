# -*- coding: utf-8 -*-
'''
Created on 30/12/2014

@author: Alex Montes Barrios
'''
import sys
import re
import CustomRegEx
import os
import tkMessageBox
import zipfile
import shutil
import operator
import tkFileDialog
import sys
import imp
import urllib
import contextlib
import StringIO
import network
import ftplib
import urlparse
import menuThreads
import xmlFileWrapper
import json

SEP = '/'
IMAGEFILES = ['.bmp', '.dcx', '.eps', '.gif', '.im', '.jpg', '.jpeg', '.pcd', '.pcx', '.pdf', '.png', '.ppm', '.psd', '.tiff', '.xbm', '.xpm']

class FileGenerator(object):
    def __init__(self, addonSettings, addonThreads):
        self.addonsettings = addonSettings
        self.addonthreads = addonThreads
        self.filesfilter = 0
        settings = addonSettings.getParam()
        fileGen = settings.get('filegen') or 'Basic'
        module = __import__('Coders.%s' % fileGen)
        module = getattr(module, fileGen)
        modeObjets = dir(module)
        self.fileClasses = [getattr(module, fileclass) for fileclass in modeObjets if fileclass.startswith('addonFile_')]
        self.getFileInstances()
        pass

    def modSourceCodeGetter(self):
        answ = []
        for key in self.editableFiles:
            filegen = self._fileGenerators[key]
            value = filegen.modSourceCode
            if value is None: continue
            answ.append((key, value))
        return answ

    def modSourceCodeSetter(self, value):
        if isinstance(value, dict):         # Para compatibilidad con versiones anteriores
            value = [('addon_module', value)]
        elif not isinstance(value, list):
            raise Exception('Invalid parameters')
        editables = dict.fromkeys(self.editableFiles, None)
        editables.update(value)
        for key, sourceCode in editables.items():
            fileObj = self._fileGenerators[key]
            fileObj.modSourceCode = sourceCode or fileObj._defConstructor()
        pass

    modSourceCode = property(fget=modSourceCodeGetter, fset=modSourceCodeSetter)

    def getAddonModule(self):
        return self._fileGenerators['addon_module']

    def getFileInstances(self):
        addonSettings = self.addonsettings
        addonThreads = self.addonthreads
        settings = addonSettings.getParam()
        fileClasses = self.fileClasses
        filesfilter = 0
        for value, key in ((1, 'point_pluginsource'),
                           (2, 'point_module'),
                           (4, 'point_repository')):
            if settings[key]:
                filesfilter +=  value
        if self.filesfilter == filesfilter: return
        self.filesfilter = filesfilter
        self._fileGenerators = {}
        self.editableFiles = []
        for fileclass in fileClasses:
            if not fileclass.generateFor & filesfilter: continue
            fileInst = fileclass(addonSettings, addonThreads)
            filemetadata = fileInst.getFileMetaData()
            fileId = filemetadata[0]
            self._fileGenerators[fileId] = fileInst
            if fileInst.isEditable: self.editableFiles.append(fileInst.fileId)

    def listFiles(self):
        self.getFileInstances()
        answ = []
        for fileInst in self._fileGenerators.values():
            answ.append(fileInst.getFileMetaData())
            if fileInst._asociatedFiles:
                answ.extend(fileInst._asociatedFiles)
        return answ

    def getSource(self, fileId):
        fileGen = self._fileGenerators[fileId]
        return fileGen.getSource()

    def setSource(self, fileId, modSource, isPartialMod = False):
        fileGen = self._fileGenerators[fileId]
        fileGen.setSource(modSource, isPartialMod)

    def getFileName(self, fileId):
        return self._fileGenerators[fileId].getFileMetaData()[1]

class vrtDisk:

    def __init__(self, menuthreads=None, addonsettings=None, modifiedcode=None, file=None):
        if file is not None:
            if isinstance(file, basestring):
                file = open(file, 'rb')

            menuthreads = self.initThreadData()
            threadData = json.loads(file.readline())
            menuthreads.setThreadData(*threadData)

            addonsettings = xmlFileWrapper.xmlFileWrapper('Addon_Settings.xml')
            settings = json.loads(file.readline())
            addonsettings.setNonDefaultParams(settings)

            modifiedcode = json.loads(file.readline())

        self._menuthreads = menuthreads or self.initThreadData()
        self._addonSettings = addonsettings or xmlFileWrapper.xmlFileWrapper('Addon_Settings.xml')
        self._filegenerator = FileGenerator(self._addonSettings, self._menuthreads)
        self._changeMngr = None
        self._reportChange = True
        self.hasChange = False
        self._filegenerator.modSourceCode = modifiedcode or []
        self.path_cache = {}

    def initThreadData(self):
        xbmcMenu = menuThreads.menuThreads()
        params = {'url':'https://www.youtube.com/watch?v=aCWRPqLt0wE', 'regexp':r'"adaptive_fmts":"(?P<youtube_fmts>[^"]+)"', 'compflags':'re.DOTALL'}
        xbmcMenu.setThreadParams('media', params)

        xbmcMenu.lstChanged = []  # Se borra cualquier actualización del árbol
                                  # porque este en este punto no existe
        return xbmcMenu


    def setChangeMngr(self, callbackfunction):
        self._changeMngr = callbackfunction

    def reportChanges(self):
        if self._reportChange and self._changeMngr:
            self._changeMngr(True)

    def exists(self, fileName):
        addonTemplate = [x[0] for x in self.getAddonTemplate()[1:]]
        return fileName[5:].replace(os.path.sep, '/') in addonTemplate

    def setVrtDiskData(self, newsettings=None, threaddata=None, modifiedcode=None):
        threaddata = threaddata or self.initThreadData().getThreadData()
        self._menuthreads.setThreadData(*threaddata)

        newsettings = newsettings or {}
        if newsettings.has_key('reset'):
            toReset = addonSettings.pop('reset')
            for key in toReset:
                newsettings.pop(key)
        self._addonSettings.setNonDefaultParams(newsettings)
        fileGenerator = self.getFileGenerator()
        fileGenerator.getFileInstances()

        modifiedcode = modifiedcode or []
        coder = self.getFileGenerator()
        coder.modSourceCode = modifiedcode

    def getVrtDiskData(self):
        settings = self._addonSettings.getNonDefaultParams()
        threadData = self._menuthreads.getThreadData()
        coder = self.getFileGenerator()
        modsource = coder.modSourceCode
        return (settings, threadData, modsource)

    def addon_id(self):
        return self._addonSettings.getParam('addon_id')

    def getAddonTemplate(self):
        addonTemplate = self.getAddonStruct()
        rootId = self.addon_id()
        addonTemplate[0] = rootId + SEP + addonTemplate[0].partition(SEP)[2]
        for elem in addonTemplate[1:]: elem[0] = rootId + SEP + elem[0]
        return addonTemplate

    def getAddonStruct(self):
        addonSettings = self._addonSettings
        fileGenerator = self._filegenerator
        getData = lambda setting: [map(lambda x: x.strip(), elem.split(',')) for elem in setting.split('|')]
        getFileLoc = lambda fileLoc, fileName:os.path.join(os.path.normpath(fileLoc), fileName).replace(os.sep,'/').replace('./','')
        addonTemplate = [self.addon_id()]
        if not addonSettings.getParam('generatedFiles'):
            generatedFiles = fileGenerator.listFiles()
        else:
            generatedFiles = getData(addonSettings.getParam('generatedFiles'))

        for elem in generatedFiles:
            fileId, fileName, fileLoc, isEditable = elem
            fileLoc = getFileLoc(fileLoc,fileName)
            addonTemplate.append([fileLoc, {'type':'genfile', 'editable':isEditable, 'source':fileId, 'inspos':'1.0'}])

        optionalfiles = [('addon_icon', 'icon.png'),        ('addon_fanart', 'fanart.jpg')]

        for key, fileName in optionalfiles:
            source = addonSettings.getParam(key)
            if source:
                addonTemplate.append([fileName, {'type':'file', 'editable':True, 'source':source}])

        addon_resources = addonSettings.getParam('addon_resources')
        resources = getData(addon_resources) if addon_resources else []
        for elem in resources:
            try:
                fileName, fileLoc, isEditable, source = elem
            except:
                continue
            fileLoc = getFileLoc(fileLoc,fileName)
            isEditable = isEditable or 'True'
            source = source or fileName
            addonTemplate.append([fileLoc, {'type':'file', 'editable':isEditable, 'inspos':'1.0', 'source':source}])

        dependencies = getData(addonSettings.getParam('addon_requires'))
        for elem in dependencies:
            fileName, fileVer, fileOp = elem
            fileLoc = getFileLoc('Dependencies',fileName)
            addonTemplate.append([fileLoc, {'type':'depdir', 'editable':False, 'source':fileName, 'inspos':fileVer}])

        addonTemplate.insert(0,addonTemplate.pop(0) + "/addon.xml")

        return addonTemplate

    def getRequiredDirectories(self):
        addonSettings = self._addonSettings
        reqDirectories = {'point_pluginsource': ['resources/media', 'Dependencies'],
                          'point_module': [addonSettings.getParam('script_library'), 'Dependencies'],
                          'point_repository': ['datadir']}
        reqdirs = set()
        for key, dirs in reqDirectories.items():
            bFlag = addonSettings.getParam(key)
            if isinstance(bFlag, basestring):
                bFlag = bFlag == 'true'
            if bFlag:
                reqdirs.update(dirs)
        directories = []
        dirtypes = {'Dependencies':'depdir', 'datadir':'repdatadir'}
        for key in sorted(reqdirs):
            dirtype = dirtypes.get(key, 'reqdir')
            directories.append([key, {'type': dirtype, 'editable':False, 'source':''}])

        rootId = self.addon_id()
        directories = [(rootId + SEP + key, value) for key, value in directories]

        return directories


    def modResources(self, modType, fileName, location, isEditable, fileSource):
        addonResources = self._addonSettings.getParam('addon_resources')
        addonResources = map(lambda x: x.split(','), addonResources.split('|'))
        addonid = len(self.addon_id()) + 1
        if modType == 'insert':
            location = location[addonid:]
            nFileSource = os.path.normpath(fileSource)
            if nFileSource.startswith(os.getcwd()): fileSource = fileSource[len(os.getcwd())+1:]
            addonResources.append([fileName, location, str(isEditable), fileSource])
        elif modType == 'delete':
            fileName = fileName[addonid:]
            trnfunc = lambda x: not SEP.join([x[1], x[0]]).startswith(fileName)
            addonResources = filter(trnfunc, addonResources)
        elif modType == 'rename':
            fileName = fileName[addonid:]
            replName = SEP.join([fileName.rpartition(SEP)[2], fileSource])
            for item in addonResources:
                itemid = SEP.join([item[1], item[0]])
                if itemid == fileName:
                    item[0] = fileSource
                    break
                if item[1].startswith(fileName):
                    item[1] = item[1].replace(fileName, replName)
            pass
        addonResources = '|'.join([','.join(item) for item in addonResources])
        self._addonSettings.settings['addon_resources'] = addonResources
        self._addonSettings.refreshFlag = True
        self.reportChanges()

    def modDependencies(self, modType, dependency, version):
        addonRequires = self._addonSettings.getParam('addon_requires')
        if modType == 'insert':
            pattern = '\|* *' + dependency + ',[^|]+'
            if not re.search(pattern, addonRequires):
                addonRequires = '|'.join([addonRequires,','.join([dependency, version, ''])])
        elif modType == 'delete':
            dependency = dependency.rpartition(SEP)[2]
            pattern = '\|* *' + dependency + ',[^|]+'
            toRep = re.compile(pattern)
            addonRequires = toRep.sub('', addonRequires)
        self._addonSettings.settings['addon_requires'] = addonRequires
        self.reportChanges()

    def getApiGenerator(self):
        apiGenerator = self.getFileGenerator()
        return apiGenerator.getAddonModule()

    def getFileGenerator(self, fileId=None):
        return self._filegenerator

    def getGeneratorFor(self, fileId):
        fgen = self.getFileGenerator()
        return fgen._fileGenerators[fileId]

    def zipFileStr(self):
        fp = StringIO.StringIO()
        errMsg = ''
        addonFiles = self.listAddonFiles()
        if self._addonSettings.getParam('point_repository'):
            repodir = '%s/datadir' % self.addon_id()
            addonFiles = filter(lambda x: not x[0].startswith(repodir), addonFiles)
        with zipfile.ZipFile(fp, 'w') as zipFile:
            for elem in addonFiles:
                dstFile, mode, srcFile = elem
                try:
                    fileContent = self.getPathContent((mode, srcFile))
                    if not fileContent: continue
                    zipFile.writestr(dstFile, fileContent)
                except:
                    errFile = dstFile.rpartition('\\')[2]
                    errMsg += errFile + '\n'
        if errMsg: raise Exception(errMsg)
        fp.seek(0)
        return fp

    def sincronizeRepoTo(self, host, user, password, datadir='/public_html/'):
        addonSettings = self._addonSettings
        if not addonSettings.getParam('point_repository'): return
        net = network.network()
        checksum_dir = addonSettings.getParam('repository_checksum')
        try:
            repo_checksum = net.openUrl(checksum_dir)[0]
        except:
            repo_checksum = ''
        repository_checksum =  '%s/datadir/addons.xml.md5' % self.addon_id()
        repository_checksum = self.getPathContent(repository_checksum)
        if repo_checksum == repository_checksum.decode('utf-8'):
            return tkMessageBox.showinfo('Sincronize Repository', 'Repository is updated')

        pattern = r'(?#<addon id=id name=name version=version>)'
        info_dir = addonSettings.getParam('repository_info')
        try:
            repo_info = net.openUrl(info_dir)[0]
        except:
            repo_info = []
        else:
            repo_info = CustomRegEx.findall(pattern, repo_info)
            repo_info = [item[0] + '+' + item[2] for item in repo_info]
        repository_info =  '%s/datadir/addons.xml' % self.addon_id()
        repository_info = self.getPathContent(repository_info)
        real_info = CustomRegEx.findall(pattern, repository_info)
        real_info = [item[0] + '+' + item[2] for item in real_info]

        toDelete = set(repo_info).difference(real_info)
        toDelete = [item[:item.find('+')]  for item in toDelete]
        toAdd = set(real_info).difference(repo_info)
        toAdd = [item[:item.find('+')]  for item in toAdd]
        toUpdate = set(toAdd).intersection(toDelete)
        toAdd = set(toAdd).difference(toUpdate)
        toDelete = set(toDelete).difference(toUpdate)
        toRename = set()

        ftp = ftplib.FTP(host=host, user=user, passwd=password)
        repository_datadir = addonSettings.getParam('repository_datadir')
        repository_datadir = urlparse.urlparse(repository_datadir).path.strip('/')
        relativedir = repository_datadir.strip('/')
        dirname = '/' + datadir.strip('/')
        while relativedir:
            adir, relativedir = relativedir.split('/', 1)
            dirname += '/' + adir
            try:
                ftp.cwd(dirname)
            except:
                ftp.mkd(dirname)

        ftp.cwd(datadir)
        for item in toUpdate:
            files = filter(lambda x: x not in ['.', '..'], ftp.nlst(item))
            map(lambda x: ftp.rename(item + '/' + x, item + '/' + x + '.bak'), files)

        datadirLst= ftp.nlst()
        addonFiles = self.listAddonFiles()
        repodir = '%s/datadir' % self.addon_id()
        addonFiles = filter(lambda x: x[0].startswith(repodir), addonFiles)
        fltfnc = lambda x: os.path.dirname(x[0][len(repodir)+1:]) in toAdd.union(toUpdate)
        addonFiles = sorted(filter(fltfnc, addonFiles))

        moddir = set()
        for elem in addonFiles:
            dstFile, mode, srcFile = elem
            try:
                if not os.path.isdir(srcFile):
                    if srcFile.endswith('.zip'):
                        fp = StringIO.StringIO()
                        with open(srcFile, 'rb') as f:
                            fp.write(f.read())
                    else:
                        try:
                            fileContent = self.getPathContent((mode, srcFile))
                        except:
                            fileContent = None
                        if not fileContent: continue
                        if srcFile.endswith('.pck'):
                            fobj = fileContent
                            fp = fobj.zipFileStr()
                        else:
                            fp = StringIO.StringIO(fileContent)
                else:
                    excludedext= ('.pyo', '.pyc')
                    fp = StringIO.StringIO()
                    rootDir = os.path.dirname(srcFile)
                    zfile = zipfile.ZipFile(fp, 'w')
                    for dirname, subshere, fileshere in os.walk(srcFile):
                        for fname in fileshere:
                            if os.path.splitext(fname)[1] in excludedext: continue
                            fname = os.path.join(dirname, fname)
                            aname = os.path.relpath(fname, rootDir)
                            zfile.write(fname, aname)
                    zfile.close()
                fp.seek(0)
                basedir, filename = os.path.split(dstFile)
                basedir = basedir[len(repodir)+1:]
                if basedir not in datadirLst:
                    datadirLst.append(ftp.mkd(basedir))
                ftp.storbinary('STOR %s/%s' % (basedir, filename), fp)
                moddir.add(basedir)
            except:
                toDelete = moddir.difference(toUpdate)
                toRename = toUpdate.difference(moddir)
                bSuccess = False
            else:
                toRename = toUpdate
                bSuccess = True

        if not bSuccess:
            for item in toRename:
                files = filter(lambda x: x not in ['.', '..'] and not x.endswith('.bak'), ftp.nlst(item))
                map(lambda x: ftp.delete(item + '/' + x), files)
            for item in toRename:
                files = filter(lambda x: not x.endswith('.bak'), ftp.nlst(item))
                map(lambda x: ftp.rename(item + '/' + x, item + '/' + x[:-4]), files)
            return tkMessageBox('Sincronize Repo', 'While updating the repository addons '
                                                   'an error has ocurred')

        repo_pairs = [(info_dir, 'addons.xml', repository_info),
                      (checksum_dir, 'addons.xml.md5', repository_checksum)]
        try:
            for itemdir, itemname, itemcontent in repo_pairs:
                itemdir = '/' + datadir.strip('/') + '/' + urlparse.urlparse(itemdir).path.lstrip('/')
                ftp.rename('/'.join(itemdir, itemname), '/'.join(itemdir, itemname + '.bak'))
                fp = StringIO.StringIO(itemcontent)
                ftp.storbinary('STOR %s/%s' % (itemdir, itemname), fp)
        except:
            for itemdir, itemname, itemcontent in repo_pairs:
                try:
                    ftp.delete('/'.join(itemdir, itemname))
                except:
                    break
                else:
                    ftp.rename('/'.join(itemdir, itemname + '.bak'), '/'.join(itemdir, itemname))
            for item in toRename:
                files = filter(lambda x: x not in ['.', '..'] and not x.endswith('.bak'), ftp.nlst(item))
                map(lambda x: ftp.delete(item + '/' + x), files)
            for item in toRename:
                files = filter(lambda x: not x.endswith('.bak'), ftp.nlst(item))
                map(lambda x: ftp.rename(item + '/' + x, item + '/' + x[:-4]), files)
            return tkMessageBox('Sincronize Repo', 'While updating the repository info/checksum '
                                                   'an error has ocurred')
        for item in toRename:
            files = filter(lambda x: not x.endswith('.bak'), ftp.nlst(item))
            map(lambda x: ftp.delete(item + '/' + x), files)
        for item in toDelete:
            files = filter(lambda x: x not in ['.', '..'], ftp.nlst(item))
            map(lambda x: ftp.delete(item + '/' + x), files)
            ftp.rmd(item)
        return tkMessageBox('Sincronize Repo', 'Repository successfully updated')

    def repositoryFile(self):
        if not self._addonSettings.getParam('point_repository'): return
        addonFiles = self.listAddonFiles()
        repodir = '%s/datadir' % self.addon_id()
        addonXmlFile = '%s/datadir/addon.xml' % self.addon_id()
        addonXmlMd5File = '%s/datadir/addon.xml.md5' % self.addon_id()
        addonFiles = filter(lambda x: x[0].startswith(repodir), addonFiles)
        datadir = self._addonSettings.getParam('repository_datadir')
        redirect = {addonXmlFile: self._addonSettings.getParam('repository_info'),
                    addonXmlMd5File: self._addonSettings.getParam('repository_checksum')}
        errMsg = ''
        for elem in addonFiles:
            dstFile, mode, srcFile = elem
            trnDstFile = dstFile.replace(repodir, datadir)
            dstFile = redirect.get(dstFile, trnDstFile)
            try:
                if not os.path.isdir(srcFile):
                    if srcFile.endswith('.zip'):
                        fp = StringIO.StringIO()
                        with open(srcFile, 'rb') as f:
                            fp.write(f.read())
                    else:
                        fileContent = self.getPathContent((mode, srcFile))
                        if not fileContent: continue
                        if srcFile.endswith('.pck'):
                            fobj = fileContent
                            fp = fobj.zipFileStr()
                        else:
                            fp = StringIO.StringIO(fileContent)
                else:
                    excludedext= ('.pyo', '.pyc')
                    fp = StringIO.StringIO()
                    rootDir = os.path.dirname(srcFile)
                    zfile = zipfile.ZipFile(fp, 'w')
                    for dirname, subshere, fileshere in os.walk(srcFile):
                        for fname in fileshere:
                            if os.path.splitext(fname)[1] in excludedext: continue
                            fname = os.path.join(dirname, fname)
                            aname = os.path.relpath(fname, rootDir)
                            zfile.write(fname, aname)
                    zfile.close()
                fp.seek(0)
                try:
                    basedir = os.path.dirname(dstFile)
                    os.makedirs(basedir)
                except:
                    pass
                with open(dstFile, 'wb') as f:
                    shutil.copyfileobj(fp, f)
            except:
                errFile = dstFile.rpartition('\\')[2]
                errMsg += errFile + '\n'
        if errMsg: raise Exception(errMsg)

    def mapVrtDisk(self, name=None):
        if name is None:
            try:
                import xbmc
            except Exception as e:
                tkMessageBox.showerror('Addon creation', str(e))
            name = xbmc.translatePath('special://home/addons')
        addonName, addonId = self._addonSettings.getParam('addon_name'),self.addon_id()
        try:
            fp = self.zipFileStr()
        except Exception as e:
            errMsg = 'During addon creation for ' + addonName + ' (' + addonId + ') , the following source files were not found: \n' + str(e)
            return tkMessageBox.showerror('Addon creation', errMsg)
        with contextlib.closing(fp):
            try:
                if os.path.exists(name) and os.path.isdir(name):
                    zfile = zipfile.ZipFile(fp, 'r')
                    zfile.extractall(name)
                else:
                    with open(name, 'wb') as f:
                        shutil.copyfileobj(fp, f)
            except Exception as e:
                tkMessageBox.showerror('Addon creation', str(e))
            else:
                errMsg = 'Addon for ' + addonName + ' (' + addonId + ') succesfully created'
                tkMessageBox.showinfo('Addon creation', errMsg)
        self.repositoryFile()

    def listAddonFiles(self, name = None):
        fileList = self.getAddonTemplate()[1:]
        fileList = [(filePath, fileAttr['type'], fileAttr['source']) for filePath, fileAttr in fileList if 'Dependencies' not in filePath]
        return fileList         #addonListFiles

    def _getTypeSource(self, path):
        path = os.path.normpath(path)
        if path.startswith('vrt:'):
            path = os.path.relpath(path, 'vrt:')
        path = path.replace(os.path.sep, '/')
        fileMapping = dict(self.getAddonTemplate()[1:])
        test = fileMapping.get(path, None)
        if not test: raise IOError
        return test['type'], test['source']

    def getPathContent(self, path):
        if isinstance(path, basestring):
            itype, filesource = self._getTypeSource(path)
        else:
            itype, filesource = path

        filesource = filesource.split('::')
        if itype in ('file', 'depfile'):
            filename = filesource[0]
            try:
                filename = urllib.pathname2url(filename)
            except:
                pass
            urllib.URLopener.version = 'Mozilla/5.0 (Windows NT 6.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36'
            opener = urllib.FancyURLopener()
            f = opener.open(filename)
            source = f.read()
            ContentType = f.headers['Content-Type']
            m = re.match(r'(\w+)/(\w+)(?:; charset=([-\w]+))*', ContentType)
            if m.group(3) and m.group(3).lower() != 'utf-8':
                source = source.decode(m.group(3)).encode('utf-8')
            f.close()

            rawcontent = source
            rawtype = ''
            while filesource:
                filetype, filesource = filesource[0], filesource[1:]
                if not rawtype:
                    fp = StringIO.StringIO(rawcontent)
                    if filetype.endswith('.zip'):
                        rawcontent = zipfile.ZipFile(fp, 'r')
                    elif filetype.endswith('.pck'):
                        rawcontent = vrtDisk(file=fp)
                    rawtype = os.path.splitext(filetype)[1]
                else:
                    if rawtype == '.zip':
                        rawcontent = rawcontent.read(filetype)
                    elif rawtype == '.pck':
                        rawcontent = rawcontent.getPathContent(filetype)
                    if rawtype in ['.zip', '.pck']:filesource.insert(0, filetype)
                    rawtype = ''
            source = rawcontent

        elif itype == 'genfile':
            file_id, filesource = filesource[0], filesource[1:]
            filesource = filesource or ('getSource',)
            f = operator.methodcaller(*filesource)
            obj = self.getGeneratorFor(file_id)
            source = f(obj)
            if source is not None: source = source.encode('utf-8')
        return source

class mountVrtDisk(vrtDisk):

    def installPathHook(self):
        """
        Install a KodiScriptImporter instance as meta path or path hook

        meta_path:  bool - Set the instance as a META PATH importer (meta_path = True) or
                    as a PATH HOOK (meta_path = False
        Example:
            - import KodiScriptImporter as ksi
            - importer = ksi.KodiScriptImporter()           # For Windows x86 users
            - importer.install(False)                       # Install as a path hook
        Note:
            Define a self.logger in your __main__ script to view messages from the logging in this module
        """
        class trnClass:
            def __init__(aninst, path):
                if path.startswith('vrt:%s%s' % (os.path.sep, self.addon_id())):
                    aninst.path = path
                else:
                    raise ImportError

            def find_module(aninst, fullname, path = None):
                if not path or path[0].startswith(aninst.path):
                    modules = ['vrt:/%s' % x[0] for x in self.getAddonTemplate() if x[0].endswith('.py')]
                    modules = '\n'.join(modules)
                    pathStr = path[0] if path else '.+?'
                    pattern = r'^{0}/(?:{1}.py|{1}/__init__.py)$'.format(pathStr, fullname)
                    m = re.search(pattern, modules, re.MULTILINE)
                    if m:
                        self.path_cache[fullname] = os.path.normpath(m.group())
                        return self

            def __getattr__(aninst, attr):
                return getattr(self, attr)

        sys.path_hooks.append(trnClass)

    def addon_library_path(self):
        path = os.path.normpath('vrt:/%s/addon.xml' % self.addon_id())
        rawData = self.get_data(path)
        data = rawData.encode('utf-8')
        match = CustomRegEx.search(r'(?#<extension point="xbmc.python.pluginsource" library=library>)', data)
        return match.group(1)

    def get_source(self, fullname):
        path = self.path_cache.get(fullname)
        return self.getPathContent(path).encode('utf-8')

    def get_code(self, fullname):
        source = self.get_source(fullname)
        type, filename = self._getTypeSource(self.path_cache[fullname])
        if type != 'file': filename = self.path_cache[fullname]
        return compile(source, filename, 'exec', dont_inherit=True)
        pass

    def get_data(self, path):
        if not path.startswith('vrt:%s%s' % (os.path.sep, self.addon_id())): raise IOError
        try:
            source = self.getPathContent(path)
        except Exception as e:
            raise IOError
        return source

    def open(self, name, mode='r', buffering=-1):
        try:
            source = self.get_data(name)
        except IOError:
            return open(name, mode, buffering)
        else:
            return contextlib.closing(StringIO.StringIO(source))

    def is_package(self, fullname):
        path = self.path_cache[fullname]
        return path.endswith('__init__.py')

    def load_module(self, fullname):
        if fullname in sys.modules:
            mod = sys.modules[fullname]
        else:
            mod = sys.modules.setdefault(fullname, imp.new_module(fullname))
        mod.__file__ = self.path_cache[fullname]
        mod.__name__ = fullname
        mod.__path__ = os.path.dirname(mod.__file__)
        mod.__loader__ = self
        mod.__package__= '.'.join(fullname.split('.')[:-1])
        if self.is_package(fullname):
            mod.__path__ = [mod.__path__]
        source = self.get_code(fullname)
        exec source in mod.__dict__
        mod.__dict__['open'] = self.open
        return mod




if __name__ == '__main__':
    # cargar el archivo de prueba
    name = os.path.abspath(r'./AddonsData/meta_project_free_tv.pck')

    test = 'vrtDisk'
    if test == 'vrtDisk':
        mydisk = vrtDisk(file=name)
        try:
            fp = mydisk.zipFileStr()
        except Exception as  errMsg:
            print errMsg
        else:
            mydisk.mapVrtDisk(r'C:\testFiles\pic\test\plugin.test.tests.zip')
    elif test == 'mountVrtDisk':
        import json
        import menuThreads
        import xmlFileWrapper

        with open(name,'rb') as f:
            kodiThreadData = json.loads(f.readline())
            settings = json.loads(f.readline())
            modifiedCode = json.loads(f.readline())

        xbmcThreads = menuThreads.menuThreads()
        xbmcThreads.setThreadData(*kodiThreadData)
        addonSettings = xmlFileWrapper.xmlFileWrapper('Addon_Settings.xml')
        addonSettings.setNonDefaultParams(settings)

        myVrtDisk = mountVrtDisk(xbmcThreads, addonSettings)
        coder = myVrtDisk.getApiGenerator()
        coder.modSourceCode = modifiedCode or {}

        myVrtDisk.installPathHook()
        sys.path.insert(0, r'vrt:\plugin.video.projectfreetvide\resources\lib')
        import adgMesh
        print dir(adgMesh)
        pass
