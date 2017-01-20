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
import tkFileDialog
import sys
import imp
import urllib
import contextlib
import StringIO
import menuThreads
import xmlFileWrapper
import json

SEP = '/'
IMAGEFILES = ['.bmp', '.dcx', '.eps', '.gif', '.im', '.jpg', '.jpeg', '.pcd', '.pcx', '.pdf', '.png', '.ppm', '.psd', '.tiff', '.xbm', '.xpm']

class FileGenerator(object):
    def __init__(self, addonSettings, addonThreads):
        self._fileGenerators = {}
        self.editableFiles = []
        fileGen = addonSettings.getParam('filegen') or 'Basic'
        module = __import__('Coders.%s' % fileGen)
        module = getattr(module, fileGen)
        fileObjets = module.__dict__
        fileClass = [fileGen for fileGen in fileObjets.keys() if fileGen.startswith('addonFile_')]
        for fileGen in fileClass:
            fileObj = fileObjets[fileGen](addonSettings, addonThreads)
            self.addFile(fileObj)
            if fileObj.isEditable: self.editableFiles.append(fileObj.fileId)
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

    def listFiles(self):
        return [ value.getFileMetaData() for value in self._fileGenerators.values()]

    def addFile(self, fileObject):
        fileId = fileObject.getFileMetaData()[0]
        self._fileGenerators[fileId] = fileObject

    def getSource(self, fileId):
        fileGen = self._fileGenerators[fileId]
        return fileGen.getSource()

    def setSource(self, fileId, modSource, isPartialMod = False):
        fileGen = self._fileGenerators[fileId]
        fileGen.setSource(modSource, isPartialMod)

    def getFileName(self, fileId):
        return self._fileGenerators[fileId].getFileMetaData()[1]

class vrtDisk:

    def __init__(self, menuthreads=None, addonsettings=None, modifiedcode=None):
        self._menuthreads = menuthreads or menuThreads.menuThreads()
        self._addonSettings = addonsettings or xmlFileWrapper.xmlFileWrapper('Addon_Settings.xml')
        self._filegenerator = FileGenerator(self._addonSettings, self._menuthreads)
        self._changeMngr = None
        self._reportChange = True
        self.hasChange = False
        self._filegenerator.modSourceCode = modifiedcode or []
        self.path_cache = {}

    def setChangeMngr(self, callbackfunction):
        self._changeMngr = callbackfunction

    def reportChanges(self):
        if self._reportChange and self._changeMngr:
            self._changeMngr(True)

    def exists(self, fileName):
        addonTemplate = [x[0] for x in self.getAddonTemplate()[1:]]
        return fileName[5:].replace(os.path.sep, '/') in addonTemplate

    def setVrtDiskData(self, newsettings='', threaddata='', modifiedcode=''):
        if threaddata:
            threaddata = json.loads(threaddata)
            self._menuthreads.setThreadData(*threaddata)
        if newsettings:
            newsettings = json.loads(newsettings)
            self._addonSettings.setNonDefaultParams(newsettings)
        if modifiedcode:
            coder = self.getApiGenerator()
            modifiedcode = json.loads(modifiedcode)
            coder.modSourceCode = modifiedcode

    def getVrtDiskData(self):
        settings = json.dumps(self._addonSettings.getNonDefaultParams())
        threadData = json.dumps(self._menuthreads.getThreadData())
        coder = self.getApiGenerator()
        modsource = json.dumps(coder.modSourceCode)
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

        rootFiles = [('addon_icon', 'icon.png'),        ('addon_fanart', 'fanart.jpg')]

        for key, fileName in rootFiles:
            source = addonSettings.getParam(key)
            if source:
                addonTemplate.append([fileName, {'type':'file', 'editable':True, 'source':source}])

        resources = getData(addonSettings.getParam('addon_resources'))
        for elem in resources:
            fileName, fileLoc, isEditable, source = elem
            fileLoc = getFileLoc(fileLoc,fileName)
            isEditable = isEditable or 'True'
            source = source or fileName
            addonTemplate.append([fileLoc, {'type':'file', 'editable':isEditable, 'inspos':'1.0', 'source':source}])

        dependencies = getData(addonSettings.getParam('addon_requires'))
        for elem in dependencies:
            fileName, fileVer, fileOp = elem
            fileLoc = getFileLoc('Dependencies',fileName)
            addonTemplate.append([fileLoc, {'type':'depdir', 'editable':False, 'source':fileName, 'inspos':fileVer}])

        addonTemplate.insert(0,addonTemplate.pop(0) + "/" + addonSettings.getParam('addon_module'))
        return addonTemplate

    def modResources(self, modType, fileName, location, isEditable, fileSource):
        addonResources = self._addonSettings.getParam('addon_resources')
        if modType == 'insert':
            location = location.partition(SEP)[2]
            nFileSource = os.path.normpath(fileSource)
            if nFileSource.startswith(os.getcwd()): fileSource = fileSource[len(os.getcwd())+1:]
            addonResources = '|'.join([addonResources, ','.join([fileName, location, str(isEditable), fileSource])])
        elif modType == 'delete':
            fileName = fileName.rpartition(SEP)[2]
            pattern = '\|* *' + fileName + ',[^|]+'
            toRep = re.compile(pattern)
            addonResources = toRep.sub('', addonResources)
        elif modType == 'rename':
            fileName = fileName.rpartition(SEP)[2]
            addonResources = addonResources.replace(fileName + ',', fileSource + ',')
            pass
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

    def getFileGenerator(self):
        return self._filegenerator

    def mapVrtDisk(self, name=None):
        import xbmc
        errMsg = ''
        if name:
            zipFile = zipfile.ZipFile(name, 'w')
            copySrcFile = zipFile.write
            genFileFromStr = zipFile.writestr
        else:
            if xbmc.special_home != self._addonSettings.getParam('appdir_xbmchome'):
                xbmc.special_home = self._addonSettings.getParam('appdir_xbmchome')
            baseDirectory = xbmc.translatePath('special://home/addons')
            if not os.path.exists(baseDirectory):
                xbmc.special_home = special_home = tkFileDialog.askdirectory(title='Enter directory for special://home/addons')
                nonDefParam = self._addonSettings.getNonDefaultParams()
                nonDefParam['appdir_xbmchome'] = special_home
                self._addonSettings.setNonDefaultParams(nonDefParam)
                baseDirectory = xbmc.translatePath('special://home/addons')
            copySrcFile = shutil.copyfile
        addonFiles = self.listAddonFiles(name)
        for elem in addonFiles:
            dstFile, mode, srcFile = elem
            if not name:
                dstFile = os.path.normpath(os.path.join(baseDirectory, dstFile))
                dstDirectory = os.path.dirname(dstFile)
                if not os.path.exists(dstDirectory): os.makedirs(dstDirectory)
            try:
                if mode == 'f':
                    copySrcFile(srcFile, dstFile)
                elif mode == 's':
                    srcFile = self._filegenerator.getSource(srcFile)
                    if not srcFile: continue
                    if name:
                        genFileFromStr(dstFile, srcFile)
                    else:
                        with open(dstFile,'w') as wfile:
                            wfile.write(srcFile)
            except:
                errFile = dstFile.rpartition('\\')[2]
                errMsg += errFile + '\n'
        if name: zipFile.close()
        addonId = self.addon_id()
        addonName = self._addonSettings.getParam('addon_name')
        if errMsg:
            errMsg = 'During addon creation for ' + addonName + ' (' + addonId + ') , the following source files were not found: \n' + errMsg
            tkMessageBox.showerror('Addon creation', errMsg)
        else:
            errMsg = 'Addon for ' + addonName + ' (' + addonId + ') succesfully created'
            tkMessageBox.showinfo('Addon creation', errMsg)

    def listAddonFiles(self, name = None):
        fileList = self.getAddonTemplate()[1:]
        fileList = [(filePath, fileAttr['type'], fileAttr['source']) for filePath, fileAttr in fileList if 'Dependencies' not in filePath]
        addonListFiles = []
        for filePath, itype, source in fileList:
            itype = {'file':'f', 'genfile':'s'}[itype]
            if type == 's':
                source = self._filegenerator.getSource(source)
            else:
                if urllib.splittype(source)[0] in ['http', 'https', 'ftp']:
                    urllib.URLopener.version = 'Mozilla/5.0 (Windows NT 6.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36'
                    (source, HttpMessage) = urllib.urlretrieve(source)
            addonListFiles.append((filePath, itype, source))
        return addonListFiles

    def _getTypeSource(self, path):
        path = os.path.normpath(path)
        path = path[5:].replace(os.path.sep, '/')
        fileMapping = dict(self.getAddonTemplate()[1:])
        test = fileMapping.get(path, None)
        if not test: raise IOError
        return test['type'], test['source']

    def getPathContent(self, path):
        type, filename = self._getTypeSource(path)
        if type == 'file':
            if os.path.splitdrive(filename)[0]:
                with open(filename, 'rb') as f:
                    source = f.read()
            else:
                f = urllib.urlopen(filename)
                source = f.read()
                f.close()
        elif type == 'genfile':
            file_id = filename
            fgen = self.getFileGenerator()
            source = fgen._fileGenerators[file_id].getSource()
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
    import json
    import menuThreads
    import xmlFileWrapper

    name = os.path.abspath(r'./AddonsData/path_hook_test.pck')
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
