# %% [markdown]
# # BusComodin — revisión M7
# Notebook compatible con Jupyter/VS Code mediante celdas `# %%`.
# Reproduce los resultados principales usando los runners versionados.

# %%
from pathlib import Path
import json
import subprocess
import sys

ROOT = Path.cwd()
if ROOT.name == "notebooks": ROOT = ROOT.parent
SCENARIO = ROOT / "configs" / "scenario-villa-alemana-un11-2025-spatial-v1.json"
OUT = ROOT / "outputs" / "notebook-m7-review"
OUT.mkdir(parents=True, exist_ok=True)

# %% [markdown]
# ## Escenario
# UN11-2025 es benchmark histórico/provisional, no operación vigente 2026.

# %%
scenario = json.loads(SCENARIO.read_text(encoding="utf-8"))
print("version:", scenario["version"])
print("stops:", len(scenario["stops"]), "lines:", len(scenario["lines"]))

# %% [markdown]
# ## Multi-seed normal

# %%
subprocess.run([sys.executable, str(ROOT / "tools" / "run_m7_multiseed.py"), "--scenario", str(SCENARIO), "--output-dir", str(OUT / "normal")], check=True, cwd=ROOT)
normal = json.loads((OUT / "normal" / "summary.json").read_text(encoding="utf-8"))
for row in normal: print(row)

# %% [markdown]
# ## Resiliencia
# Cuando haya pasajeros no atendidos, priorizar espera censurada y tasa de servicio.

# %%
subprocess.run([sys.executable, str(ROOT / "tools" / "run_m7_resilience.py"), "--scenario", str(SCENARIO), "--output-dir", str(OUT / "resilience")], check=True, cwd=ROOT)
resilience = json.loads((OUT / "resilience" / "summary.json").read_text(encoding="utf-8"))
for row in resilience:
    if row["perturbation"] in {"normal", "C04_half_service", "C01_C02_half_service"}: print(row)

# %% [markdown]
# ## Próxima hipótesis
# Comparar misma flota total: `fixed-extra` vs `flexible-extra`, N=1..5.
# Si flexible gana robustamente, el beneficio puede atribuirse a la flexibilidad.
