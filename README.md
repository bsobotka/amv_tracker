# AMV Tracker 2

<p align="center">
<img src="https://github.com/bsobotka/amv_tracker/blob/main/md_images/md-amvt-logo.png">
</p>

AMV Tracker is a simple but feature-rich GUI application which is designed to allow you to track, categorize, and rate the fanmade music videos you watch, although it is specifically tailored to the curation of anime music videos (AMVs).

1. [Purpose](#purpose)
2. [Installation](#installation)
3. [Usage](#usage)

## Purpose
I originally created AMV Tracker as a way to easily enter the AMVs I was watching into an Excel database -- prior to this it was a cumbersome, time-consuming, manual process, so I built a GUI to make this process significantly faster and easier. AMV Tracker v1.3.0 can be found [here](https://amvtracker.wordpress.com/). It worked fine but it had its limitations, and in retrospect was not the most user-friendly piece of software. Over the course of building that application, I learned a lot and realized too late that much of the way that program had been structured was of poor quality.

I decided to completely re-write the program from the ground up to accomplish the following:
1. Make the experience much more user-friendly
2. Make the program more fun to look at, interact with, and use in general
3. Reduce the number of windows the user had to click through to do almost anything in the program
4. Remove the database limitations which the original program's design enforced (it put all data into an .xls file, which has a hard limit of 65,536 rows per sheet)
5. Remove the arbitrary limitations I had enforced on the user with regard to content tagging, data integrity checks, and other things
6. Introduce additional automation to make filling out video data quicker and easier still
7. Introduce more advanced filtering tools to make finding specific videos or types of videos as easy as possible
8. In general, add enough features to make AMV Tracker the user's primary method of keeping track of the videos they love, over other potential tools such as YouTube playlists or personal spreadsheets

## Installation
All you need to do to get AMV Tracker up and running is to download the ZIP file from [here](link), and extract the folder to a directory of your choice. Double-click the AMV Tracker 2.exe file to run the program.

*Note: AMV Tracker makes use of ffmpeg for one of its features, which is generating thumbnails from video files. In order to use this feature, you will need to download the latest FULL build from [here](https://www.gyan.dev/ffmpeg/builds/), extract the ffmpeg.exe and ffprobe.exe execultables from the 'bin' folder, and put them in your AMV Tracker directory. AMV Tracker will still function without these executables, but you will be unable to generate thumbnail images from local video files.*

## Usage
The main window which you will be spending most of your time in looks like this, and can be broadly separated into five different sections:
![Main window](/md_images/01_mainwindow.png)

1. Top ribbon, which can be further subdivided into three sections:
	1. Video entry options
		* [Add video](#Single-video-entry)
		* [Download video data from YouTube channel or AnimeMusicVideos.org editor profile]()
		* [Download video data from public YouTube playlist]()
	2. [View type]()
		* List view
		* Detail view
	3. Misc AMV Tracker functions
		* Check for update
		* [AMV Tracker settings]()
2. Search options
	* Apply top-level filter to show all videos in a given sub-database or custom list, and from there apply additional [basic filters]() based on what is chosen in the dropdown menu to further narrow your search
	* Basic stats about the displayed filtered video list will be shown in the box near the bottom
	* Five additional functions:
		1. Play a random locally-stored video from the filtered videos
		2. Go to a random video on YouTube from the filtered videos
		3. [Mass edit]() the filtered videos
		4. [Add all filtered videos to a custom list]()
		5. Export filtered list to a .csv file
3. [Video list]() (this may look different depending on your view type)
4. [Advanced filters]()
5. Status bar which shows persistent AMV Tracker information
	* Version number on the left
	* Path to the current working database on the right

### <ins>Adding videos</ins>
#### Single video entry
To add a single new video entry to your database, click the "+" button on the upper-left of the main window. You will be shown a new window with four tabs, each of which includes different types of data you can add to your video.
##### Sources and URLs
This tab allows you to identify where this video and editor can be found on the internet, as well as where the video file might be found on your local computer (if it exists there). It is also where you locate/generate/download thumbnail images for your video entries.
1. Video sources
	* **Video URL text boxes**: These four boxes are for you to put URLs to where the video lives on specific websites -- YouTube, AnimeMusicVideos.org, AMVNews, and/or any other website where the video might be found. There are additional functions which are activated when certain criteria are met:
		* ![Go to URL](/md_images/icon-md-go-to-url.png) - URL must be entered. Click to open the corresponding URL in your browser. (If you put a URL in and this button does not activate, please ensure that the URL you are entering is correct -- i.e. you are entering a YouTube URL in the the YouTube text box, an AMV.org video URL in the AMV.org text box, etc.)
		* ![Fetch info](/md_images/icon-md-fetch.png) - URL must be entered. Click to auto-populate video and editor information with data scraped from the corresponding URL.
		* ![Download video](/md_images/icon-md-download.png) - URL must be entered. Click to download video.
			* For **YouTube** URL, download the video in 720p resolution (if available) (NOTE: due to the library used for YouTube-related functions within AMV Tracker, this function may not always be working, in which case an error message will pop up directing you to alternatives to achieve this).
			* For **AMV.org** URL, be taken to the video's download page (NOTE: you must be logged in to your .org account and have fewer than 10 outstanding star ratings, which can be cleared on the Member's Main Page).
			* For **AMVNews** URL, be taken to the video's download page.
		* ![Search for video](/md_images/icon-md-search.png) - Video title and editor name must be entered on "Video information" tab (for AMVNews, only video title is required). This will execute a search on the corresponding website to try and find the video.
		* ![Search and fetch](/md_images/icon-md-search-and-fetch.png) - AMV.org only. Video title and editor name must be entered on "Video information" tab. AMV Tracker will execute a search for the video based on AnimeMusicVideos.org based on the entered editor name and video title, and will scrape the video/editor information from the first search result that occurs.
	* **Local file**: If you have the video file saved locally on your computer, you can locate it here by clicking the "Local file" button.
		* ![Clear text](/md_images/icon-md-delete-text.png) - Clear the file path from the "Local file" text box.
		* ![Play video](/md_images/icon-md-play.png) - Play video file. If the file has been renamed, moved, or deleted since the local file path was specified, an error message will alert you to this fact.
	* **Thumbnail**: Thumbnails are used to display an image for each video entry while in [Detail View](). You can either manually select an image file on your computer by clicking the "Thumbnail" button here, or you can generate/download one if certain conditions are met (see below). *NOTE: All generated or downloaded thumbnails are automatically put into the AMV_Tracker/thumbnails/[db_name] directory. They are named based on the unique video ID that is generated when you enter the video into your database.*
		* ![Clear text](/md_images/icon-md-delete-text.png) - Clear the file path from the "Thumbnails" text box.
		* ![Download thumbnail](/md_images/icon-md-download.png) - Download the YouTube thumbnail for this video. YouTube URL must be entered in the "Video YouTube URL" text box.
		* ![Generate thumbnail](/md_images/icon-md-generate-thumb.png) - Generate a thumbnail from the local video file specified in the "Local file" text box. NOTE: You must have both the ffmpeg.exe and ffprobe.exe files in your base AMV Tracker directory for this to work. You can download the FULL build [here](https://www.gyan.dev/ffmpeg/builds/) and extract these two files from the 'bin' folder in the .7z file.
		
2. Editor channels/profiles
	* **Fetch URLs from existing entries**: If you have entered the editor's name on the "Video information" tab and this editor has at least one video entry already in your database, you can click this button to auto-populate the below four text boxes with any URLs already entered into AMV Tracker for this editor.
	* **URL text boxes**: Here you can specify links to where to find this editor on YouTube, AMV.org, AMVNews, or any other locations. Clicking the corresponding ![Go to URL](/md_images/icon-md-go-to-url.png) button will take you to the provided URL in your browser.
		
##### Video information
This tab is where you will enter all of the publicly available information about this video, such as video footage used, song artist/title, video duration, contests entered, the editor's own words about the video, among other things. Most of these things should be pretty self-explanatory, but here are some details to know about some of the fields on this tab. *PLEASE NOTE: By default, all fields in the video entry window are OPTIONAL, with the exception of "Primary editor username" and "Video title". These two fields are <ins>always</ins> required for a video to be entered into your database.*
* **Primary editor other username(s)**: Used to denote any other usernames this editor currently goes by, or has gone by in the past. If you need to enter multiple names here, separate them with a semicolon + space ("; ")
* **Addl. editor(s)**: Used to list out other editors involved in the creation of the video. Activates once the "Primary editor username" field is filled in. Click the "2+ editors" button that appears to enter the names of multiple editors, each on their own line, if needed.
* **Release date**: Please note that all three dropdown boxes must be filled in for the release date to be entered, otherwise it will just go into your database as blank. If the release date is not known, check the "Date unknown" checkbox.
* **Star rating**: Used to record any publicly available star ratings (for example, on the .org you can see this per video if you are/were a Donator, and there is a star rating available for every video on AMVNews). Needs to be a number between 0 - 5.
* **Video footage used**: As you enter more and more videos into AMV Tracker, you will be able to select already-entered footage by either double-clicking the text box or starting to type the footage name and selecting it from the popup. If the footage is not already represented in the database, type it out and then click the "+" button to add it.
* **Song genre**: If you are unsure what genre a song is, enter the artist name and click the "[?]" link next to the "Song genre" text box to look the artist up on RateYourMusic, which should provide good suggestions.

##### My rating/tags/comments
This tab is to input your own personal feedback on the video, including a rating you can assign (out of 10), marking the video as notable or as a favorite, adding tags, and writing your own notes on the video.
* **My rating**: This is a rating you can assign to the video to denote how much you like it. Ratings are at intervals of 0.5 on a scale of 0 - 10.
* **Notable/Favorite**: These are checkboxes you can use to identify videos of note (whatever that means to you), or to easily mark your "favorite" videos. Both of these can be used to easily find such videos via [filtering]() later.
* **Apply custom logic**: Custom tag logic can be set in the [Video entry]() section of AMV Tracker's [Settings](). This function allows you to auto-tag videos based on other fields within AMV Tracker being filled out in certain ways, in order to make tagging videos easier. Clicking this button will run through any active filter logic and apply tags as instructed. <ins>PLEASE NOTE: clicking this button will erase any existing tags and overwrite them based on your defined logic -- thus it's best to click this button BEFORE any other tags have been applied.</ins>
* **Tags**: Here you can select any tags you feel apply to the video you are entering. Tags can be created and defined in the [Tag management]() section of AMV Tracker's [Settings](). Clicking the corresponding ![Clear tags](/md_images/icon-md-delete-text.png) button will clear all tags from that row.
* **Personal comments/notes**: This is a free text entry field where you can make any notes or comments you want on the video being entered.

##### Submission rules
This tab is used to both check data before it is submitted to the database, as well as to tell AMV Tracker where to put the video within your database.
* **Checks enabled**: Check this box if you want to ensure that the fields defined under the "Data checking" section of the [Video entry]() tab in AMV Tracker's [Settings]() are populated before the video can be entered into your database. Uncheck this box to disable this check -- in this case, only the Primary Editor Username and Video Title fields need to be populated. NOTE: The default state of this checkbox can be defined in Settings.
* **Add to following sub-DBs**: If you are making use of [sub-databases]() other than "Main database", and you want this video to go into one or more of them, choose the specific sub-DBs you want this video to be entered into here. PLEASE NOTE: At least one sub-DB must be selected in order for the video to be entered into your database.
* **Add to following Custom Lists**: If you have one or more [Custom Lists]() and you'd like to put the video into them, select which Custom Lists you'd like to add the video to here.