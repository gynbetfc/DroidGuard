#!/data/data/com.termux/files/usr/bin/bash
echo "🔄 Instalando DroidGuard..."
pkg update -y
pkg install -y python termux-api termux-tools
pip install requests
mkdir -p /sdcard/Download/DroidGuard/
echo "✅ Instalado! Execute: curl -k https://raw.githubusercontent.com/gynbetfc/DroidGuard/main/start.sh | bash"
