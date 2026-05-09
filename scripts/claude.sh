#!/usr/bin/env bash
# Inicia Claude Code com configuração DeepSeek v4 Pro
# Carrega .env e exporta variáveis necessárias

set -euo pipefail

cd "$(dirname "$0")/.."

# Verificar se .env existe
if [[ ! -f .env ]]; then
  echo "❌ Erro: .env não encontrado"
  echo "   Copie .env.example para .env e preencha ANTHROPIC_AUTH_TOKEN"
  exit 1
fi

# Carregar e exportar variáveis
export $(grep -v '^#' .env | grep -v '^$' | xargs)

# Validar que a API key foi preenchida
if [[ -z "${ANTHROPIC_AUTH_TOKEN:-}" ]] || [[ "$ANTHROPIC_AUTH_TOKEN" == "<seu-deepseek-api-key>" ]]; then
  echo "❌ Erro: ANTHROPIC_AUTH_TOKEN não configurado ou ainda é placeholder"
  echo "   Edite .env e preencha com sua chave do DeepSeek"
  exit 1
fi

echo "🚀 Iniciando Claude Code com DeepSeek v4 Pro..."
echo "   Base URL: $ANTHROPIC_BASE_URL"
echo "   Model: $ANTHROPIC_MODEL"

exec claude
