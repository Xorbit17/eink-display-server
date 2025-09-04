
from django.conf import settings
import asyncio, json, socket, time

DISCOVERY_PORT = getattr(settings, "DISCOVERY_PORT", 51234)
PUBLIC_BASE_URL = getattr(settings, "PUBLIC_BASE_URL", "http://localhost:8000")

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
        sock.bind(("", DISCOVERY_PORT))
        sock.setblocking(False)
        while True:
            data, addr = await loop.sock_recvfrom(sock, 4096)
            if data.strip() == b"EINK_DISCOVER":
                await loop.sock_sendto(
                    sock, json.dumps(reply).encode("utf-8"), addr
                )
    finally:
        sock.close()