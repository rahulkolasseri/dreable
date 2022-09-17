import os
import threading

from modules.paths import script_path

import torch
from omegaconf import OmegaConf

import signal

from ldm.util import instantiate_from_config

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


modules.codeformer_model.setup_codeformer()
modules.gfpgan_model.setup_gfpgan()
shared.face_restorers.append(modules.face_restoration.FaceRestoration())

esrgan.load_models(cmd_opts.esrgan_models_path)
realesrgan.setup_realesrgan()


def load_model_from_config(config, ckpt, verbose=False):
    print(f"Loading model [{shared.sd_model_hash}] from {ckpt}")
    pl_sd = torch.load(ckpt, map_location="cpu")
    if "global_step" in pl_sd:
        print(f"Global Step: {pl_sd['global_step']}")
    sd = pl_sd["state_dict"]

    model = instantiate_from_config(config.model)
    m, u = model.load_state_dict(sd, strict=False)
    if len(m) > 0 and verbose:
        print("missing keys:")
        print(m)
    if len(u) > 0 and verbose:
        print("unexpected keys:")
        print(u)
    if cmd_opts.opt_channelslast:
        model = model.to(memory_format=torch.channels_last)
    model.eval()
    return model

# 
# skipped stuff
# 


modules.scripts.load_scripts(os.path.join(script_path, "scripts"))

try:
    # this silences the annoying "Some weights of the model checkpoint were not used when initializing..." message at start.

    from transformers import logging

    logging.set_verbosity_error()
except Exception:
    pass

with open(cmd_opts.ckpt, "rb") as file:
    import hashlib
    m = hashlib.sha256()

    file.seek(0x100000)
    m.update(file.read(0x10000))
    shared.sd_model_hash = m.hexdigest()[0:8]

sd_config = OmegaConf.load(cmd_opts.config)
shared.sd_model = load_model_from_config(sd_config, cmd_opts.ckpt)
shared.sd_model = (shared.sd_model if cmd_opts.no_half else shared.sd_model.half())

if cmd_opts.lowvram or cmd_opts.medvram:
    modules.lowvram.setup_for_low_vram(shared.sd_model, cmd_opts.medvram)
else:
    shared.sd_model = shared.sd_model.to(shared.device)

modules.sd_hijack.model_hijack.hijack(shared.sd_model)

# 
#skipped stuff 
#

def text2image(prompt) -> None:
    with threading.Lock():
        images, js, info = modules.txt2img.txt2img(prompt, "", "", "", 20, 0, False, False, 1, 2, 7.0, -1, -1, 0.0, 0.0, 0.0, 512, 512, 0)
    return images