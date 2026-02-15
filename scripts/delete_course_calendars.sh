#!/usr/bin/env bash
set -euo pipefail
PY="/home/notadil/Projects/Calendar/.venv/bin/python"
CLI="src/gcal_cli.py"
echo "Deleting calendar pattern: Algébre 2 (NAJMEDDINE)"
$PY $CLI delete "Algébre 2 (NAJMEDDINE)" --yes || true
echo "Deleting calendar pattern: Analyse 4 (MOUZOUN)"
$PY $CLI delete "Analyse 4 (MOUZOUN)" --yes || true
echo "Deleting calendar pattern: Développement personnel (BADIOUI)"
$PY $CLI delete "Développement personnel (BADIOUI)" --yes || true
echo "Deleting calendar pattern: Electromagnétisme (KHADIRI)"
$PY $CLI delete "Electromagnétisme (KHADIRI)" --yes || true
echo "Deleting calendar pattern: Elément de mach (OUDRA)"
$PY $CLI delete "Elément de mach (OUDRA)" --yes || true
echo "Deleting calendar pattern: English for International"
$PY $CLI delete "English for International" --yes || true
echo "Deleting calendar pattern: Méthodes numérique (FASSI FIHRI)"
$PY $CLI delete "Méthodes numérique (FASSI FIHRI)" --yes || true
echo "Deleting calendar pattern: Optique (QARCHI)"
$PY $CLI delete "Optique (QARCHI)" --yes || true
echo "Deleting calendar pattern: Progr avancée (AHMADI)"
$PY $CLI delete "Progr avancée (AHMADI)" --yes || true
echo "Deleting calendar pattern: Savoir être"
$PY $CLI delete "Savoir être" --yes || true
echo "Deleting calendar pattern: Techniques d'écriture (ISMAILI)"
$PY $CLI delete "Techniques d'écriture (ISMAILI)" --yes || true
echo "Deleting calendar pattern: développement personnel"
$PY $CLI delete "développement personnel" --yes || true
