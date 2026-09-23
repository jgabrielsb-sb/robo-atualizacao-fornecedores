#!/usr/bin/env bash
# Runs run_update_<cnpj>.py for a fixed set of fornecedores against the real
# production workflow (Protheus update + fornecedores API persist).
#
# CNPJs covered:
#   Prevesat Solução Em Engenharia Ltda - 21.966.327/0001-92
#   Senar                                - 04.155.170/0001-04
#   Disrupy                              - 10.711.572/0001-32
#   Frln Advogados                       - 26.705.113/0001-86
#   Climex                               - 17.532.856/0001-00
#   Idc Solucoes Empresa                 - 07.502.722/0001-93
#   Vitte                                - 22.935.016/0001-29
#   Sistema De Seguranca                 - 18.593.359/0001-85
#   Coop Tele Taxi                       - 24.312.944/0001-62

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

CNPJS=(
  21966327000192
  04155170000104
  10711572000132
  26705113000186
  17532856000100
  07502722000193
  22935016000129
  18593359000185
  24312944000162
)

cd "$REPO_ROOT"

for cnpj in "${CNPJS[@]}"; do
  script_path="$SCRIPT_DIR/run_update_${cnpj}.py"
  if [[ ! -f "$script_path" ]]; then
    echo "Skipping ${cnpj}: ${script_path} not found" >&2
    continue
  fi
  echo "==> Running update for CNPJ ${cnpj}"
  uv run python "$script_path"
done
