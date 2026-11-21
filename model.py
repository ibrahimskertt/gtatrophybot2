import math
from datetime import datetime, timezone

RELEASE = datetime(2026, 11, 19, tzinfo=timezone.utc)
Z = [-1.644854, -0.674490, 0.0, 0.674490, 1.644854]
PRIOR = {'platinum': 0.55, 'gold': 0.75, 'silver': 0.90, 'bronze': 1.00}

def clamp(v, lo, hi):
    return lo if v < lo else hi if v > hi else v

def logit(rate):
    r = clamp(rate, 0.01, 99.99)
    p = r / 100.0
    return math.log(p / (1 - p))

def inv_logit(l):
    return 100.0 / (1.0 + math.exp(-l))

def hours(ts):
    iso = ts.replace('Z', '+00:00')
    dt = datetime.fromisoformat(iso)
    return (dt - RELEASE).total_seconds() / 3600.0

def wls(u, y, w):
    sw = sum(w)
    if sw == 0:
        return 0.0, 0.0
    um = sum(wi * ui for wi, ui in zip(w, u)) / sw
    ym = sum(wi * yi for wi, yi in zip(w, y)) / sw
    num = sum(wi * (ui - um) * (yi - ym) for wi, ui, yi in zip(w, u, y))
    den = sum(wi * (ui - um) ** 2 for wi, ui in zip(w, u))
    slope = 0.0 if den == 0 else num / den
    rms = math.sqrt(sum(wi * (yi - (ym + slope * (ui - um))) ** 2 for wi, ui, yi in zip(w, u, y)) / sw)
    return slope, rms

def forecast(points, tier, x_t, horizon_days):
    xs, rates = zip(*points)
    r_last, x_last = rates[-1], xs[-1]
    if len(points) < 3 or all(r == rates[0] for r in rates):
        b = PRIOR[tier]
        s_fit = 0.30
    else:
        u = [math.log(1 + x) for x in xs]
        y = [logit(r) for r in rates]
        w = [1 + x / x_last if x_last > 0 else 1.0 for x in xs]
        slope, rms = wls(u, y, w)
        s_fit = max(rms, 0.30)
        b = 0.65 * slope + 0.35 * PRIOR[tier]
    g = b * (math.log(1 + x_t) - math.log(1 + x_last))
    damp = 1.0 / (1.0 + math.exp((r_last - 50) / 12.0))
    med = logit(r_last) + g * (0.35 + 0.65 * damp)
    rate = inv_logit(med)
    if r_last < 20:
        rate = min(rate, min(99.5, max(r_last * 8, r_last + 12)))
    rate = clamp(rate, max(0.01, r_last * 0.25), 99.99)
    med = logit(rate)
    s = math.sqrt((0.5 * math.sqrt(horizon_days)) ** 2 + (0.6 * s_fit) ** 2 + 0.22 ** 2)
    qs = [round(clamp(inv_logit(med + z * s), 0.01, 99.99), 4) for z in Z]
    for i in range(1, len(qs)):
        if qs[i] < qs[i - 1]:
            qs[i] = qs[i - 1]
    return qs
