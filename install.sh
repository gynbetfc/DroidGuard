#!/data/data/com.termux/files/usr/bin/bash
# DroidGuard - Instalador Completo

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🛡️ DROIDGUARD - INSTALADOR"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Atualizar pacotes
echo "📦 Atualizando pacotes..."
pkg update -y

# Instalar dependências
echo "📦 Instalando termux-api..."
pkg install -y termux-api termux-tools python git

# Instalar requests
echo "📦 Instalando requests..."
pip install requests

# Criar diretório
mkdir -p ~/droidguard
cd ~/droidguard

# Baixar scripts
echo "📥 Baixando scripts..."
curl -k -o start.sh https://raw.githubusercontent.com/gynbetfc/DroidGuard/main/start.sh
curl -k -o kill.sh https://raw.githubusercontent.com/gynbetfc/DroidGuard/main/kill.sh
curl -k -o status.sh https://raw.githubusercontent.com/gynbetfc/DroidGuard/main/status.sh

chmod +x *.sh

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ INSTALAÇÃO CONCLUÍDA!"
echo ""
echo "📱 COMANDOS:"
echo "   cd ~/droidguard"
echo "   ./start.sh   # Iniciar o bot"
echo "   ./status.sh  # Verificar status"
echo "   ./kill.sh    # Matar o bot"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
