'''
Created on 13/10/2014

@author: Alex Montes Barrios
'''

import sys, os
import re

special_xbmc = ''
special_home = ''

def translatePath(path):
    """
    --Returns the translated path.

    path : string or unicode - Path to format

    *Note, Only useful if you are coding for both Linux and Windows.
    e.g. Converts 'special://masterprofile/script_data' -> '/home/user/XBMC/UserData/script_data' on Linux.

    example:
        - fpath = xbmc.translatePath('special://masterprofile/script_data')
        :type path: string or unicode
    """
    specialProtocol = {
                       'special://temp':'special://home/cache',
                       'special://masterprofile':'special://home/userdata',
                       'special://profile':'special://masterprofile',
                       'special://userdata':'special://masterprofile',
                       'special://database':'special://masterprofile/Database',
                       'special://thumbnails':'special://masterprofile/Thumbnails',
                       'special://musicplaylists':'special://profile/playlists/music',
                       'special://videoplaylists':'special://profile/playlists/video',
                       'special://logpath':'special://home',
                       'special://skin':'special://xbmc/addons'
                       }

    if sys.platform[:3] == 'win':
        specialProtocol['special://xbmc'] = special_xbmc or os.path.join(os.path.expandvars("$PROGRAMFILES"), "Kodi")
        specialProtocol['special://home'] = special_home or os.path.join(os.path.expandvars("$APPDATA"), "Kodi")
    elif not (special_home or special_xbmc):
        raise Exception('You must define the vars xbmc.special_xbmc (special://xbmc) and xbmc.special_home (special://home)')
    else:
        specialProtocol['special://xbmc'] = special_xbmc
        specialProtocol['special://home'] = special_home

    pattern = 'special://[^\\\\/]+'
    oldPath = ''
    while oldPath != path:
        oldPath = path
        path = re.sub(pattern, lambda x: specialProtocol.get(x.group(), x.group()), oldPath)
    root = re.match(pattern, path)
    if not root: return validatePath(path)
    raise Exception(root.group() + ' is not a special path in KODI')

def validatePath(aPath):
    """
    --Returns the validated path.

    path : string or unicode - Path to format

    *Note, Only useful if you are coding for both Linux and Windows for fixing slash problems.
    e.g. Corrects 'Z://something' -> 'Z:'
    example:
        - fpath = xbmc.validatePath(somepath)
    """
    return os.path.normpath(aPath)
