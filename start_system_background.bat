@echo off
title Khoi dong he thong SYNAPES AUDIT chay ngam
echo Dang khoi dong Docker Containers va Tunnel ket noi truc tuyen...

:: 1. Nap duong dan Docker Desktop
set "PATH=C:\Users\84364\AppData\Local\Programs\DockerDesktop\resources\bin;%PATH%"

:: 2. Di chuyen den thu muc du an
cd /d "C:\Users\84364\.gemini\antigravity\scratch\academic-checker-system"

:: 3. Khoi dong Docker Compose
echo Dang bat Docker containers (checker-api, checker-worker, checker-redis)...
docker compose up -d

:: 4. Cho 3 giay de server khoi dong hoan tat
timeout /t 3 /nobreak >nul

:: 5. Bat localtunnel va cloudflared chay ngam
echo Dang kich hoat duong truyen truc tuyen vinh vien...
start /b npx -y localtunnel --port 8000 --subdomain synapeseducheck
start /b npx -y cloudflared tunnel --url http://localhost:8000

echo.
echo =====================================================================
echo  HE THONG SYNAPES AUDIT DA DUOC KHOI CHAY HOAN TAT!
echo  Web hoat dong doc lap, ban co the dong hoan toan Antigravity.
echo.
echo  Dia chi truy cap chinh: https://synapeseducheck.loca.lt
echo  Mat khau xac thuc IP: 123.21.221.221
echo =====================================================================
echo.
pause
