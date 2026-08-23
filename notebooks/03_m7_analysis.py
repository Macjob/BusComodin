# %% [markdown]
# # BusComodin — M7 Analysis Dashboard
#
# Notebook visual para revisar el benchmark UN11-2025 espacial.
# Ejecutar con Jupyter/VS Code usando las celdas `# %%`.
#
# **Importante:** UN11-2025 es un benchmark histórico/provisional. Las rutas y
# frecuencias provienen de DTPR; demanda, paradas secundarias y tiempos espaciales
# conservan supuestos/calibraciones documentadas. No representa la operación 2026.

# %%
from pathlib import Path
import json
import subprocess
import sys

import matplotlib.pyplot as plt

ROOT = Path.cwd()
if ROOT.name == "notebooks":
    ROOT = ROOT.parent
SCENARIO = ROOT / "configs" / "scenario-villa-alemana-un11-2025-spatial-v1.json"
OUT = ROOT / "outputs" / "notebook-m7-analysis"
OUT.mkdir(parents=True, exist_ok=True)

# %% [markdown]
# ## 1. Actualizar resultados reproducibles
#
# Estas celdas vuelven a ejecutar las mismas 20 semillas antes de graficar.

# %%
subprocess.run([
    sys.executable, str(ROOT / "tools" / "run_m7_multiseed.py"),
    "--scenario", str(SCENARIO), "--output-dir", str(OUT / "normal")
], check=True, cwd=ROOT)
subprocess.run([
    sys.executable, str(ROOT / "tools" / "run_m7_resilience.py"),
    "--scenario", str(SCENARIO), "--output-dir", str(OUT / "resilience")
], check=True, cwd=ROOT)

normal = json.loads((OUT / "normal" / "summary.json").read_text(encoding="utf-8"))
resilience = json.loads((OUT / "resilience" / "summary.json").read_text(encoding="utf-8"))

# %% [markdown]
# ## 2. KPIs principales

# %%
baseline = next(r for r in normal if r["policy"] == "baseline")
adaptive = [r for r in normal if r["policy"] != "baseline"]
best = min(adaptive, key=lambda r: r["mean_wait_minutes"])
best_improvement = 100 * (baseline["mean_wait_minutes"] - best["mean_wait_minutes"]) / baseline["mean_wait_minutes"]

c04 = [r for r in resilience if r["perturbation"] == "C04_half_service"]
c04_best = min(c04, key=lambda r: r["mean_censored_wait_minutes"])

print("BUSCOMODIN — M7 KPI SNAPSHOT")
print("=" * 42)
print(f"Baseline normal             : {baseline['mean_wait_minutes']:.2f} min")
print(f"Mejor política normal       : {best['policy']}")
print(f"Mejora normal               : {best_improvement:.2f}%")
print(f"Tasa servicio baseline      : {baseline['mean_service_rate_pct']:.2f}%")
print(f"P95 espera baseline         : {baseline['mean_p95_wait_minutes']:.2f} min")
print(f"Mejor política C04 50%      : {c04_best['policy']}")
print(f"Mejora censurada C04 50%    : {c04_best['censored_wait_improvement_vs_baseline_pct']:.2f}%")

# %% [markdown]
# ## 3. Espera media en operación normal
# Menor es mejor.

# %%
labels = [r["policy"] for r in normal]
values = [r["mean_wait_minutes"] for r in normal]
plt.figure(figsize=(10, 5))
plt.bar(labels, values)
plt.ylabel("Espera media (min)")
plt.title("UN11-2025 — espera media por política, 20 seeds")
plt.xticks(rotation=20, ha="right")
plt.tight_layout()
plt.show()

# %% [markdown]
# ## 4. Mejora respecto del baseline
# Permite ver rápidamente que el beneficio normal es modesto.

# %%
improvements = [100 * (baseline["mean_wait_minutes"] - r["mean_wait_minutes"]) / baseline["mean_wait_minutes"] for r in adaptive]
plt.figure(figsize=(9, 5))
plt.bar([r["policy"] for r in adaptive], improvements)
plt.axhline(0, linewidth=1)
plt.ylabel("Mejora vs baseline (%)")
plt.title("Beneficio de políticas adaptativas — operación normal")
plt.xticks(rotation=20, ha="right")
plt.tight_layout()
plt.show()

# %% [markdown]
# ## 5. Normal vs red degradada
# Compara la mejora censurada en cada perturbación. Esta es la visualización más
# importante para la hipótesis de resiliencia.

# %%
perturbations = []
policies = sorted({r["policy"] for r in resilience if r["policy"] != "baseline"})
for p in sorted({r["perturbation"] for r in resilience}):
    row = {"perturbation": p}
    for policy in policies:
        match = next(r for r in resilience if r["perturbation"] == p and r["policy"] == policy)
        row[policy] = match["censored_wait_improvement_vs_baseline_pct"]
    perturbations.append(row)

x = range(len(perturbations))
width = 0.8 / len(policies)
plt.figure(figsize=(13, 6))
for idx, policy in enumerate(policies):
    offset = (idx - (len(policies) - 1) / 2) * width
    plt.bar([i + offset for i in x], [r[policy] for r in perturbations], width=width, label=policy)
plt.axhline(0, linewidth=1)
plt.xticks(list(x), [r["perturbation"] for r in perturbations], rotation=25, ha="right")
plt.ylabel("Mejora espera censurada (%)")
plt.title("¿Cuánto ayuda BusComodin cuando la red se degrada?")
plt.legend()
plt.tight_layout()
plt.show()

# %% [markdown]
# ## 6. Espera censurada en C04 al 50%
# Incluye correctamente a pasajeros que permanecen esperando al terminar el horizonte.

# %%
plt.figure(figsize=(9, 5))
plt.bar([r["policy"] for r in c04], [r["mean_censored_wait_minutes"] for r in c04])
plt.ylabel("Espera censurada media (min)")
plt.title("C04 al 50% de oferta — costo total de espera")
plt.xticks(rotation=20, ha="right")
plt.tight_layout()
plt.show()

# %% [markdown]
# ## 7. Tasa de servicio bajo perturbaciones
# Una política no debe parecer buena simplemente porque deja sin transportar a los
# pasajeros que más esperan.

# %%
for perturbation in ["normal", "C04_half_service", "C01_C02_half_service"]:
    rows = [r for r in resilience if r["perturbation"] == perturbation]
    plt.figure(figsize=(9, 4))
    plt.bar([r["policy"] for r in rows], [r["mean_service_rate_pct"] for r in rows])
    plt.ylim(90, 100.5)
    plt.ylabel("Pasajeros atendidos (%)")
    plt.title(f"Tasa de servicio — {perturbation}")
    plt.xticks(rotation=20, ha="right")
    plt.tight_layout()
    plt.show()

# %% [markdown]
# ## 8. Hipótesis y próximo gráfico decisivo
#
# > Una pequeña flota de refuerzo reasignable puede absorber disrupciones locales
# > mejor que una asignación rígida de la misma capacidad.
#
# El siguiente experimento debe comparar **igual cantidad total de buses**:
# `fixed-extra` vs `flexible-extra`, N=1..5. Cuando ese runner exista, este notebook
# debe incorporar un gráfico de mejora vs número de buses y otro de utilización/
# reposicionamiento. Ese será el test visual principal de la hipótesis.
