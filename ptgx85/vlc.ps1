$vlc_location="C:\Program Files (x86)\VideoLAN\VLC\vlc.exe"

$str=$args[0]

$file=$str.Split(":", 2)[1]

Start-Process $vlc_location $file