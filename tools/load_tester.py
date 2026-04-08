"""
Basic HTTP load tester that fires concurrent GET requests to a target host.

Usage:
    python tools/load_tester.py <ip> <port> <total_requests>

Example:
    python tools/load_tester.py 127.0.0.1 8000 50
"""

import sys
import threading

import requests


def send_request(url: str, request_id: int) -> None:
    """Send a single GET request and print the result."""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code < 400:
            print(f"Request {request_id}: Successful (status {response.status_code})")
        else:
            print(f"Request {request_id}: Failed (status {response.status_code})")
    except Exception as e:
        print(f"Request {request_id}: Failed (error: {e})")


def main() -> None:
    if len(sys.argv) != 4:
        print("Usage: python tools/load_tester.py <ip> <port> <total_requests>")
        print("Example: python tools/load_tester.py 127.0.0.1 8000 50")
        sys.exit(1)

    ip = sys.argv[1]
    port = sys.argv[2]
    total = int(sys.argv[3])

    url = f"http://{ip}:{port}"
    print(f"Testing {total} requests to {url}...")

    threads = [
        threading.Thread(target=send_request, args=(url, i + 1))
        for i in range(total)
    ]

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    print("Done.")


if __name__ == "__main__":
    main()
