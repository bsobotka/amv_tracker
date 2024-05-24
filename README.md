# AMV Tracker

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
**IF YOU ARE A USER OF AMV TRACKER v1 AND YOU WANT TO IMPORT YOUR OLD DATABASE INTO v2, PLEASE [READ THIS](https://github.com/bsobotka/amv_tracker/wiki/Adding-videos-to-your-database#import-from-previous-version-of-amv-tracker) BEFORE GOING ANY FURTHER.**

All you need to do to get AMV Tracker up and running is to download the ZIP file from [here](link), and extract the folder to a directory of your choice. Double-click the AMV Tracker 2.exe file to run the program.

Note: AMV Tracker makes use of ffmpeg for one of its features, which is generating thumbnails from video files. In order to use this feature, you will need to:
1. Download the latest FULL build from [here](https://www.gyan.dev/ffmpeg/builds/)
2. Extract the ffmpeg.exe and ffprobe.exe executables from the 'bin' folder
3. Copy those files to your AMV Tracker directory

Note that AMV Tracker will still function without these executables, but you will be unable to generate thumbnail images from local video files.

## Usage
For an explanation of how to use AMV Tracker, please see the [wiki](https://github.com/bsobotka/amv_tracker/wiki) on this GitHub page. All features are explained in detail there.

Thank you for checking this out, and enjoy using AMV Tracker!
