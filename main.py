import os, json, base64, requests
from PIL import Image
import gamesense

def resizeImage(path, w=128, h=40):
    im = Image.open(path).convert("1")
    im = im.resize((w, h))

    pixels = im.getdata()
    out = bytearray((w*h+7) // 8)
    for i, p in enumerate(pixels):
        if p > 0:
            byte_i = i//8
            bit = 7 - (i % 8)
            out[byte_i] |= (1 << bit)
            return bytes(out)

GAME_ID = "DOOMKeyboard"
EVENT = "OLED_FRAME"
DISPLAY = "screened-128x40"

gs = gamesense.GameSense(GAME_ID, "OLED_DISPLAY")

gs.register_game(icon_color_id=gamesense.GS_ICON_RED)
gs.register_event(EVENT)

coreProps = os.path.join(os.getenv("PROGRAMDATA"), "SteelSeries", "GG", "coreProps.json")
address = json.load(open(coreProps, "r", encoding="utf-8"))["address"]

bitVec = resizeImage("image.bmp")
bind_url = f"http://{address}/bind_game_event"
bind_payload = {
    "game": GAME_ID,
    "event": EVENT,
    "handlers": [{
        "device_type": DISPLAY,
        "zone": 1,
        "mode": "screen",
        "datas": [{
            "has-text": False,
            "image-data": {
                "format": "bitvector",
                "width": 128,
                "height": 40,
                "data": base64.b64encode(bitVec).decode("ascii")
            }
        }]
    }]
}

requests.post(bind_url, json=bind_payload).raise_for_status()
        
bitVec = resizeImage("image.bmp")
imagePayload = {
    "image-data": {
        "format": "bitvector",
        "width": 128,
        "height": 40,
        "data": base64.b64encode(bitVec).decode("ascii")
    }
}
gs.send_event(EVENT, {
    "value": 1,
    "frame": {
        "image": imagePayload
    }
})