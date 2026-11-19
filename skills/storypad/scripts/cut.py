"""The first cut: each shot's approved take at its length, joined by its transitions, with every
layer that has a file laid over its span, rendered by ffmpeg.

A dissolve or fade is centred on the cut, as the strip draws it: the shot before runs half of it
past the cut and the shot after starts half of it before. A plain cut is a one-frame crossfade,
so every join goes through one filter. A shot with no approved take is black and a layer with no
file is left out; each is named. A layer with no file but a text (a title's words, --meta text=) is
drawn with ffmpeg's drawtext, or, where this ffmpeg has none, laid as a plain card that ffmpeg's
tty reader draws in its own font.
"""

import json
import re
import shutil
import subprocess
import tempfile
import textwrap
from pathlib import Path

import timeline
from storyfile import TimelineError

FPS = 30
FRAME = 1 / FPS
AUDIO = {'.mp3', '.wav', '.m4a', '.aac', '.flac', '.ogg', '.aif', '.aiff'}
STILL = {'.png', '.jpg', '.jpeg', '.webp', '.bmp', '.tif', '.tiff'}


def frame_size(text):
    """`1920x1080` → (1920, 1080); both even, as the encoder's yuv420p frames need."""
    m = re.match(r'^\s*(\d+)\s*x\s*(\d+)\s*$', text or '', re.IGNORECASE)
    w, h = (int(m.group(1)), int(m.group(2))) if m else (0, 0)
    if not w or not h or w % 2 or h % 2:
        raise TimelineError(f'not a size: {text!r}; give an even width and height, as in 1920x1080')
    return w, h


def probe(path):
    """A media file's length in seconds, or None when ffprobe can't tell."""
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'json', str(path)],
                       capture_output=True, text=True)
    try:
        return float(json.loads(r.stdout)['format']['duration'])
    except (KeyError, ValueError, TypeError):
        return None


def has_sound(path):
    r = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'a', '-show_entries', 'stream=index',
                        '-of', 'csv=p=0', str(path)], capture_output=True, text=True)
    return bool(r.stdout.strip())


def draws_text():
    """Whether this ffmpeg has the drawtext filter."""
    r = subprocess.run(['ffmpeg', '-hide_banner', '-filters'], capture_output=True, text=True)
    return 'drawtext' in r.stdout.split()


def text_card(text, w, h, path):
    """A still the frame's size at `path`: `text` in white on a black card, centred, drawn by ffmpeg's
    tty reader in its built-in 8x16 font, so no font library is needed."""
    lines = textwrap.wrap(text, max(1, w // 8 - 1)) or [text]
    cols = max(map(len, lines))
    path.with_suffix('.txt').write_bytes(
        b'\x1b[1;37m' + '\r\n'.join(line.center(cols).rstrip() for line in lines).encode('cp437', 'replace'))
    k = max(1, min(w * 9 // 10 // ((cols + 1) * 8), h // 2 // (len(lines) * 16)))
    r = subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'tty', '-video_size', f'{(cols + 1) * 8}x{len(lines) * 16}',
                        '-i', str(path.with_suffix('.txt')), '-frames:v', '1', '-vf',
                        f'format=rgba,scale=iw*{k}:ih*{k}:flags=neighbor,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:color=black@0',
                        str(path)], capture_output=True, text=True)
    if r.returncode:
        raise TimelineError('ffmpeg could not draw a text card: ' + ' '.join(r.stderr.strip().splitlines()[-2:]))
    return path


def draw_text(last, label, text, a, b, fi, fo, w, h, path):
    """The drawtext filter laying `text` over [last] from a to b, faded in and out."""
    path.write_text('\n'.join(textwrap.wrap(text, max(1, 20 * w // h)) or [text]), encoding='utf-8')
    alpha = f"min(min(1,{f'(t-{a:.3f})/{fi:.3f}' if fi else '1'}),{f'({b:.3f}-t)/{fo:.3f}' if fo else '1'})"
    return (f"[{last}]drawtext=textfile='{path}':fontcolor=white:fontsize=h/12:box=1:boxcolor=black@0.6:"
            f"boxborderw=h/60:line_spacing=h/60:x=(w-text_w)/2:y=(h-text_h)/2:alpha='{alpha}':"
            f"enable='between(t,{a:.3f},{b:.3f})'[{label}]")


def overlap(end):
    kind, secs = end
    return secs if kind in ('dissolve', 'fade') else FRAME


def media(path, dur, start=0):
    """The ffmpeg input options for a file played for `dur` seconds from `start` into it."""
    if path.suffix.lower() in STILL:
        return ['-loop', '1', '-t', f'{dur:.3f}', '-i', str(path)]
    return (['-ss', f'{start:.3f}'] if start else []) + ['-i', str(path)]


def shots_of(story, notes):
    """Each shot in story order with its scene, its approved take's file and where in it the shot
    starts; lengths filled in."""
    out = []
    for s in story['scenes']:
        if not s['shots']:
            notes.append(f"{s['num']} {s['name']}: no shots yet, left out")
            continue
        for x in s['shots']:
            take = timeline.approved(s, x['id'])
            file = timeline.local(story['path'], timeline.resolve(story, take['file'])) if take else None
            if file and not file.exists():
                raise TimelineError(f"{take['id']}: {take['file']} is missing")
            if take is None:
                notes.append(f"{x['id']} {x['name']}: no approved take, black")
            start = (take['in'] or 0) if take else 0
            if file and file.suffix.lower() not in STILL and (start or x['length'] is None):
                full = probe(file)
                if start and full is not None and start >= full:
                    raise TimelineError(f"{take['id']}: starts {timeline.num(start)}s in, past the end of {take['file']}")
                if x['length'] is None and full:
                    x['length'] = full - start
            out.append((s, x, file, start))
        for x, n in zip(s['shots'], timeline.drawn(s['shots'])):
            if x['length'] is None:
                x['length'] = n
                notes.append(f"{x['id']} {x['name']}: no length, cut at {timeline.clock(n)}")
    return out


def layer_runs(scenes):
    """Every layer in story seconds; one carried across scenes is one run. A shot with no length
    yet takes its scene's average."""
    offs = timeline.starts([timeline.scene_length(s) for s in scenes])
    inner = [{**l, 't0': off + l['t0'], 't1': off + l['t1']} for s, off in zip(scenes, offs)
             for l in timeline.scene_layers(s) if l['t0'] is not None and l['t1'] is not None]
    return timeline.crossing(scenes, offs) + inner


def build(story, output, size, scene=None):
    """Render the cut into `output`: the whole story, or only `scene` with the layers carried into
    it from the scenes before; returns the lines that report it."""
    w, h = frame_size(size)
    if not (shutil.which('ffmpeg') and shutil.which('ffprobe')):
        raise TimelineError('making the cut needs ffmpeg and ffprobe installed')
    with tempfile.TemporaryDirectory(prefix='storypad-cut-') as cards:
        return render(story, output, w, h, Path(cards), scene)


def window(story, scene, total):
    """Where the cut sits in story seconds: from the start of `scene` (the story's start when
    None) for `total` seconds, open-ended when nothing with shots follows it."""
    scenes = [s for s in story['scenes'] if s['shots']]
    if scene is None:
        return scenes, 0, float('inf')
    i = next(k for k, s in enumerate(scenes) if s is scene)
    t0 = sum(timeline.scene_length(s) for s in scenes[:i])
    return scenes, t0, t0 + total if i < len(scenes) - 1 else float('inf')


def render(story, output, w, h, cards, scene=None):
    """build's work; the text cards and text files it makes go in `cards`."""
    notes = []
    shots = shots_of({**story, 'scenes': [scene]} if scene else story, notes)
    if not shots:
        raise TimelineError('no scene has shots yet')
    total = sum(x['length'] for _, x, _, _ in shots)
    scenes, t0, t1 = window(story, scene, total)
    inputs, graph = [], []
    frame = (f'scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2,'
             f'setsar=1,fps={FPS},format=yuv420p')

    sounds, start = [], 0
    for i, (_, x, file, start_at) in enumerate(shots):
        head = overlap(shots[i - 1][1]['ends']) / 2 if i else 0
        tail = overlap(x['ends']) / 2 if i < len(shots) - 1 else 0
        dur = x['length'] + head + tail
        inputs += media(file, dur, max(0, start_at - head)) if file else \
            ['-f', 'lavfi', '-t', f'{dur:.3f}', '-i', f'color=c=black:s={w}x{h}:r={FPS}']
        graph.append(f'[{i}:v]{frame},tpad=stop_mode=clone:stop_duration={dur:.3f},'
                     f'trim=duration={dur:.3f},setpts=PTS-STARTPTS[v{i}]')
        if file and has_sound(file):
            ms = round((start - head) * 1000)
            graph.append(f'[{i}:a]atrim=0:{dur:.3f},asetpts=PTS-STARTPTS'
                         + (f',afade=t=in:st=0:d={head * 2:.3f}' if head > FRAME else '')
                         + (f',afade=t=out:st={dur - tail * 2:.3f}:d={tail * 2:.3f}' if tail > FRAME else '')
                         + f',adelay={ms}|{ms}[s{i}]')
            sounds.append(f'[s{i}]')
        start += x['length']
    last, t = 'v0', 0
    for i in range(len(shots) - 1):
        x = shots[i][1]
        t += x['length']
        d = overlap(x['ends'])
        graph.append(f"[{last}][v{i + 1}]xfade=transition={'fadeblack' if x['ends'][0] == 'fade' else 'fade'}:"
                     f'duration={d:.3f}:offset={t - d / 2:.3f}[x{i}]')
        last = f'x{i}'
    kind, secs = shots[-1][1]['ends']
    if kind == 'fade':
        graph.append(f'[{last}]fade=t=out:st={total - secs:.3f}:d={secs:.3f}[end]')
        last = 'end'

    laid, drawtext = 0, None
    for whole in layer_runs(scenes):
        run = timeline.clip({**whole, 't0': whole['t0'] or 0}, t0, t1)
        if run is None:
            continue
        a = run['t0'] or 0
        b = total if run['t1'] is None else min(run['t1'], total)
        fi = whole['in'][1] if run['t0'] is not None else 0
        fo = whole['out'][1] if run['t1'] is not None or t1 == float('inf') else 0
        seek = 0 if run['t0'] is not None else t0 - (whole['t0'] or 0)
        k = inputs.count('-i')
        text = timeline.layer_text(run)
        if not run.get('file') and not text:
            notes.append(f"layer {run['name']}: no file, left out")
            continue
        laid += 1
        if not run.get('file'):
            drawtext = draws_text() if drawtext is None else drawtext
            if drawtext:
                graph.append(draw_text(last, f't{laid}', text, a, b, fi, fo, w, h, cards / f'{laid}.txt'))
                last = f't{laid}'
                notes.append(f"layer {run['name']}: no file, its text drawn")
                continue
            path = text_card(text, w, h, cards / f'{laid}.png')
            notes.append(f"layer {run['name']}: no file, its text shown on a plain card (this ffmpeg has no drawtext)")
        else:
            path = timeline.local(story['path'], timeline.resolve(story, run['file']))
        if not path.exists():
            raise TimelineError(f"layer {run['name']}: {run['file']} is missing")
        if path.suffix.lower() in AUDIO:
            inputs += media(path, b - a, seek)
            ms = round(a * 1000)
            graph.append(f'[{k}:a]atrim=0:{b - a:.3f},asetpts=PTS-STARTPTS'
                         + (f',afade=t=in:st=0:d={fi:.3f}' if fi else '')
                         + (f',afade=t=out:st={b - a - fo:.3f}:d={fo:.3f}' if fo else '')
                         + f',adelay={ms}|{ms}[a{k}]')
            sounds.append(f'[a{k}]')
        else:
            inputs += media(path, b - a, seek)
            graph.append(f'[{k}:v]scale={w}:{h}:force_original_aspect_ratio=decrease,format=rgba'
                         + (f',fade=t=in:st=0:d={fi:.3f}:alpha=1' if fi else '')
                         + (f',fade=t=out:st={b - a - fo:.3f}:d={fo:.3f}:alpha=1' if fo else '')
                         + f',setpts=PTS-STARTPTS+{a:.3f}/TB[o{k}]')
            graph.append(f"[{last}][o{k}]overlay=(W-w)/2:(H-h)/2:eof_action=pass:"
                         f"enable='between(t,{a:.3f},{b:.3f})'[y{k}]")
            last = f'y{k}'
    maps = ['-map', f'[{last}]']
    if sounds:
        graph.append(f"{''.join(sounds)}amix=inputs={len(sounds)}:normalize=0:duration=longest[aout]")
        maps += ['-map', '[aout]', '-c:a', 'aac']
    cmd = ['ffmpeg', '-v', 'error', '-y', *inputs, '-filter_complex', ';'.join(graph), *maps,
           '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-t', f'{total:.3f}', str(output)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        raise TimelineError('ffmpeg failed: ' + ' '.join(r.stderr.strip().splitlines()[-3:]))
    made = sum(1 for _, _, f, _ in shots if f)
    return [f'  {timeline.clock(total)}  ·  {made}/{len(shots)} shots from approved takes  ·  {laid} layers laid'] \
        + [f'  {n}' for n in notes]
