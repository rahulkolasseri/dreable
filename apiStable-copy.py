import os
import threading

from modules.paths import script_path

#import signal

from modules.shared import opts, cmd_opts, state
import modules.shared as shared
#import modules.ui
import modules.scripts
import modules.sd_hijack
#import modules.codeformer_model
#import modules.gfpgan_model
#import modules.face_restoration
#import modules.realesrgan_model as realesrgan
#import modules.esrgan_model as esrgan
#import modules.extras
#import modules.lowvram
import modules.txt2img
#import modules.img2img
import modules.sd_models

modules.scripts.load_scripts(os.path.join(script_path, "scripts"))

shared.sd_model = modules.sd_models.load_model()

def text2image(prompt, w=320, h=320, steps=20, batch_size=4, cfg=7.0, seed=-1, sampler=0) -> None:
    with threading.Lock():
        images, js, info = modules.txt2img.txt2img(prompt, "", "", "", steps, sampler, False, False, 1, batch_size, cfg, seed, -1, 0.0, 0, 0, w, h, 0)
    #print(info)
    return images