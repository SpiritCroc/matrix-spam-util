#!/usr/bin/env python3

import asyncio
import getpass

from nio import AsyncClient, AsyncClientConfig

homeserver = input("Homeserver: ")
mxid = input("mxid: ")
device = input("Device name: ")
passwd = getpass.getpass("Password: ")

if not homeserver.startswith("http"):
    homeserver = f"https://{homeserver}"

client_config = AsyncClientConfig(
    max_limit_exceeded=0,
    max_timeouts=0,
    store_sync_tokens=False,
    encryption_enabled=True,
)
client = AsyncClient(homeserver, mxid, config=client_config)
try:
    resp = asyncio.get_event_loop().run_until_complete(client.login(password = passwd, device_name = device))
    print(f"Token: {resp.access_token}")
finally:
    asyncio.get_event_loop().run_until_complete(client.close())
