# AMV Tracker 2

AMV Tracker is a simple but feature-rich GUI application which is designed to allow you to track, categorize, and rate the fanmade music videos you watch, although it is specifically tailored to the curation of anime music videos (AMVs).

1. [Purpose](link)
2. [Installation](link)
3. [Usage](link)

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
		* [Add video]()
		* [Download video data from YouTube channel or AnimeMusicVideos.org editor profile]()
		* [Download video data from public YouTube playlist]()
	2. [View type]()
		* List view
		* Detail view
	3. Misc AMV Tracker functions
		* Database statistics/analytics
		* Check for update
		* [AMV Tracker settings]()
2. Search options
	* Apply top-level filter to show all videos in a given sub-database or custom list, and from there apply additional [basic filters]() based on what is chosen in the dropdown menu to further narrow your search
	* Basic stats about the displayed filtered video list will be shown in the box near the bottom
	* Four additional functions:
		1. Play a random locally-stored video from the filtered videos
		2. Go to a random video on YouTube from the filtered videos
		3. [Mass edit]() the filtered videos
		4. [Add all filtered videos to a custom list]()
3. [Video list]() (this may look different depending on your view type)
4. [Advanced filters]()
5. Status bar which shows persistent AMV Tracker information
	* Version number on the left
	* Path to the current working database on the right

### <ins>Adding videos</ins>
#### Single video entry
To add a single new video entry to your database, click the "+" button on the upper-left of the main window. You will be shown a new window with four tabs, each of which includes different types of data you can add to your video.
1. Sources and URLs
	* **Video URL text boxes**: These four boxes are for you to put URLs to where the video lives on specific websites -- YouTube, AnimeMusicVideos.org, AMVNews, and/or any other website where the video might be found. There are additional functions which are activated when certain criteria are met:
		* ![Go to URL](/md_images/icon-md-go-to-url.png) - URL must be entered. Click to open the corresponding URL in your browser
		* ![Fetch info](/md_images/icon-md-fetch.png) - URL must be entered. Click to auto-populate video and editor information with data scraped from the corresponding URL
		* ![Download video](/md_images/icon-md-download.png) - URL must be entered. Click to download video
			* For **YouTube** URL, download the video in 720p resolution (if available) (NOTE: due to the library used for YouTube-related functions within AMV Tracker, this function may not always be working, in which case an error message will pop up directing you to alternatives to achieve this)
			* For **AMV.org** URL, be taken to the video's download page (NOTE: you must be logged in to your .org account and have fewer than 10 outstanding star ratings, which can be cleared on the Member's Main Page)
			* For **AMVNews** URL, be taken to the video's download page
		* ![Search for video](/md_images/icon-md-search.png) - Video title and editor name must be entered on "Video information" tab (for AMVNews, only video title is required). This will execute a search on the corresponding website to try and find the video.
		* ![Search and fetch](/md_images/icon-md-search-and-fetch.png) - AMV.org only. Video title and editor name must be entered on "Video information" tab. AMV Tracker will execute a search for the video based on AnimeMusicVideos.org based on the entered editor name and video title, and will scrape the video/editor information from the first search result that occurs.