# TO DO
## Settings
### Data management settings  
- [x] Import old AMV Tracker database  
  - [ ] Check to confirm that selected spreadsheet is compatible
  - [x] If day is added to video entry, make sure "01" is added as the day in all videos imported from old AMVT db
  - [x] Check what happens if user tries to import AMVT database if they have already done so once
- [ ] Import personal spreadsheet (.CSV format)  
- [x] Create sub-DBs
- [x] Rename sub-DBs (except for Main Database)
- [ ] Delete sub-DBs
- [ ] Create/restore backup database  
- [ ] Allow user to specify location to save backup file (? - think about this)  
- [x] Create new database (? - think about this)  
- [x] Point to database location in settings.db, and update common_vars.py with that reference  
  ~~Rename database (? - think about this)~~
- [ ] Clear all data from selected sub-DBs  
- [ ] Clear selected data from sub-DBs (except for editor name/video title)  
- [ ] Mass update videos with tags, 'Favorite', and 'Notable' designations
	
### General settings

### Video entry settings
- [ ] Set mutually exclusive tags
- [ ] Populate editor profile URLs if already exist

### Video search settings
- [x] Allow user to set visible columns for search screen

### Tag management settings  
- [ ] When a tag is deleted, it must be completely removed from all entries  
- [ ] When a tag is moved to a different list, it must be moved to the new column in the db for all entries  
- [ ] When a tag is renamed, it must be renamed on all entries
	
## Video entry
- [x] If pseudonym(s) is/are entered, update editor's existing videos with those pseudonyms, as well as any videos listed under any of their pseudonyms
- [x] Add day to date entry
- [ ] Redesign video footage entry method
- [ ] If user has entered the video's .org profile URL, give them the option to auto-fetch video profile text into Description box
- [ ] If "link profiles" has been checked in settings, auto-populate editor profile URL boxes based on existing entries
- [ ] Populate Custom Lists listview with any custom lists user has created
- [x] If editor name/video title combo exists in database, alert user
- [x] Create popup box that alerts user that video is successfully submitted to database

## Video search
- [ ] Search table/list view  
  - [ ] Automatically update when new search parameters are specified
  - [ ] Clickable fields for opening video file/URL/etc.
  - [ ] Show working database path
- [ ] Create video profiles for list view  
- [ ] Create editor profiles
  - [ ] Thumbnails based on .org profile/YT channel?
- [ ] Detail view  
- [ ] Basic search filters on left side  
  - [ ] One dropdown for sub-db selection  
- [ ] Advanced search filters on right side (? - may not be necessary)  
- [ ] Custom search integration using AND/OR/NOT logic  

## Custom Lists
- [ ] Create process for creating custom lists
- [ ] Create process for finding existing videos and adding them to custom lists

## AMV Notepad

## Misc.  
- [ ] Create 'check for update' / AMV Tracker update process
- [ ] Import custom lists from old version of AMV Tracker

# BUGS  
- [x] On video entry, tag list does not open and program crashes if no tooltips exist on any of the tags in the selected list
	
