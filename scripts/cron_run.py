#!/usr/bin/env python3
"""
Cron entry point: run pipeline (and optionally approval check) with logging.
Use this on Hostinger or any server with cron.

  python scripts/cron_run.py              → run pipeline only
  python scripts/cron_run.py --approval  → run pipeline, then approval check

Logs go to logs/cron.log (created automatically).
"""
import sys
import subprocess
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent
LOG_DIR = ROOT / "logs"
LOG_FILE = LOG_DIR / "cron.log"

# Prefer venv Python so cron uses the same deps as local
PYTHON = ROOT / ".venv" / "bin" / "python"
if not PYTHON.exists():
    PYTHON = Path(sys.executable)


def main() -> None:
    run_approval = "--approval" in sys.argv
    LOG_DIR.mkdir(exist_ok=True)

    with open(LOG_FILE, "a", encoding="utf-8") as log:
        def write(msg: str) -> None:
            log.write(msg)
            log.flush()

        ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        write(f"\n--- {ts} (cron_run.py) ---\n")

        # Run pipeline
        write("Running pipeline...\n")
        r = subprocess.run(
            [str(PYTHON), str(ROOT / "scripts" / "run_pipeline.py")],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=300,
        )
        write(r.stdout or "")
        if r.stderr:
            write("stderr: " + r.stderr)
        if r.returncode != 0:
            write(f"Pipeline exit code: {r.returncode}\n")
            sys.exit(r.returncode)
        write("Pipeline OK.\n")

        if run_approval:
            write("Running approval check...\n")
            r2 = subprocess.run(
                [str(PYTHON), str(ROOT / "scripts" / "run_approval_check.py")],
                cwd=str(ROOT),
                capture_output=True,
                text=True,
                timeout=120,
            )
            write(r2.stdout or "")
            if r2.stderr:
                write("stderr: " + r2.stderr)
            write(f"Approval check exit code: {r2.returncode}\n")

        write("Done.\n")


if __name__ == "__main__":
    main()
