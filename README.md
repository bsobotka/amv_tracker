# AMV Tracker

<p align="center">
<img src="https://github.com/bsobotka/amv_tracker/blob/main/md_images/md-amvt-logo.png">
</p>

Thank you for checking out my little project!

AMV Tracker is a simple but feature-rich GUI application which is designed to allow you to track, categorize, and rate the fanmade music videos you watch, although it is specifically tailored to the curation of anime music videos (AMVs).

- [Purpose](#purpose)
- [Installation](#installation)
- [Usage](#usage)
- [For developers](#for-developers)
- [TODOs](#todos)

## Purpose
I originally created AMV Tracker as a way to easily enter the AMVs I was watching into an Excel database -- prior to this it was a cumbersome, time-consuming, manual process, so I built a GUI to make this process significantly faster and easier. AMV Tracker v1.3.0 can be found [here](https://amvtracker.wordpress.com/). It worked fine but it had its limitations, was developed completely independent of any version control, was not open sourced, and in retrospect was not the most user-friendly piece of software. Over the course of building that application, I learned a lot about Python development in general and realized too late that much of the way that program had been structured was of poor quality.

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
**IF YOU ARE A USER OF AMV TRACKER v1 AND YOU WANT TO IMPORT YOUR OLD DATABASE INTO v2, PLEASE [READ THIS](https://github.com/bsobotka/amv_tracker/wiki/Adding-videos-to-your-database#import-from-previous-version-of-amv-tracker) BEFORE GOING ANY FURTHER.**

All you need to do to get AMV Tracker up and running is to download the ZIP file from [here](link), and extract the folder to a directory of your choice. Double-click the AMV Tracker 2.exe file to run the program. **Please note: this will only work on Windows 10+.**

Note: AMV Tracker makes use of ffmpeg for one of its features, which is generating thumbnails from video files. In order to use this feature, you will need to:
1. Download the latest FULL build from [here](https://www.gyan.dev/ffmpeg/builds/)
2. Extract the ffmpeg.exe and ffprobe.exe executables from the 'bin' folder
3. Copy those files to your AMV Tracker directory

AMV Tracker will still function without these executables, but you will be unable to generate thumbnail images from local video files.

## Usage
For an explanation of how to use AMV Tracker, please see the [wiki](https://github.com/bsobotka/amv_tracker/wiki) on this GitHub page. All features are explained in detail there.

## For developers

Pre-requisites:
 - Python 3
 - pipenv `pip install --user pipenv`

To run AMV Tracker, clone the repo and run these commands in the project root.

```sh
pipenv install
pipenv run python amv_tracker.py
```

If your IDE supports pipenv, it will ask you to enter a pipenv virtual environment. If you choose to do that, you can run `python amv_tracker.py` directly. PyCharm does this by default. 

## TODOs
A small list of longer-term implementations I would like to eventually include:
- [ ] Data source field? E.g. tracking whether a video came from a manual add, mass import, or somewhere else
- [ ] Create Statistics module for visualizing data contained in database
- [ ] Allow user to import CSV files
  - [ ] Create window to map CSV headers and AMV Tracker fields
  - [ ] Detection of poorly-matched datatypes?
