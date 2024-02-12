# Recorder

## Introduction
This folder contains the scripts for recording live streams from various websites.

## Usage
1. First, make sure you have the necessary dependencies installed. You can find the installation instructions in the main README file.
2. After installing the dependencies, you can use the `record.bat` script to start the recording process. This script reads the model list from `model.txt` and calls `download_single.bat` to download the streams. You can refer to the content of `model.txt` to add complete links for downloading.

## Important Notes
- The `download_single.bat` script uses the `streamlink` command to download the streams. Make sure you have `streamlink` installed and in your system's PATH. You need to set the download location and file name in the streamlink config by yourself.
- The `record.bat` script starts a new command prompt window for each model in the list. This is done to prevent the command prompt window from closing after the download is finished. If you want to change this behavior, you can modify the script accordingly.

## Additional Information
For more information on how to use the scripts in this folder, please refer to the individual script files and their comments.
