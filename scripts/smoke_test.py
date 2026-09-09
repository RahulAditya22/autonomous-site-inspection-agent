"""Offline smoke check for the project structure."""

from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    required = [
        root / ".env.example",
        root / "requirements.txt",
        root / "README.md",
        root / "backend" / "run.py",
        root / "backend" / "app" / "services" / "vision.py",
        root / "backend" / "app" / "services" / "actions.py",
    ]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise SystemExit("Missing required files:\n" + "\n".join(missing))
    print("AeroGuard structure OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
