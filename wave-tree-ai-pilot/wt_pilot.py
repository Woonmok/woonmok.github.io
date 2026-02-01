import argparse, json, os, sys, time
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

def ensure_dirs(*paths: str):
    for p in paths:
        Path(p).mkdir(parents=True, exist_ok=True)

def load_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def write_json(path: str, obj: dict):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

def now_utc_str():
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

def new_run_id(prefix: str) -> str:
    return f"{prefix}-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"

def read_or_generate_growth(csv_path: str, seed: int = 42) -> pd.DataFrame:
    p = Path(csv_path)
    if p.exists():
        return pd.read_csv(p)

    rng = np.random.default_rng(seed)
    n = 2500
    temp = rng.normal(26, 2.5, n).clip(18, 34)
    humidity = rng.normal(78, 8, n).clip(40, 95)
    nutrient = rng.normal(12, 3, n).clip(2, 22)
    ph = rng.normal(6.2, 0.4, n).clip(4.8, 7.4)
    time_hr = rng.uniform(4, 72, n)
    agitation = rng.normal(120, 60, n).clip(0, 300)

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

def pretty_table(d: dict, title: str):
    t = Table(title=title)
    t.add_column("Key")
    t.add_column("Value", justify="right")
    for k, v in d.items():
        if isinstance(v, float):
            t.add_row(k, f"{v:.6f}")
        else:
            t.add_row(k, str(v))
    print(t)

@dataclass
class RunMeta:
    run_id: str
    timestamp_utc: str
    server: str
    label: str
    gpu: str
    gpu_hours: float
    notes: str

def est_gpu_hours(rate_per_min: float, minutes: float) -> float:
    return float(rate_per_min * minutes)

def cmd_init(cfg: dict):
    _ = read_or_generate_growth(cfg["data"]["growth_csv"], seed=cfg["data"]["seed"])
    print("[bold green]Initialized[/bold green]")
    print(f"- data: {cfg['data']['growth_csv']}")

def cmd_server_a(cfg: dict):
    run_id = new_run_id("A")
    run_dir = Path(cfg["runs"]["dir"]) / run_id
    ensure_dirs(run_dir.as_posix())

    df = read_or_generate_growth(cfg["data"]["growth_csv"], seed=cfg["data"]["seed"])
    X = df.drop(columns=["growth_index"])
    y = df["growth_index"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=cfg["data"]["seed"])

    model = RandomForestRegressor(n_estimators=300, random_state=cfg["data"]["seed"], n_jobs=-1)

    start = time.time()
    model.fit(X_train, y_train)
    pred = model.predict(X_test)
    elapsed = time.time() - start
    minutes = max(elapsed / 60, 0.2)

    mape = float(mean_absolute_percentage_error(y_test, pred))
    rmse = float(np.sqrt(mean_squared_error(y_test, pred)))

    rate = float(cfg["servers"]["A"]["rate_gpu_hours_per_min"])
    gpu_hours = est_gpu_hours(rate, minutes)

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

    meta = RunMeta(run_id, now_utc_str(), "A", "RUNNING→READY", cfg["servers"]["A"]["gpu"], gpu_hours,
                   "Baseline model trained (toy). Replace with real training later.")
    write_json((run_dir / "run_meta.json").as_posix(), asdict(meta))

    print(f"[bold green]Server A complete[/bold green] → {run_dir}")
    pretty_table(metrics, "Server A Metrics")

def cmd_server_b(cfg: dict, baseline_run: str):
    base_dir = Path(cfg["runs"]["dir"]) / baseline_run
    base_path = base_dir / "baseline_metrics.json"
    if not base_path.exists():
        print(f"[bold red]Missing baseline metrics:[/bold red] {base_path}")
        sys.exit(1)

    run_id = new_run_id("B")
    run_dir = Path(cfg["runs"]["dir"]) / run_id
    ensure_dirs(run_dir.as_posix())

    df = read_or_generate_growth(cfg["data"]["growth_csv"], seed=cfg["data"]["seed"])
    X = df.drop(columns=["growth_index"])
    y = df["growth_index"]

    model = RandomForestRegressor(n_estimators=250, random_state=cfg["data"]["seed"], n_jobs=-1)

    start = time.time()
    model.fit(X, y)

    rng = np.random.default_rng(cfg["data"]["seed"] + 7)
    n_trials = 1500
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
    rate = float(cfg["servers"]["B"]["rate_gpu_hours_per_min"])
    gpu_hours = est_gpu_hours(rate, minutes)

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

    meta = RunMeta(run_id, now_utc_str(), "B", "QUEUE→RUNNING→OPTIMIZING", cfg["servers"]["B"]["gpu"], gpu_hours,
                   "Optimization sweeps (toy). Replace with Bayesian optimization later.")
    write_json((run_dir / "run_meta.json").as_posix(), asdict(meta))

    print(f"[bold green]Server B complete[/bold green] → {run_dir}")
    pretty_table({"run_id": run_id, "baseline": baseline_run, "trials": n_trials, "gpu_hours": gpu_hours}, "Server B Summary")
    print("[bold]Top 5 candidate conditions:[/bold]")
    print(top)

def cmd_server_c(cfg: dict, baseline_run: str, optimize_run: str):
    base_dir = Path(cfg["runs"]["dir"]) / baseline_run
    opt_dir = Path(cfg["runs"]["dir"]) / optimize_run

    base_path = base_dir / "baseline_metrics.json"
    opt_path = opt_dir / "opt_results.json"
    if not base_path.exists() or not opt_path.exists():
        print("[bold red]Missing inputs for report.[/bold red]")
        print(f"- {base_path}")
        print(f"- {opt_path}")
        sys.exit(1)

    base = json.loads(base_path.read_text(encoding="utf-8"))
    opt = json.loads(opt_path.read_text(encoding="utf-8"))

    top5 = opt["top5"]
    best_pred = float(top5[0]["pred_growth_index"])
    cost_eff = best_pred / max(opt["estimated_gpu_hours"], 1e-6)

    report_date = datetime.utcnow().strftime("%Y%m%d")
    ensure_dirs(cfg["runs"]["reports_dir"])
    report_md = Path(cfg["runs"]["reports_dir"]) / f"report_{report_date}.md"

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
        md.append(
            f"{i}. temp={row['temp_c']:.2f}C, hum={row['humidity_pct']:.1f}%, nutrient={row['nutrient_g_l']:.2f} g/L, "
            f"pH={row['ph']:.2f}, time={row['time_hr']:.1f}h, agit={row['agitation_rpm']:.0f}rpm → pred={row['pred_growth_index']:.4f}"
        )
    md.append("")
    md.append("## 3) Decision Snapshot (Server C)")
    md.append(f"- Best predicted growth_index: {best_pred:.4f}")
    md.append(f"- Toy cost-efficiency (best_pred / GPU-hrs_B): {cost_eff:.4f}")
    md.append("")
    md.append("## 4) Wave Tree Status Labels (recommended)")
    md.append("- Global Biz: `PIPELINE`")
    md.append("- POM Core: `DESIGN`")
    md.append("- AI Infra: `RUNNING→REVIEW`")
    md.append("")
    md.append("## 5) Next Tickets")
    md.append("- WT-PILOT-A: replace synthetic data with real measurements")
    md.append("- WT-PILOT-B: add constraints + Bayesian optimization")
    md.append("- WT-PILOT-C: integrate real telemetry later")

    report_md.write_text("\n".join(md), encoding="utf-8")

    summary = {
        "baseline_run": baseline_run,
        "optimize_run": optimize_run,
        "best_pred_growth_index": best_pred,
        "toy_cost_efficiency": cost_eff,
        "labels": {"Global Biz": "PIPELINE", "POM Core": "DESIGN", "AI Infra": "RUNNING→REVIEW"},
    }
    write_json((Path(cfg["runs"]["reports_dir"]) / f"summary_{report_date}.json").as_posix(), summary)

    print(f"[bold green]Report created[/bold green] → {report_md}")
    pretty_table(summary, "Report Summary")

def cmd_blackwell(cfg: dict, baseline_run: str):
    base_dir = Path(cfg["runs"]["dir"]) / baseline_run
    base_path = base_dir / "baseline_metrics.json"
    if not base_path.exists():
        print(f"[bold red]Missing baseline metrics:[/bold red] {base_path}")
        sys.exit(1)

    base = json.loads(base_path.read_text(encoding="utf-8"))

    run_id = new_run_id("BW")
    run_dir = Path(cfg["runs"]["dir"]) / run_id
    ensure_dirs(run_dir.as_posix())

    rng = np.random.default_rng(cfg["data"]["seed"] + 99)
    speedup = float(rng.uniform(1.15, 1.60))  # toy
    base_elapsed = float(base["elapsed_sec"])
    bw_elapsed = base_elapsed / speedup

    bw_minutes = max((bw_elapsed / 60), 0.2)
    bw_rate = float(cfg["servers"]["BW"]["rate_gpu_hours_per_min"])
    bw_gpuhrs = est_gpu_hours(bw_rate, bw_minutes)

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
        "baseline_gpu_hours": float(base["estimated_gpu_hours"]),
        "blackwell_gpu_hours": bw_gpuhrs,
        "baseline_mape": mape_base,
        "blackwell_mape": mape_bw,
        "toy_cost_efficiency_ratio": (float(base["estimated_gpu_hours"]) / max(bw_gpuhrs, 1e-6))
    }
    write_json((run_dir / "blackwell_benchmark.json").as_posix(), result)

    meta = RunMeta(run_id, now_utc_str(), "BW", "DESIGN→RUNNING→REVIEW", cfg["servers"]["BW"]["gpu"], bw_gpuhrs,
                   "Toy benchmark. Replace with actual Blackwell run later.")
    write_json((run_dir / "run_meta.json").as_posix(), asdict(meta))

    print(f"[bold green]Blackwell benchmark complete[/bold green] → {run_dir}")
    pretty_table(result, "Blackwell Benchmark (Toy)")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="pilot_config.yaml")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("init")
    sub.add_parser("server-a")

    b = sub.add_parser("server-b")
    b.add_argument("--baseline-run", required=True)

    c = sub.add_parser("server-c")
    c.add_argument("--baseline-run", required=True)
    c.add_argument("--optimize-run", required=True)

    bw = sub.add_parser("blackwell")
    bw.add_argument("--baseline-run", required=True)

    args = ap.parse_args()
    cfg = load_config(args.config)
    ensure_dirs(cfg["runs"]["dir"], cfg["runs"]["reports_dir"], "data")

    if args.cmd == "init":
        cmd_init(cfg)
    elif args.cmd == "server-a":
        cmd_server_a(cfg)
    elif args.cmd == "server-b":
        cmd_server_b(cfg, args.baseline_run)
    elif args.cmd == "server-c":
        cmd_server_c(cfg, args.baseline_run, args.optimize_run)
    elif args.cmd == "blackwell":
        cmd_blackwell(cfg, args.baseline_run)

if __name__ == "__main__":
    main()
