@ECHO off
ECHO Building...
.\7za.exe e deno_win.7z
.\7za.exe e ffmpeg_win.7z
.\7za.exe e ytdlp_win.7z
EXIT/B