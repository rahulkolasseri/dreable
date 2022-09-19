import os
import threading

from modules.paths import script_path

#import signal

from modules.shared import opts, cmd_opts, state
import modules.shared as shared
from modules.shared import mem_mon, sd_model
#import modules.ui
import modules.scripts
import modules.sd_hijack
#import modules.codeformer_model
#import modules.gfpgan_model
#import modules.face_restoration
#import modules.realesrgan_model as realesrgan
#import modules.esrgan_model as esrgan
#import modules.extras
import modules.lowvram
import modules.txt2img
#import modules.img2img
import modules.sd_models

def wrap_queued_call(func):
    def f(*args, **kwargs):
        with threading.Lock():
            res = func(*args, **kwargs)

        return res

    return f

modules.scripts.load_scripts(os.path.join(script_path, "scripts"))

shared.sd_model = modules.sd_models.load_model()
shared.opts.onchange("sd_model_checkpoint", wrap_queued_call(lambda: modules.sd_models.reload_model_weights(shared.sd_model)))

def text2image(prompt, batch_size=4, steps=25, w=320, h=320, cfg=7.0, seed=-1, sampler=2):
    mem_mon.monitor()
    images, js, info = modules.txt2img.txt2img(prompt, "", "", "", steps, sampler, False, False, 1, batch_size, cfg, seed, -1, 0.0, 0, 0, w, h, False, False, 0.0, 0)
    mem_stats = {k: -(v//-(1024*1024)) for k, v in mem_mon.stop().items()}
    active_peak = mem_stats['active_peak']
    reserved_peak = mem_stats['reserved_peak']
    sys_peak = mem_stats['system_peak']
    sys_total = mem_stats['total']
    sys_pct = round(sys_peak/max(sys_total, 1) * 100, 2)
    vram_info = f"Torch active/reserved: {active_peak}/{reserved_peak} MiB, Sys VRAM: {sys_peak}/{sys_total} MiB ({sys_pct}%)"
    #print(info)
    return images, vram_info