# iLEAPP

iOS Logs, Events, And Plists Parser  
Details in blog post here: https://abrignoni.blogspot.com/2019/12/ileapp-ios-logs-events-and-properties.html

Supports iOS/iPadOS 11, 12, 13 and 14, 15, 16.
Select parsing directly from a compressed .tar/.zip file, or a decompressed directory, or an iTunes/Finder backup folder.

## Features

Parses:  
⚙️ Mobile Installation Logs  
⚙️ iOS 12+ Notifications  
⚙️ Build Info (iOS version, etc.)  
⚙️ Wireless cellular service info (IMEI, number, etc.)  
⚙️ Screen icons list by screen and in grid order.  
⚙️ ApplicationState.db support for app bundle ID to data container GUID correlation.   
⚙️ User and computer names that the iOS device connected to. Function updated by Jack Farley (@JackFarley248, http://farleyforensics.com/).  
etc...

## Requirements

Python 3.9 to latest version (older versions of 3.x will also work with the exception of one or two modules)
If on macOS (Intel) make sure Xcode is installed and have command line tools updated to be able to use Python 3.11. 

### PayByPhone App

Code to parse the PayByPhone application. 


## Acknowledgements

This tool is the result of a collaborative effort of many people in the DFIR community.
