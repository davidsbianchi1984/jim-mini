"""``python -m botcleaner [--host 127.0.0.1] [--port 8000]`` — run the web app and API."""
import argparse

import uvicorn


def main() -> None:
    p = argparse.ArgumentParser(description="Bot Account Cleaner server")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8000)
    a = p.parse_args()
    uvicorn.run("botcleaner.api:create_app", factory=True, host=a.host, port=a.port)


if __name__ == "__main__":
    main()
