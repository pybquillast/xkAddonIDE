# Addon IDE
Integrated Development Enviroment for XBMC/KODI addons

## Description
This application is intended to be used in the development of XBMC/KODI addons 
from initial steps to addon installation.

Once you have decided to make an addon for a specific site you have to go through this 
major steps:
1. Site scraping: Find the regexp expresions for the webpages of the site
2. Coding: Write the API for the site
3. Adding media: Icons and thumbnails for the addon.
4. Test: View the addon with XBMC/KODI.
5. Prepare for distribution.

For any of the listed steps, the Addon IDE has an associated view in witch you can edit the 
information for that step. There are four views available:
1. Settings:   Global characteristics of the addon.
2. Design: 
    * Api:         Regexp parser with extended capabilities.
    * Code:        Code generated for the application that can be edited by the user. 
    * Data:        Basic information for a XBMC/KODI folder.
    * Preview:     Shows the folder like XBMC/KODI does.
3. Addon Explorer: Resources for the addon. the user can add images, 
python modules, etc.
4. Test: Mock for XBMC/KODI.
 
## Requirements
This project has been tested in a system with the following characteristics:
- Windows Vista SP2
- Python 2.7.9
- Pillow package
- KodiStubs package

## Installation
- Clone the repository to a directory in your system

## Running the application
If you clone the repository, for example, to the  directory **c:/addonide** in your system:
- python c:/addonide/XbmcAddonIDE.py
- In the first run, the application will require that you provide the location for
  the module KodiScriptImporter which is located in the KodiImporter folder of the
  KodiStubs package
- The splash screen is presented
- The application loads the default.pck file. This file is an empty project.

## The Basics
XBMC/KODI display information in logical units named Folder. Each folder display a list of
 items that can redirect the application to a new folder or a resource that can be displayed 
 by XBMC/KODI player.
 
We can say that an addon is a navigation through folder views until you reach a playable resource.

With Addon IDE each folder of the addon is represented as a node in one of two special trees. 
*The list tree*, with root in the "**rootmenu**" node, that shows the folders that are constructed 
by the addon itself. *The weblist tree*, with root in the "**media**" node, that shows the folders 
that are constructed by scrapping a web site. In the list tree, the information flows from parent 
to child and in the weblist tree the information flows from child to parent. The information flows
 from the list tree to the weblist tree through an entity call a "*link*".
  
The addon structure can be changed by adding, deleting or renaming the nodes on the list tree 
or the weblist tree. By editing the links you change the flow of information from the list to 
the weblist trees.

To start developing your addon, is neccesary to know the steps required to modify the list 
and the weblist trees that make up the addon. To do that, you can follow the 
tutorials, study the examples and finally, read the description of the views.      

## Examples
- *HelloWorld.pck*: Final version of the Hello World tutorial.
- *IdeTutorial01.pck*: Final version of the Simple Addon tutorial.
- *meta_project_free_tv.pck*: An IDE version of the famous Project Free TV addon.  
- *vodly.pck*: An IDE version of the famous 1Channel Addon.
- *Opera.pck*: Addon for the content in the Opera Platform Website. 

## The Hello World Addon
The Hello World Addon will display a youtube video in XBMC/KODI. To generate this addon, 
you must go to the **SETTINGS VIEW** (click the Settings button) and click to the Addon Setting
 (right side buttons). Edit the ID and Name fields with the following information:   
  - ID: plugin.video.helloworld
  - Name: Hello World
 
- Click on the Apply Button in the right bottom corner of the screen to save the changes.
  
- Go to "*Menu/Save as*" and give this file he name HelloWorld, click Save button.
 
- Go to "*Menu/MakeZip File*" and point to the location where the application must 
 create the Zip file for importing into XBMC/KODI.
 
 - Start XBMC/KODI and import the addon from the zip file just created. Wait for the addon 
 to be installed.
 
 - In XBMC/KODI go to Video/Addons and start the *Hello World* Addon.
 
### Adding icon.png and fanart.png to the addon
The *Hello World* created doesn't have a fanart or an icon associated to it. To associate an 
icon and a fanart to the addon, we must go to the **SETTINGS VIEW**, click on the resources 
Settings. 
- Click the Icon Button and navigate to the file images/hello_world_icon.png
- Click the Fanart Button and navigat to the file images/hello_world_fanart.jpg
Click on the Apply Button in the right bottom corner of the screen to save the changes.
- Generate the Addon Zip file. And install in XBMC/KODI. Verify that the *Hello World* 
addon display now the fanart and the icon in the XBMC/KODI Video/Add-ons folder.

### Adding an iconImage to a folder item
Once you start the *Hello World* addon, the initial folder only displays one item. This item 
has a *media* label and no icon in it. Now we are going to associate an icon to it.
Go to the **ADDON EXPLORER VIEW** (Button located at the top). Right click the "*resources*" 
folder in the right tree pane. In the pop-up menu navigate to "*Insert New/Dir*" and enter 
"media". The tree must display a new directory with the name "*media*". Right click this 
folder and navigate to "*Insert New/Web Resource*" and enter an Url for an icon image, 
in this example we use 
"*https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcToJildfZrOAZT99oWbPWgCpxFzblrhhar-RGk2agqunSaEujZd"
Now the tree display a file with a odd name under the directory "*media*". Right click in
 the new file and navigate to "*Rename*" and enter "video.png" there. In this point you have 
 edited the addon structure, inserting new directory, inserting a webresource and renaming a resource.
 
The *media* directory was created because the addon search for media files in the 
directory media under the resource directory. Now that we have the media resource required, we 
must associate this to the item folder.
 
Go to the **DESIGN VIEW** and click in the *Data* button (left side of the screen):
- Double click the "*rootmenu*" on the right tree pane. 
- Now the left pane displays the data associated with the *rootmenu*. 
- Under Icons. Check the "*Use custom icons*" checkbutton. On "*Icon names" enter "video.png"
- Click on the Apply Button in the right bottom corner of the screen to save the changes.
- Go to "*Menu/Save*" and save the changes to file.
- Now we are going to try the export to XBMC/KODI. Navigate to "*Menu/Export to XBMC*" and 
click there. The application requires confirmation for this action because the addon already 
exists under XBMC/KODI. Click Accept. Now a success dialog appear.
- In XBMC/KODI execute the *Hello World* addon an verify the new icon added.

## A simple Addon Tutorial
In this tutorial we are going to build an addon that play youtube videos related to Kodi 
Home Theater Software and the python programming language.

* Define the addon Id, addon name and related information:
  - Start the Addon IDE application or if it is already open, navidate to *Menu/New*
  - In the upper left corner of the screen appears the name *default.pck* that is 
  the default file for the application. 
  - Click on the **SETTINGS VIEW** button.
  - On the right side panel, click the *Addon* button.
  - In the **ID** field type: *plugin.video.idetutorial01*.
  - In the **name** field type: *Addon IDE tutorial01*.
  - In the *Provides* section check thet the video checkmark is selected. This is the 
  default and defines the resource that the application can display.
  - Here you can edit any field that you want. The Summary and Disclaimer fields 
  in the *Metadata* section for example.
  - Click the *Apply* button (right bottom) to save this settings. Now in the upper left 
  corner we have 'default.pck**'. The two asterisks means that the file has been modified.
  - Go to the  *Menu/Save as* and give this file the name 'ideTutorial01'.
 
### Inserting a list node.
  - Go to the **DESIGN VIEW** and click in the *Data* button (left side of the screen).
  - Select the *rootmenu* (double click on it). The center panel shows that this node 
  is linked to the *media* weblist node. By default all list nodes are created linked 
  to the *media* weblist node and all weblist nodes are created linked to the *rootmenu*. 
  - Right click the "*rootmenu*" node and in the pop up menu navigate to 
  the *Insert New/Output*.
  - In the dialog that pop ups, type "*kodi*". Here you define node's name   
    that will display this folder. Now the list Tree displays the new node selected. 
  - Double click the "*rootmenu*". Here you can see that the root menu points to the 
  kodi node and not to the media node as before. 
  - Navigate to the menu *Menu/Edit/Insert New/Output*, this is the same as we did with 
  the *kodi* node and type *python*.
  - Go to the *Menu/Save* to save the changes to disk.
  
### Exporting to XBMC/KODI. 
In this point we want to see in the XBMC/KODI application how the proces is going.. The Addon 
IDE application, allows this to be done in three ways:
  - Creating a zip File: Go to the menu *Menu/MakeZip File* and in the "*Zip File to create" navigate 
   to the location where you want this file to be created and give it the name 
   *ide_tutorial01_ver01'. Click the "Ok" button. If all goes well, an info dialog shows
    that the process was succesful. Now go to the XBMC/KODI application and import the 
    zipfile created.
  - Creating a directory under the "*special://home/addons/*" path  with the addon 
  ID: Go to the menu *File/Expot to XBMC*. If all goes well, an info dialog shows that the 
  process was succesful.
  - Go to the **TEST VIEW**. There you can see a list of all video addons installed 
  in XBMC/KODI and in red the *Addon IDE tutorial 01 (test mode)*. Now you can test the new 
  addon as it is in XBMC/KODI.
  
### Inserting a weblist node.
A weblist node generates a XBMC/KODI folder by scraping a particular webpage. We are going to 
need an url and one regexp expression for scraping that webpage.
  - Go to the **DESIGN VIEW** and click in the *Api* button (left side of the screen).
  - Right click the "*media*" node and in the pop up menu navigate to 
  the *Insert New/Source*.
  - In the dialog that pop ups, type "*kodivideos*". 
  - Double click the "*rootmenu*". Here you can see that the root menu points to the 
  kodivideo node. Each weblist node created points to the *rootmenu* node in the list tree.
  - Return to the new created node *kodivideos* by double-clicking on it.
  - In the field *Actual URL*, copy this url *https://www.youtube.com/results?q=kodi*. 
  This webpage display videos from a youtube search for *kodi*.
  - Navigate to *Menu/Edit/Set Url*. Now this is the test url for the *kodivideos* node.
  - In the field *Regexp*, copy this expression (?#<ol class="item-section" .li< .h3.a{href=url *=label} .img{src=iconImage data-thumb=_iconImage_}>*>).
  - Navigate to *Menu/Edit/Set Regexp*. Now this is the regexp expression for *kodivideos* node.
  - To verify that we have set the url and the regexp for the new *kodivideos* weblist, click 
  the *Data* button (left side of the screen) and in the *URL* and *Regexp* fields must appear the 
  information that we just set.
  - Go to "*Menu/Save*" and save the changes.

### Inserting a link between a list node and a weblist.
While in the **DESIGN VIEW**, click in the *Api* button (left side of the screen).
    - Select the *rootmenu* node (double click on it). Now we can see in the left panel 
    that this node has three links: kodi, python and kodivideos. We don't want that the 
    *kodivideos* link be accessible from the *rootmenu* node. We want that it be accessible 
    from the *kodi* node. To solve this problem we must create a link between the *kodi* list 
    node and the *kodivideos* weblist node.
   - Select the *kodi* node. You can see that this node is linked to the *media* node. 
   - Navigate to *Menu/Edit/Insert New/Link*.
   - In the dialog that appears type kodivideos. Now you see that the link from *kodi* 
   node points to *kodivideos*
   - Select the *rootmenu* node. Now the *kodivideos* link has dissapeared.
   - To verify that this works, click in the **PREVIEW** Button (left side of the screen).
   - Like in XBMC/KODI select kodi and then kodivideos. The **PREVIEW** Button start the 
   simulation from the active node (in this case the *rootmenu* weblist node)  
   - Save the changes (Go to menu "*File/Save*")  
 
### Adding a Next Page item to a weblist node.
The test url for the *kodivideos* node, display the first 20 videos in a search for *kodi* 
in youtube, but at the bottom of the page (load the url in a browser) there is links for 
additional pages with the same information.
  - Select the *kodivideos* node (Double click the "*kodivideos*" node). 
  - In the field *Regexp*, copy this expression:
   (?#<a class="yt-uix-button\s+vve-check[^"]+" href=url span.*="Next.+?">).
  - Navigate to *Menu/Edit/Add Footer*. 
  - Save the changes (Go to menu "*File/Save*")

  
##The VIEWS

###The SETTINGS VIEW
This view allows to edit the general parameters for the addon. The parameters are grouped 
in categories thet are shown as bottons in the right pane. This categories are:
 - Addon: Allows to define the following parameters: ID, Name, Version, Provider's Name, 
  Initial script, the type of information that provides (video, audio, image or Executable) 
  and the dependencies for the addon. By default the addon requires the xbmc.python and 
   script.module.urlresolver dependencies.
 - Metadata: Summary, Description, Disclaimer, Language, Platform, License, Forum, Website, 
  Email and Source
 - Resources: Allows to define files to be used for the Icon, Fanart and License. In 
 Addon additional resources, we list all the additional files needed for the addon. By 
 default, the addon gnerated needs the modules BasiFunc.py and CustomRegEx.py 
  
###The DESIGN VIEW
Shows information related to the nodes that make up the addon.
 
**The Api Button**: Divides the middle panel in two panels. 

The top panel, named the browser, display the source code for the url associated to 
the node.
 
In the adress bar (first row of the panel), in addition to urls, you can type the curl 
command for the page you want (At this point only a subset of curl options).
 
The second row of the browser is the regex bar. Here you can type any valid regular 
expression and the result is displayed on the source code of the page. 

The regex bar can process a superset of regex that is design for html/xml content. 
An example of this is the
expression (?#<a href=url *=label>) that is interpreted as "Search for all *a* tags and 
save the *href attribute in the group *url* and the *text in the group *label*".

The results of applying the regexp expression to the source code for the url in the address bar 
is presented in the body of the top panel by highligthing sections of the code in three 
colours: yellow, red and green. The green colour shows the actual match.

In addition to the url in the address bar, the content of the top panel can be provided by 
sources like the clipboard, an external file, an url or a selected url in the content. 
That can be done with the options in the *Menu/Get*.
 
You can navigate throught the results of the regex expression,  by pressing the buttons 
at the left of the regexp field.
 
When you make click in any hyperlink displayed in the body section, the address bar is set to 
the full url indicated by the hyperlink and if there is a processing node, the regexp bar 
is set to the regexp expression of that node. So you can navigate through the api trees 
by its hyperlinks.
  
You can select any section of the source code and by pressing the ZoomIn button (right side of 
the regexp expression), the text widget will display only that particular section. 
Pressing the ZoomIn button with no selection, will display the actual match section 
(green section). To return to the original state, press the same button again 
(now it displays the label "ZoomOut").

The bottom panel, shows a list that display the groups defined by the regexp expression. 

If you select the SPAN flag (regexp bar), additional to the groups you can see the initial 
(posINI) and final position (posFIN) in characters of the regex match in the source 
code (match.span()).
 
By selecting one row of the list, you change the actual match to the section that display that 
information in the source code. 

You can select multiples rows and copy to the  
clipboard (Control-C). To sort the result, press the heading for sort in ascending order, press
 again and sort in descending order.
 
**The Code Button**: Shows the python code that generates the folder associated to the node. You 
  can edit this content and save the changes throught *Menu/Code/Save Code*. When you edit the 
  content generated and save the changes the node is considered to be a locked node and in the 
  tree it is indicated by a lock icon. To restore the initial state for this node you must 
  reset the code by going to *Menu/Code/Reset Code*.
  
**The Data Button**: Shows the information associated to the node. At the top of the panel, it 
 displays the node ID, and if it is a locked node, a lock icon is displayed to the left of 
 the ID. Once you have making the necessesary changes, press the *Apply* button (right bottom)
 or *Discard* to return the initial data. For locked nodes, the *Apply* and *Discard* 
 buttons are shown inactive, so you can make changes but the changes can be saved.
 
**The Preview Button**: Shows a mock for XBMC/KODI for the folder generated for this node. The 
*media* weblist node present the url asociated to the media that is going to be displayed 
 for the XBMC/KODI player, this url can be copied to the clipboard.
 
##The ADDON EXPLORER VIEW
This view shows the structure for the addon. Any file you add/remove in this view, modified the additional 
resources displayed in the *SETTINGS VIEW*. Additional to the external resorces show in the tree,  
this view shows the files generated for this specific addon. In this implementation the addon.xml,
 default.py, settings.xml and changelog.txt are generated. This resources can be editable or not.
 The settings.xml, changelog.txt and default.py files are editable, the addon.xml isn't.
The most important file you can edit in this view, is the default.py file (or any name you 
provide for the initial script in the *SETTINGS VIEW*). In addition to edit the source code 
for a specif node, that can be done in the *Code* section of the *DESIGN VIEW*, you can add any 
 function or class not directly associated to a specific node.

##The TEST VIEW
This view is a mock for the XBMC/KODI application, and starts with the content of the 
Video/Add-ons folder. There you can find the list of all installed addons in XBMC/KODI. 
The addon to be tested is showed in red and it is associated with the Addon IDE and test the 
actual state of the addon. It is not neccesary to save the changes to test the addon.
You can try the others addons installed but, at this point, only the addons where the xbmcgui  
module isn't required can be played.

    
   
     