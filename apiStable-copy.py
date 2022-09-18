import os
import threading

from modules.paths import script_path

import signal

from modules.shared import opts, cmd_opts, state
import modules.shared as shared
import modules.ui
import modules.scripts
import modules.sd_hijack
import modules.codeformer_model
import modules.gfpgan_model
import modules.face_restoration
import modules.realesrgan_model as realesrgan
import modules.esrgan_model as esrgan
import modules.extras
import modules.lowvram
import modules.txt2img
import modules.img2img
import modules.sd_models

modules.scripts.load_scripts(os.path.join(script_path, "scripts"))

shared.sd_model = modules.sd_models.load_model()

def text2image(prompt, w=512, h=512) -> None:
    with threading.Lock():
        images, js, info = modules.txt2img.txt2img(prompt, "", "", "", 20, 0, False, False, 1, 2, 7.0, -1, -1, 0.0, 0.0, 0.0, w, h, 0)
    return images