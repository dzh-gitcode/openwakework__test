$url = "https://openaipublic.azureedge.net/main/whisper/models/ed3a0b6b1c0edf879ad9b11b1af5a0e6ab5db9205f891f668f8b0e6c6326e34e/base.pt"
$cacheDir = "$env:USERPROFILE\.cache\whisper"
New-Item -ItemType Directory -Path $cacheDir -Force | Out-Null
$dest = "$cacheDir\base.pt"
Write-Host "Downloading whisper base model (~139MB)..."
$start = Get-Date
Invoke-WebRequest -Uri $url -OutFile $dest -UseBasicParsing
$size = [math]::Round((Get-Item $dest).Length / 1MB, 2)
$elapsed = (Get-Date) - $start
Write-Host "Downloaded: $size MB in $([math]::Round($elapsed.TotalSeconds, 1)) seconds"
