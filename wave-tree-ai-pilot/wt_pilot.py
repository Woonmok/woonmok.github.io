import argparse
import json
import os
import sys
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from rich import print
from rich.table import Table
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_percentage_error, mean_squared_error

# -----------------------------
# Config / Utilities
# -----------------------------
DEFAULT_CONFIG = {
    "project": {
        "name": "Wave Tree AI Infra Pilot",
        "timezone": "Asia/Seoul",
    },
    "kpi": {
        "target_mape_baseline": 0.18,   # baseline acceptable threshold (example)
        "target_speedup_blackwell": 1.30,  # >= 1.3x speedup vs baseline (example)
        "target_cost_efficiency": 1.15, # >= 1.15x better (example)
    },
    "servers": {
        "A": {"role": "baseline_training", "gpu": "A100x4", "rate_gpu_hours_per_min": 0.25},
        "B": {"role": "optimization_sweeps", "gpu": "L40Sx8", "rate_gpu_hours_per_min": 0.35},
        "C": {"role": "inference_reporting", "gpu": "RTX6000Ada x4", "rate_gpu_hours_per_min": 0.10},
        "BW": {"role": "blackwell_benchmark", "gpu": "Blackwell (pilot)", "rate_gpu_hours_per_min": 0.22},
    },
    "data": {
        "growth_csv": "data/growth.csv",
        "seed": 42,
    },
    "runs": {
        "dir": "runs",
        "reports_dir": "reports",
    }
}

def now_kst_str():
    # KST fixed offset handling without pytz
    # (For logging only; not used for scheduling)
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

def ensure_dirs(*paths: str):
    for p in paths:
        Path(p).mkdir(parents=True, exist_ok=True)

def load_or_init_config(path: str) -> dict:
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    else:
        with open(path, "w", encoding="utf-8") as f:
            yaml.safe_dump(DEFAULT_CONFIG, f, sort_keys=False, allow_unicode=True)
        return DEFAULT_CONFIG

def write_json(path: str, obj: dict):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

def read_csv_or_generate(csv_path: str, seed: int = 42) -> pd.DataFrame:
    """
    If data/growth.csv doesn't exist, generate a synthetic mycelium growth dataset.
    Columns:
      - temp_c, humidity_pct, nutrient_g_l, ph, time_hr, agitation_rpm
      - growth_index (target)
    """
    p = Path(csv_path)
    if p.exists():
        df = pd.read_csv(p)
        return df

    rng = np.random.default_rng(seed)
    n = 2500

    temp = rng.normal(26, 2.5, n).clip(18, 34)
    humidity = rng.normal(78, 8, n).clip(40, 95)
    nutrient = rng.normal(12, 3, n).clip(2, 22)
    ph = rng.normal(6.2, 0.4, n).clip(4.8, 7.4)
    time_hr = rng.uniform(4, 72, n)
    agitation = rng.normal(120, 60, n).clip(0, 300)

    # Underlying synthetic "biology-like" response curve (toy)
    # Favor: temp around 27, humidity around 80, nutrient around 13, pH around 6.2
    growth = (
        1.2
        * np.exp(-((temp - 27) ** 2) / (2 * 2.8**2))
        * np.exp(-((humidity - 80) ** 2) / (2 * 10**2))
        * np.exp(-((nutrient - 13) ** 2) / (2 * 3.5**2))
        * np.exp(-((ph - 6.2) ** 2) / (2 * 0.45**2))
        * (1 - np.exp(-time_hr / 20))
        * (0.85 + 0.15 * (agitation / 300))
    )

    noise = rng.normal(0, 0.03, n)
    growth_index = (growth + noise).clip(0, None)

    df = pd.DataFrame({
        "temp_c": temp,
        "humidity_pct": humidity,
        "nutrient_g_l": nutrient,
        "ph": ph,
        "time_hr": time_hr,
        "agitation_rpm": agitation,
        "growth_index": growth_index,
    })

    ensure_dirs(p.parent.as_posix())
    df.to_csv(p, index=False)
    return df

@dataclass
class RunMeta:
    run_id: str
    timestamp_utc: str
    server: str
    label: str
    gpu: str
    gpu_hours: float
    notes: str

def new_run_id(prefix: str) -> str:
    return f"{prefix}-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"

def estimate_gpu_hours(server_cfg: dict, minutes_spent: float) -> float:
    return float(server_cfg.get("rate_gpu_hours_per_min", 0.1) * minutes_spent)

def pretty_metrics_table(metrics: dict, title: str = "Metrics"):
    t = Table(title=title)
    t.add_column("Metric")
    t.add_column("Value", justify="right")
    for k, v in metrics.items():
        if isinstance(v, float):
            t.add_row(k, f"{v:.6f}")
        else:
            t.add_row(k, str(v))
    print(t)

# -----------------------------
# Core: A / B / C / Blackwell
# -----------------------------

def server_a_baseline(cfg: dict, config_path: str):
    """
    Server A: Train baseline model (ground truth proxy)
    Output:
      - runs/<run_id>/baseline_model.pkl (optional; here we store model params and metrics)
      - runs/<run_id>/baseline_metrics.json
    """
    run_id = new_run_id("A")
    run_dir = Path(cfg["runs"]["dir"]) / run_id
    ensure_dirs(run_dir.as_posix())

    df = read_csv_or_generate(cfg["data"]["growth_csv"], seed=cfg["data"]["seed"])
    X = df.drop(columns=["growth_index"])
    y = df["growth_index"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=cfg["data"]["seed"])

    # lightweight baseline
    model = RandomForestRegressor(
        n_estimators=300,
        random_state=cfg["data"]["seed"],
        n_jobs=-1
    )

    start = time.time()
    model.fit(X_train, y_train)
    pred = model.predict(X_test)
    elapsed = time.time() - start
    minutes = max(elapsed / 60, 0.2)

    mape = float(mean_absolute_percentage_error(y_test, pred))
    rmse = float(np.sqrt(mean_squared_error(y_test, pred)))

    gpu_hours = estimate_gpu_hours(cfg["servers"]["A"], minutes)

    metrics = {
        "run_id": run_id,
        "server": "A",
        "gpu": cfg["servers"]["A"]["gpu"],
        "elapsed_sec": float(elapsed),
        "estimated_gpu_hours": gpu_hours,
        "mape": mape,
        "rmse": rmse,
        "rows": int(len(df)),
        "features": list(X.columns),
    }

    write_json((run_dir / "baseline_metrics.json").as_posix(), metrics)

    meta = RunMeta(
        run_id=run_id,
        timestamp_utc=now_kst_str(),
        server="A",
        label="RUNNING→READY",
        gpu=cfg["servers"]["A"]["gpu"],
        gpu_hours=gpu_hours,
        notes="Baseline model trained (toy RF). Replace with real training pipeline later."
    )
    write_json((run_dir / "run_meta.json").as_posix(), asdict(meta))

    print(f"[bold green]Server A baseline complete[/bold green] → {run_dir}")
    pretty_metrics_table(metrics, title="Server A Baseline Metrics")


def server_b_optimize(cfg: dict, baseline_run: str):
    """
    Server B: Run optimization sweeps (simulate search for best conditions).
    Uses baseline model metrics as anchor; here we perform a simple randomized search
    for input conditions maximizing predicted growth.
    Output:
      - runs/<run_id>/opt_results.json (Top 5 conditions)
    """
    baseline_dir = Path(cfg["runs"]["dir"]) / baseline_run
    baseline_metrics_path = baseline_dir / "baseline_metrics.json"
    if not baseline_metrics_path.exists():
        print(f"[bold red]Baseline metrics not found:[/bold red] {baseline_metrics_path}")
        sys.exit(1)

    run_id = new_run_id("B")
    run_dir = Path(cfg["runs"]["dir"]) / run_id
    ensure_dirs(run_dir.as_posix())

    df = read_csv_or_generate(cfg["data"]["growth_csv"], seed=cfg["data"]["seed"])
    X = df.drop(columns=["growth_index"])
    y = df["growth_index"]

    # Re-train quickly to simulate having the baseline model artifact available.
    # In production, load the trained model artifact from Server A.
    model = RandomForestRegressor(
        n_estimators=250,
        random_state=cfg["data"]["seed"],
        n_jobs=-1
    )

    start = time.time()
    model.fit(X, y)

    rng = np.random.default_rng(cfg["data"]["seed"] + 7)
    n_trials = 1500

    # sample candidate conditions within observed ranges
    cand = pd.DataFrame({
        "temp_c": rng.uniform(X["temp_c"].min(), X["temp_c"].max(), n_trials),
        "humidity_pct": rng.uniform(X["humidity_pct"].min(), X["humidity_pct"].max(), n_trials),
        "nutrient_g_l": rng.uniform(X["nutrient_g_l"].min(), X["nutrient_g_l"].max(), n_trials),
        "ph": rng.uniform(X["ph"].min(), X["ph"].max(), n_trials),
        "time_hr": rng.uniform(X["time_hr"].min(), X["time_hr"].max(), n_trials),
        "agitation_rpm": rng.uniform(X["agitation_rpm"].min(), X["agitation_rpm"].max(), n_trials),
    })

    preds = model.predict(cand)
    cand["pred_growth_index"] = preds
    top = cand.sort_values("pred_growth_index", ascending=False).head(5)

    elapsed = time.time() - start
    minutes = max(elapsed / 60, 0.3)
    gpu_hours = estimate_gpu_hours(cfg["servers"]["B"], minutes)

    results = {
        "run_id": run_id,
        "server": "B",
        "gpu": cfg["servers"]["B"]["gpu"],
        "elapsed_sec": float(elapsed),
        "estimated_gpu_hours": gpu_hours,
        "trials": int(n_trials),
        "top5": top.to_dict(orient="records"),
        "baseline_anchor": baseline_run
    }
    write_json((run_dir / "opt_results.json").as_posix(), results)

    meta = RunMeta(
        run_id=run_id,
        timestamp_utc=now_kst_str(),
        server="B",
        label="QUEUE→RUNNING→OPTIMIZING",
        gpu=cfg["servers"]["B"]["gpu"],
        gpu_hours=gpu_hours,
        notes="Optimization sweeps completed (random search toy). Replace with Bayesian optimization later."
    )
    write_json((run_dir / "run_meta.json").as_posix(), asdict(meta))

    print(f"[bold green]Server B optimization complete[/bold green] → {run_dir}")
    pretty_metrics_table({
        "run_id": run_id,
        "baseline_anchor": baseline_run,
        "trials": n_trials,
        "estimated_gpu_hours": gpu_hours
    }, title="Server B Optimization Summary")
    print("[bold]Top 5 candidate conditions:[/bold]")
    print(top)


def server_c_report(cfg: dict, baseline_run: str, optimize_run: str):
    """
    Server C: Produce decision-ready report assets:
      - reports/report_<date>.md
      - reports/summary.json
    """
    base_dir = Path(cfg["runs"]["dir"]) / baseline_run
    opt_dir = Path(cfg["runs"]["dir"]) / optimize_run

    base_path = base_dir / "baseline_metrics.json"
    opt_path = opt_dir / "opt_results.json"

    if not base_path.exists() or not opt_path.exists():
        print("[bold red]Missing inputs for report.[/bold red]")
        print(f"baseline_metrics: {base_path}")
        print(f"opt_results: {opt_path}")
        sys.exit(1)

    base = json.loads(base_path.read_text(encoding="utf-8"))
    opt = json.loads(opt_path.read_text(encoding="utf-8"))

    # Minimal KPI framing
    # "cost efficiency" toy: better predicted growth per gpu-hour of optimization (illustrative)
    top5 = opt["top5"]
    best_pred = float(top5[0]["pred_growth_index"])
    cost_eff = best_pred / max(opt["estimated_gpu_hours"], 1e-6)

    report_date = datetime.utcnow().strftime("%Y%m%d")
    report_md = Path(cfg["runs"]["reports_dir"]) / f"report_{report_date}.md"
    ensure_dirs(Path(cfg["runs"]["reports_dir"]).as_posix())

    md = []
    md.append(f"# AI Infra Pilot Report — {report_date}")
    md.append("")
    md.append("## 1) Baseline (Server A)")
    md.append(f"- Run: `{baseline_run}`")
    md.append(f"- GPU: {base.get('gpu')}")
    md.append(f"- MAPE: {base.get('mape'):.4f}")
    md.append(f"- RMSE: {base.get('rmse'):.4f}")
    md.append(f"- Est. GPU-hrs: {base.get('estimated_gpu_hours'):.3f}")
    md.append("")
    md.append("## 2) Optimization Sweeps (Server B)")
    md.append(f"- Run: `{optimize_run}`")
    md.append(f"- GPU: {opt.get('gpu')}")
    md.append(f"- Trials: {opt.get('trials')}")
    md.append(f"- Est. GPU-hrs: {opt.get('estimated_gpu_hours'):.3f}")
    md.append("")
    md.append("### Top 5 Candidate Conditions (predicted best)")
    for i, row in enumerate(top5, 1):
        md.append(f"{i}. temp={row['temp_c']:.2f}C, hum={row['humidity_pct']:.1f}%, nutrient={row['nutrient_g_l']:.2f} g/L, pH={row['ph']:.2f}, time={row['time_hr']:.1f}h, agit={row['agitation_rpm']:.0f}rpm → pred={row['pred_growth_index']:.4f}")
    md.append("")
    md.append("## 3) Decision Snapshot (Server C)")
    md.append(f"- Best predicted growth_index: {best_pred:.4f}")
    md.append(f"- Toy cost-efficiency (best_pred / GPU-hrs_B): {cost_eff:.4f}")
    md.append("")
    md.append("## 4) Wave Tree Status Labels (recommended)")
    md.append("- Global Biz: `PIPELINE`")
    md.append("- POM Core: `DESIGN`")
    md.append("- AI Infra: `RUNNING` (during pilot), then `REVIEW` for decision")
    md.append("")
    md.append("## 5) Next Actions (tickets)")
    md.append(f"- WT-PILOT-A: validate baseline with real growth data (replace synthetic)")
    md.append(f"- WT-PILOT-B: replace random search with Bayesian optimization; add constraints")
    md.append(f"- WT-PILOT-C: integrate real GPU telemetry and job logs")

    report_md.write_text("\n".join(md), encoding="utf-8")

    summary = {
        "baseline_run": baseline_run,
        "optimize_run": optimize_run,
        "best_pred_growth_index": best_pred,
        "toy_cost_efficiency": cost_eff,
        "labels": {
            "Global Biz": "PIPELINE",
            "POM Core": "DESIGN",
            "AI Infra": "RUNNING→REVIEW"
        }
    }
    write_json((Path(cfg["runs"]["reports_dir"]) / f"summary_{report_date}.json").as_posix(), summary)

    print(f"[bold green]Server C report created[/bold green] → {report_md}")
    pretty_metrics_table(summary, title="Report Summary")


def blackwell_benchmark(cfg: dict, baseline_run: str):
    """
    Blackwell pilot: benchmark vs baseline using toy timing model.
    In reality, you will run the SAME training script on Blackwell and compare:
      - elapsed time
      - gpu-hours
      - accuracy
    Here we simulate expected speedup / efficiency to produce decision-ready numbers.
    """
    base_dir = Path(cfg["runs"]["dir"]) / baseline_run
    base_path = base_dir / "baseline_metrics.json"
    if not base_path.exists():
        print(f"[bold red]Baseline metrics not found:[/bold red] {base_path}")
        sys.exit(1)

    base = json.loads(base_path.read_text(encoding="utf-8"))

    run_id = new_run_id("BW")
    run_dir = Path(cfg["runs"]["dir"]) / run_id
    ensure_dirs(run_dir.as_posix())

    # Toy assumptions: speedup sampled; cost-efficiency derived
    rng = np.random.default_rng(cfg["data"]["seed"] + 99)
    speedup = float(rng.uniform(1.15, 1.60))  # simulate
    base_elapsed = float(base["elapsed_sec"])
    bw_elapsed = base_elapsed / speedup

    # estimate gpu-hours with BW rate
    base_gpuhrs = float(base["estimated_gpu_hours"])
    bw_minutes = max((bw_elapsed / 60), 0.2)
    bw_gpuhrs = estimate_gpu_hours(cfg["servers"]["BW"], bw_minutes)

    # assume accuracy similar within tiny delta (toy)
    mape_base = float(base["mape"])
    mape_bw = float(np.clip(mape_base + rng.normal(0, 0.01), 0, 1))

    result = {
        "run_id": run_id,
        "server": "BW",
        "gpu": cfg["servers"]["BW"]["gpu"],
        "baseline_anchor": baseline_run,
        "baseline_elapsed_sec": base_elapsed,
        "blackwell_elapsed_sec": bw_elapsed,
        "speedup": speedup,
        "baseline_gpu_hours": base_gpuhrs,
        "blackwell_gpu_hours": bw_gpuhrs,
        "baseline_mape": mape_base,
        "blackwell_mape": mape_bw,
        "cost_efficiency_ratio": (base_gpuhrs / max(bw_gpuhrs, 1e-6)),  # >1 means BW uses fewer gpu-hrs (toy)
    }
    write_json((run_dir / "blackwell_benchmark.json").as_posix(), result)

    meta = RunMeta(
        run_id=run_id,
        timestamp_utc=now_kst_str(),
        server="BW",
        label="DESIGN→RUNNING→REVIEW",
        gpu=cfg["servers"]["BW"]["gpu"],
        gpu_hours=bw_gpuhrs,
        notes="Toy benchmark. Replace with actual BW run of the exact training script."
    )
    write_json((run_dir / "run_meta.json").as_posix(), asdict(meta))

    print(f"[bold green]Blackwell benchmark complete[/bold green] → {run_dir}")
    pretty_metrics_table(result, title="Blackwell Benchmark (Toy)")

# -----------------------------
# CLI
# -----------------------------

def main():
    ap = argparse.ArgumentParser(description="Wave Tree AI Infra Pilot (MVP)")
    ap.add_argument("--config", default="pilot_config.yaml", help="Path to config YAML (auto-created if missing).")

    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("init", help="Create config + generate synthetic data if needed.")

    a = sub.add_parser("server-a", help="Run Server A baseline training (toy).")
    # no extra args

    b = sub.add_parser("server-b", help="Run Server B optimization sweeps (toy).")
    b.add_argument("--baseline-run", required=True, help="Baseline run_id produced by server-a.")

    c = sub.add_parser("server-c", help="Run Server C reporting.")
    c.add_argument("--baseline-run", required=True)
    c.add_argument("--optimize-run", required=True)

    bw = sub.add_parser("blackwell", help="Run Blackwell benchmark (toy compare).")
    bw.add_argument("--baseline-run", required=True)

    args = ap.parse_args()
    cfg = load_or_init_config(args.config)
    ensure_dirs(cfg["runs"]["dir"], cfg["runs"]["reports_dir"], "data")

    if args.cmd == "init":
        _ = read_csv_or_generate(cfg["data"]["growth_csv"], seed=cfg["data"]["seed"])
        print("[bold green]Initialized[/bold green]")
        print(f"- config: {args.config}")
        print(f"- data: {cfg['data']['growth_csv']}")
        return

    if args.cmd == "server-a":
        server_a_baseline(cfg, args.config)
        return

    if args.cmd == "server-b":
        server_b_optimize(cfg, args.baseline_run)
        return

    if args.cmd == "server-c":
        server_c_report(cfg, args.baseline_run, args.optimize_run)
        return

    if args.cmd == "blackwell":
        blackwell_benchmark(cfg, args.baseline_run)
        return

if __name__ == "__main__":
    main()
