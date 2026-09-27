# Synthesises an original, royalty-free backing track timed to the video's scene cuts.
# Usage: python3 music.py soundtrack.wav
import sys, wave
import numpy as np

SR = 48000
DUR = 76.0
BPM = 112
BEAT = 60 / BPM
N = int(SR * DUR)
t = np.arange(N) / SR
L = np.zeros(N); R = np.zeros(N)
rng = np.random.default_rng(7)

CUTS = [5.2, 10.6, 15.8, 27.2, 33.6, 39.4, 45.2, 51.4, 57.2, 63.4, 69.4]
BRAND = 10.6

def midi(n): return 440 * 2 ** ((n - 69) / 12)

def onepole(x, a):
    y = np.empty_like(x); acc = 0.0
    for i in range(len(x)):
        acc += a * (x[i] - acc); y[i] = acc
    return y

def add(buf, start, sig, gain=1.0):
    i = int(start * SR)
    if i >= N: return
    j = min(N, i + len(sig))
    buf[i:j] += sig[:j - i] * gain

def env_adsr(n, a, d, s, r, sr=SR):
    e = np.ones(n) * s
    na, nd, nr = int(a * sr), int(d * sr), int(r * sr)
    e[:na] = np.linspace(0, 1, na)
    e[na:na + nd] = np.linspace(1, s, nd)
    e[-nr:] *= np.linspace(1, 0, nr)
    return e

# chord progression: Cmaj9 - Am9 - Fmaj9 - G6/9 (bright, optimistic)
CHORDS = [[48, 55, 59, 62, 64], [45, 52, 55, 59, 60], [41, 48, 52, 55, 57], [43, 50, 55, 57, 59]]
BAR = BEAT * 4

# ---- pad ----
bar_i = 0; pos = 0.0
while pos < DUR:
    ch = CHORDS[bar_i % 4]
    n = int(BAR * SR * 1.15)
    tt = np.arange(n) / SR
    sig = np.zeros(n)
    for k, note in enumerate(ch):
        f = midi(note + 12)
        for det in (-0.12, 0.12):
            ph = 2 * np.pi * f * (1 + det / 100) * tt + k
            sig += (np.sin(ph) + 0.25 * np.sin(2 * ph) + 0.1 * np.sin(3 * ph))
    sig *= env_adsr(n, 0.6, 0.5, 0.8, 0.9) / 10
    lvl = 0.16 if pos < 5.2 else 0.12
    add(L, pos, sig, lvl); add(R, pos + 0.012, sig, lvl)
    # sub bass
    bn = int(BAR * SR)
    bt = np.arange(bn) / SR
    bass = np.sin(2 * np.pi * midi(ch[0] - 12) * bt) * env_adsr(bn, 0.02, 0.3, 0.7, 0.15)
    if pos >= BRAND - 0.01:
        add(L, pos, bass, 0.22); add(R, pos, bass, 0.22)
    bar_i += 1; pos += BAR

# ---- pluck arpeggio (from the brand reveal) ----
def pluck(f, n=int(0.45 * SR)):
    tt = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * tt) + 0.35 * np.sin(4 * np.pi * f * tt) * np.exp(-tt * 18)
    return s * np.exp(-tt * 7) * np.minimum(1, tt * 400)

step = BEAT / 2; k = 0; pos = 5.2
pattern = [0, 2, 4, 3, 1, 3, 4, 2]
while pos < DUR - 2.5:
    bar = int((pos) / BAR) % 4
    ch = CHORDS[bar]
    note = ch[1:][pattern[k % 8] % 4] + 24
    g = 0.05 if pos < BRAND else 0.075
    p = pluck(midi(note))
    pan = 0.5 + 0.3 * np.sin(k * 0.7)
    add(L, pos, p, g * (1 - pan) * 2); add(R, pos, p, g * pan * 2)
    k += 1; pos += step

# ---- drums ----
def kick():
    n = int(0.35 * SR); tt = np.arange(n) / SR
    f = 50 + 90 * np.exp(-tt * 30)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-tt * 9)

def hat():
    n = int(0.06 * SR); tt = np.arange(n) / SR
    nz = rng.standard_normal(n)
    nz = nz - onepole(nz, 0.5)
    return nz * np.exp(-tt * 70)

def clap():
    n = int(0.25 * SR); tt = np.arange(n) / SR
    nz = rng.standard_normal(n)
    nz = onepole(nz, 0.35) - onepole(nz, 0.05)
    e = np.exp(-tt * 22) + 0.6 * np.exp(-np.maximum(0, tt - 0.012) * 22) * (tt > 0.012)
    return nz * e

K, H, C = kick(), hat(), clap()
beat_t = BRAND
while beat_t < DUR - 3.0:
    bi = round((beat_t - BRAND) / BEAT)
    add(L, beat_t, K, 0.55); add(R, beat_t, K, 0.55)
    if bi % 2 == 1:
        add(L, beat_t, C, 0.10); add(R, beat_t, C, 0.12)
    add(L, beat_t + BEAT / 2, H, 0.09); add(R, beat_t + BEAT / 2, H, 0.11)
    beat_t += BEAT
# tension hats during "sound familiar?"
ht = 5.2
while ht < BRAND - 0.4:
    add(L, ht, H, 0.05 + 0.08 * (ht - 5.2) / 5); add(R, ht, H, 0.05 + 0.08 * (ht - 5.2) / 5)
    ht += BEAT / 2

# ---- transitions: whoosh into each cut, riser + impact at brand reveal ----
def whoosh(length=0.7):
    n = int(length * SR); tt = np.arange(n) / SR
    nz = rng.standard_normal(n)
    sweep = np.linspace(0.02, 0.4, n)
    y = np.empty(n); acc = 0.0
    for i in range(n):
        acc += sweep[i] * (nz[i] - acc); y[i] = acc
    return y * np.sin(np.pi * tt / length) ** 2

for c in CUTS:
    w = whoosh(0.7)
    add(L, c - 0.5, w, 0.16); add(R, c - 0.45, w, 0.16)

riser_n = int(2.2 * SR); rt = np.arange(riser_n) / SR
riser = np.sin(2 * np.pi * np.cumsum(200 + 900 * (rt / 2.2) ** 2) / SR) * (rt / 2.2) ** 2
add(L, BRAND - 2.2, riser, 0.05); add(R, BRAND - 2.2, riser, 0.05)
imp_n = int(2.5 * SR); it = np.arange(imp_n) / SR
impact = (np.sin(2 * np.pi * 45 * it) * 0.8 + onepole(rng.standard_normal(imp_n), 0.08) * 0.5) * np.exp(-it * 2.2)
add(L, BRAND, impact, 0.5); add(R, BRAND, impact, 0.5)

# ---- soft chime at the CTA ----
for i, n in enumerate([72, 76, 79, 84]):
    p = pluck(midi(n), int(1.6 * SR))
    add(L, 69.6 + i * 0.09, p, 0.09); add(R, 69.6 + i * 0.09, p, 0.09)

# ---- master: gentle bus compression-ish, fade in/out, normalise ----
mix = np.stack([L, R], 1)
fade = np.ones(N)
fi = int(0.8 * SR); fade[:fi] = np.linspace(0, 1, fi)
fo = int(3.5 * SR); fade[-fo:] = np.linspace(1, 0, fo) ** 1.5
mix *= fade[:, None]
mix = np.tanh(mix * 1.6) / 1.6
mix /= np.max(np.abs(mix)) + 1e-9
mix *= 0.89
out = sys.argv[1] if len(sys.argv) > 1 else 'soundtrack.wav'
with wave.open(out, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype('<i2').tobytes())
print('wrote', out)
