#!/usr/bin/env python3

import asyncio
import argparse
import inspect
import os
import time
import yaml

from nio import AsyncClient
from nio.responses import RoomCreateResponse, JoinedRoomsResponse
from nio.event_builders.state_events import EnableEncryptionBuilder

# Directory containing this file
this_dir = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0]))

# relative path
def rp(path):
    return os.path.join(this_dir, path)

#work_dir = rp(".data")
#if not os.path.exists(work_dir):
#    os.makedirs(work_dir)


with open(rp('config.yaml')) as fin:
    config = yaml.full_load(fin)

parser = argparse.ArgumentParser(description="Stress test matrix clients. Do not run as normal user!")
#parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
parser.add_argument("-c", "--create", type=int, nargs=1, metavar="number", default=[0], help="Number of new rooms to create")
parser.add_argument("-m", "--message", type=int, nargs=1, metavar="number", default=[0], help="Number of messages to send in the rooms")
args = parser.parse_args()

sleep_delay=0.1

HANDLED_ROOM_NAME_PREFIX = "room-spam-"

ENCRYPTION_DICT = EnableEncryptionBuilder().as_dict()
ROOM_CREATION_DICTS = [ENCRYPTION_DICT]


this_run_id = str(int(time.time()))

def is_handled_room_id(client, room_id):
    try:
        name = client.rooms[room_id].named_room_name()
        return name != None and name.startswith(HANDLED_ROOM_NAME_PREFIX)
    except KeyError:
        return False

async def main():
    client = AsyncClient(config["homeserver"], config["mx_id"], config["device_id"])
    try:
        client.user_id = config["mx_id"]
        client.device_id = config["device_id"]
        client.access_token = config["token"]
        print("Sync...")
        await client.sync()

        # Create new rooms
        create_count = min(args.create[0], 50)
        if create_count:
            base_room_name = f"{HANDLED_ROOM_NAME_PREFIX}{this_run_id}"
            print(f"Create {create_count} new rooms...")
            for i in range(create_count):
                room_name = f"{base_room_name}-{(i+1)}"
                room_response = await client.room_create(name=room_name, initial_state=ROOM_CREATION_DICTS)
                assert isinstance(room_response, RoomCreateResponse)
                print(f"Created {room_response.room_id}")
                await asyncio.sleep(sleep_delay)
            print("Sync...")
            await client.sync()

        # Find all rooms which we want to spam
        joined_rooms = await client.joined_rooms()
        assert isinstance(joined_rooms, JoinedRoomsResponse)
        handled_rooms = sorted(filter(lambda room_id: is_handled_room_id(client, room_id), joined_rooms.rooms))
        print(f"Handled rooms: {len(handled_rooms)}/{len(joined_rooms.rooms)}")
        assert len(handled_rooms) > 0

        # Enable encryption in all rooms:
        if False: # TODO arg or something, or just don't forget it in the first place
            for room_id in joined_rooms.rooms:
                room = client.rooms[room_id]
                if not room.encrypted:
                    print(f"Enable encryption in {room_id}")
                    # TODO not working? But I'm doing like https://matrix-nio.readthedocs.io/en/latest/nio.html?highlight=state#module-nio.event_builders.state_events ?
                    await client.room_send(
                        room_id      = room_id,
                        message_type = ENCRYPTION_DICT["type"],
                        content      = ENCRYPTION_DICT["content"],
                    )

        # Write messages to rooms
        message_count = min(args.message[0], 200)
        for i in range(message_count):
            msg = f"spam-{this_run_id} {(i+1)}"
            room = handled_rooms[i % len(handled_rooms)]
            content = {
                "msgtype": "m.text",
                #"format": "org.matrix.custom.html",
                "body": msg,
                #"formatted_body": formatted_msg
            }
            print(f"Message {room}")
            await client.room_send(room, "m.room.message", content, ignore_unverified_devices=True)
            await asyncio.sleep(sleep_delay)
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.new_event_loop().run_until_complete(main())
