#!/bin/bash
# 3PKC KMS MCP Server Installation Script for WSL
# Run this inside WSL: bash /mnt/c/Users/yujiashi/Desktop/SmartSuite_Phase1/setup_kms_mcp.sh

set -e
echo "=== Step 1: Midway Authentication ==="
if command -v mwinit &> /dev/null; then
    echo "Running mwinit..."
    mwinit -f
else
    echo "mwinit not found in WSL. Please authenticate in Windows PowerShell first:"
    echo "  PS> mwinit -f"
    echo ""
    read -p "Have you authenticated in Windows? (y/n): " confirmed
    if [[ "$confirmed" != "y" ]]; then
        echo "Please authenticate first, then re-run this script."
        exit 1
    fi
fi
echo ""

echo "=== Step 2: Install Builder Toolbox ==="
if ! command -v toolbox &> /dev/null; then
    echo "Installing toolbox..."
    toolbox install toolbox
    source ~/.bashrc
else
    echo "toolbox already installed: $(toolbox --version)"
fi
echo ""

echo "=== Step 3: Install AIM CLI ==="
if ! command -v aim &> /dev/null; then
    echo "Installing aim..."
    toolbox install aim
else
    echo "aim already installed: $(aim --version)"
fi
echo ""

echo "=== Step 4: Install 3PKC MCP Server ==="
echo "Installing issca-3pkc-genai-mcp..."
aim mcp install issca-3pkc-genai-mcp
echo ""

echo "=== Step 5: Install Node.js 20+ ==="
if ! command -v node &> /dev/null || [[ $(node --version | sed 's/v//' | cut -d. -f1) -lt 20 ]]; then
    echo "Installing fnm and Node.js 20..."
    curl -fsSL https://fnm.vercel.app/install | bash
    source ~/.bashrc
    export PATH="$HOME/.local/share/fnm:$PATH"
    eval "$(fnm env --shell bash)"
    fnm install 20
    fnm use 20
    echo "Node.js version: $(node --version)"
else
    echo "Node.js already OK: $(node --version)"
fi
echo ""

echo "=== Step 6: Create Wrapper Script ==="
USERNAME=$(whoami)
WRAPPER="/home/${USERNAME}/issca-3pkc-genai-mcp-wrapper.sh"

# Find the actual paths
FNM_PATH=$(find /home -name 'fnm' -type f -path '*/share/fnm/*' 2>/dev/null | head -1)
FNM_DIR=$(dirname "$FNM_PATH" 2>/dev/null || echo "/home/${USERNAME}/.local/share/fnm")

cat > "$WRAPPER" << WEOF
#!/bin/bash
export PATH="${FNM_DIR}:\$PATH"
eval "\$(${FNM_DIR}/fnm env --shell bash)"
export PATH="\$HOME/.toolbox/bin:\$PATH"
exec issca-3pkc-genai-mcp "\$@"
WEOF

chmod +x "$WRAPPER"
echo "Wrapper created at: $WRAPPER"
echo ""

echo "=== Step 7: Verify ==="
echo "Testing MCP server (should hang with no errors - will timeout in 3s)..."
timeout 3 "$WRAPPER" 2>&1 || true
echo ""
echo "=== DONE ==="
echo ""
echo "Now configure Kiro MCP. Add this to C:\\Users\\${USERNAME}\\.kiro\\settings\\mcp.json:"
echo ""
echo '{
  "mcpServers": {
    "issca-3pkc-genai-mcp": {
      "command": "wsl",
      "args": ["bash", "-l", "-c", "'$WRAPPER'"],
      "disabled": false,
      "autoApprove": []
    }
  }
}'
echo ""
echo "Then in Kiro: Ctrl+Shift+P -> 'MCP: Reconnect Servers'"
