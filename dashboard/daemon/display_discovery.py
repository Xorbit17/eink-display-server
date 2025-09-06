import django.conf
import asyncio
import json
import socket
from dashboard.services.app_settings import settings

PUBLIC_BASE_URL = getattr(django.conf.settings, "PUBLIC_BASE_URL", "http://localhost:8000")


async def udp_discovery_server_task():
    """
    Tiny UDP broadcast responder: replies with bootstrap URL.
    """
    reply = {
        "bootstrap": f"{PUBLIC_BASE_URL}/api/displays/bootstrap/",
    }

    loop = asyncio.get_running_loop()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.bind(("", settings().discovery_port))
        sock.setblocking(False)
        while True:
            data, addr = await loop.sock_recvfrom(sock, 4096)
            if data.strip() == b"EINK_DISCOVER":
                await loop.sock_sendto(sock, json.dumps(reply).encode("utf-8"), addr)
    finally:
        sock.close()
