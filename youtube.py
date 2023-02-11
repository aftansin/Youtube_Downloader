from pytube import YouTube

yt = YouTube('https://youtu.be/0lH_XiPoMlw')
streams = yt.streams.get_by_itag(22)
print(yt.streams.get_by_resolution(resolution='720p'))
video720 = yt.streams.get_by_resolution(resolution='720p')
video720.download()
