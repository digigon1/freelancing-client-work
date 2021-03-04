$vlc_location="E:\Programs\PotPlayer\PotPlayerMini64.exe"

$str=$args[0]

$file=$str.Split(":", 2)[1]

Start-Process $vlc_location $file