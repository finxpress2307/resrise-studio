import argparse
import os
import subprocess
import sys
import time
from datetime import datetime

ACCOUNTS = ["avanyamehra", "mairamehraofficial", "iamgagankumar", "resrise", "gagankumarrocks"]
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "..")) if os.path.basename(SCRIPT_DIR).lower() == "scripts" else SCRIPT_DIR


def log(msg: str) -> None:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] [AUTORUN] {msg}", flush=True)


def launch_parallel_all(mode: str = "both") -> None:
    launcher = os.path.join(PROJECT_DIR, "launch_parallel_terminals.py")
    subprocess.run([sys.executable, launcher, "--mode", mode])


def autorun_sequential_loop(minutes_per_account: int, mode: str, target_accounts: list) -> None:
    log(
        f"Autorun sequential loop | Accounts: {', '.join('@' + a for a in target_accounts)} "
        f"| {minutes_per_account} min/account | Mode: {mode}"
    )
    cycle = 1
    try:
        while True:
            log(f"=== Cycle #{cycle} ===")
            for account in target_accounts:
                log(f"Starting {mode} for @{account}...")
                run_cmd = [
                    sys.executable,
                    os.path.join(PROJECT_DIR, "run_account.py"),
                    "--account",
                    account,
                    "--mode",
                    mode,
                    "--once",
                ]
                proc = subprocess.Popen(run_cmd)
                start_time = time.time()
                deadline = start_time + (minutes_per_account * 60)
                while time.time() < deadline:
                    if proc.poll() is not None:
                        break
                    time.sleep(2.0)
                if proc.poll() is None:
                    if os.name == "nt":
                        subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    else:
                        proc.terminate()
            cycle += 1
    except KeyboardInterrupt:
        log("Autorun stopped by user.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run Instagram automation: either in 3 parallel terminal windows or for a single account."
    )
    parser.add_argument(
        "--parallel",
        action="store_true",
        default=False,
        help="Launch accounts simultaneously in separate terminals (requires distinct network proxies to avoid IP clustering)",
    )
    parser.add_argument(
        "--sequential",
        action="store_true",
        default=True,
        help="Run accounts sequentially one-by-one with rest intervals (Default & Recommended)",
    )
    parser.add_argument(
        "-a",
        "--account",
        choices=ACCOUNTS,
        help="Run only for this specific account in the current terminal",
    )
    parser.add_argument(
        "--mode",
        choices=["both", "feed", "stories", "replier"],
        default="both",
        help="Automation mode: 'both', 'feed', 'stories', or 'replier' (default: both)",
    )
    parser.add_argument(
        "--minutes",
        type=int,
        default=45,
        help="Minutes per account (for sequential mode)",
    )
    args = parser.parse_args()

    if args.account:
        from run_account import main_loop
        main_loop(account=args.account, mode=args.mode)
    elif args.sequential:
        autorun_sequential_loop(args.minutes, args.mode, ACCOUNTS)
    else:
        # Default: Launch all accounts concurrently in 3 dedicated terminals
        launch_parallel_all(args.mode)
