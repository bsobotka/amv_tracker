# AMV Tracker

<p align="center">

</p>

Thank you for checking out this project!

AMV Tracker is a simple but feature-rich GUI application which is designed to allow you to track, categorize, and rate the fanmade music videos you watch, although it is specifically tailored to the curation of anime music videos (AMVs).

- [Purpose](#purpose)
- [Installation](#installation)
- [Usage](#usage)
- [For developers](#for-developers)
- [TODOs](#todos)  
- [Special thanks](#special-thanks)

## Purpose
I originally created AMV Tracker as a way to easily enter the AMVs I was watching into an Excel database -- prior to this it was a cumbersome, time-consuming, manual process, so I built a GUI to make this process significantly faster and easier. AMV Tracker v1.3.0 can be found [here](https://amvtracker.wordpress.com/). It worked fine, but it had its limitations, was developed completely independent of any version control, was not open sourced, and in retrospect was not the most user-friendly piece of software. Over the course of building that application, I learned a lot about Python development in general and realized too late that much of the way that program had been structured was of poor quality.

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
**IF YOU ARE A USER OF AMV TRACKER v1 AND YOU WANT TO IMPORT YOUR v1 DATABASE INTO v2, PLEASE [READ THIS](https://github.com/bsobotka/amv_tracker/wiki/Adding-videos-to-your-database#import-from-previous-version-of-amv-tracker) BEFORE GOING ANY FURTHER.**

### Updating v2 version to the latest release
If you are currently using an existing v2 version of AMV Tracker, and you are looking to update to the newest release, head over to the [Releases](https://github.com/bsobotka/amv_tracker/releases) page and download the latest .zip file. When you open the archive, in most cases you will only need to extract the ``AMV Tracker.exe`` file and put it in your current AMV Tracker directory (thus overwriting the .exe file already in there). However, **please read the release notes, as in some cases there may be additional files you are asked to copy over as well.**

### First-time installation
All you need to do to get AMV Tracker up and running is to download the .zip archive from the latest release [here](https://github.com/bsobotka/amv_tracker/releases), and extract the ``/AMV Tracker`` folder to a directory of your choice. Double-click the ``AMV Tracker.exe`` file to run the program. **Please note: this will only work on Windows 10+.**

### Additional steps (optional)
AMV Tracker makes use of two optional external programs:  
* [yt-dlp](https://github.com/yt-dlp/yt-dlp) is used for downloading videos from YouTube directly from AMV Tracker  
* [ffmpeg](https://ffmpeg.org/) is used both to generate thumbnails from locally-stored video files, and to mux video and audio streams from files downloaded using yt-dlp (thus downloading from YouTube requires both yt-dlp *and* ffmpeg)

The below methods can be used to get yt-dlp and ffmpeg. Please note that Option 2 (for both) has been shown in my testing to both work and not work, thus using Option 1 in both cases is preferable as it has been successful in all test cases.

#### **<ins>To get yt-dlp</ins>**  
  
**Option 1 (preferred)**  
1. Open PowerShell (right-click Start button > Windows PowerShell) and type the following command: ``winget install yt-dlp``  
2. If you have AMV Tracker open when you do this, you may need to restart it to begin generating thumbnails.

**Option 2**
1. Download the latest version of yt-dlp.exe from [here](https://github.com/yt-dlp/yt-dlp/releases) (found under "Assets" -- you do not need any of the other files listed). NOTE: In the event that AMV Tracker starts having issues downloading YouTube videos, the specific yt-dlp version used in the initial development of AMV Tracker is ``yt-dlp 2024.05.27``.  
2. Once downloaded, there is no need to run it -- instead, you may place this file anywhere on your computer.  
3. Go to AMV Tracker's Settings, and in the "Data import" tab, click the "Find yt-dlp.exe" button to locate the .exe file. That's it!  

#### <ins>To get ffmpeg</ins>
  
**Option 1 (preferred)** 
1. Open PowerShell (right-click Start button > Windows PowerShell) and type the following command: ``winget install Gyan.FFmpeg``  
2. If you have AMV Tracker open when you do this, you may need to restart it to begin generating thumbnails.
  
**Option 2**
1. Download the latest "Essentials" build from [here](https://www.gyan.dev/ffmpeg/builds/).  
2. Extract all three executables from the ``/bin`` folder. **If you plan to use AMV Tracker's "Download from YouTube" function, you must place these files in the same folder as yt-dlp.exe (see instructions above).** Otherwise, you can put them anywhere.  
3. Go to AMV Tracker's Settings, and in the "Data import" tab, click the "Find ffmpeg.exe" and "Find ffprobe.exe" buttons to locate these files on your machine. That's it!

AMV Tracker will still function without yt-dlp and ffmpeg, but you will be unable to download YouTube videos from AMV Tracker without both yt-dlp and ffmpeg, and you will be unable to generate thumbnails from local video files without ffmpeg.exe and ffprobe.exe.

## Usage
For an explanation of how to use AMV Tracker, please see the [wiki](https://github.com/bsobotka/amv_tracker/wiki) on this GitHub page. All features are explained in detail there.

## For developers

Pre-requisites:
 - Python 3.7+
 - pipenv `pip install --user pipenv`

To run AMV Tracker, clone the repo and run these commands in the project root:

```sh
pipenv install
pipenv run python amv_tracker.py
```

If your IDE supports pipenv, it will ask you to enter a pipenv virtual environment. If you choose to do that, you can run `python amv_tracker.py` directly. PyCharm does this by default.  
  
Also, I recommend commenting out this line in `amv_tracker.py` while doing any development work:  
  
`sys.excepthook = error_handler`  
  
...as this line routes any traceback messages to the errors.log file and to a user-facing error window, rather than to the console. Commenting it out will ensure that any exceptions are communicated to you in the console.

## TODOs
A small list of longer-term implementations I would like to eventually include:
- [x] Data source field? E.g. tracking whether a video came from a manual add, mass import, or somewhere else - DONE
- [ ] Create Statistics module for visualizing data contained in database
- [ ] Allow user to import CSV files
  - [ ] Create window to map CSV headers and AMV Tracker fields
  - [ ] Detection of poorly-matched datatypes?

## Special thanks  
Thank you to the following people for beta testing AMV Tracker at various points and providing extraordinarily helpful feedback and suggestions, all of which have served to make this version of AMV Tracker better than it was before they said anything:
* seasons
* katranat
* Vars
* Reisir

Extra special thanks as well to [Reisir](https://github.com/reisir) for their contributions to the code itself, and for helping me with a bunch of code/GitHub-related things that I didn't understand!
