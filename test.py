"""Script to run blinkpy as an blinkapp."""
from os import environ
import asyncio
import logging
from datetime import datetime, timedelta
from aiohttp import ClientSession
from blinkpy.blinkpy import Blink
from blinkpy.auth import Auth
from blinkpy.helpers.util import json_load, json_dumps

CREDFILE = "config.json"
TIMEDELTA = timedelta(environ.get("TIMEDELTA", 1))
_LOGGER = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',
                    filename='blinkpy.log',
                    level=logging.DEBUG)
_LOGGER.setLevel(logging.DEBUG)


def get_date():
    """Return now - timedelta for blinkpy."""
    return (datetime.now() - TIMEDELTA).isoformat()


async def download_videos(blink, save_dir="."):
    """Make request to download videos."""
    await blink.download_videos(save_dir, since=get_date())

def get_camera_info(blink):
    for name, camera in blink.cameras.items():
        print(name)                             # Name of the camera
        print(json_dumps(camera.attributes))    # Print available attributes of camera

async def arm_blink(blink,
                    set_sync=False,
                    arm_sync=True,
                    set_camera=False,
                    arm_cameras=True):

    await blink.refresh()

    # Arm a sync module
    for name, sync in blink.sync.items():
        print(name)                         # Name of the camera
        print(json_dumps(sync.attributes))  # Print available attributes of camera

        # Arm/Disarm a sync module
        if set_sync:
            await blink.sync[name].async_arm(arm_sync)

            # Print arm status of a sync module - a system refresh should be performed first
            await blink.refresh()
        sync = blink.sync[name]
        print(f"{sync.name} status: {sync.arm}")

    for name in blink.cameras.keys():
        print(name)                             # Name of the camera
        camera = blink.cameras[name]

        # Enable/Disable motion detection on a camera
        if set_camera:
            await camera.async_arm(arm_cameras)

            # Print arm status of a sync module - a system refresh should be performed first
            await blink.refresh()
        print(f"{camera.name} status: {camera.arm}")

async def start(session: ClientSession):
    """Startup blink app."""
    blink = Blink(session=session)
    blink.auth = Auth(await json_load(CREDFILE), session=session)
    await blink.start()
    return blink


async def main():
    """Run the blink app."""
    session = ClientSession()
    blink = await start(session)
#    await download_videos(blink)
    get_camera_info(blink=blink)
    await arm_blink(blink=blink)
    await blink.save(CREDFILE)
    await session.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

