"""The condition network: attention layers over the sensor history,
conditioned by the known condition and the degree of engagement, trained
offline on encrypted weights (claims 22 and 26, as they read on JIM).

`continuity.py` carries the state that survives between sessions and renders
it as attention weighting in the coach's prompt. `finetune.py` trains a small
logistic model from answered follow-ups and is honest that the transformer
stays the vendor's. This module is the part that was still a sentence: an
attention network JIM owns, in numpy, forward and backward written out, run
on every coach turn, every companion check-in and every engaged-session
reply, and trained here from this person's own readings with the network
blocked.

What it reads. The person's last twelve biometric readings are a sequence.
Each one is embedded from plain features — heart rate against their own
baseline, HRV, breathing, oxygen, temperature, stress, activity, whether they
said something, and **how far the reading can be trusted** (`signal.py`'s
grade, carried on every stored sample). A context vector rides every
position: the declared known conditions, hashed into slots, and the
sensitivity dial. Two attention layers read the sequence. Each key's logit is
shifted by that reading's trust (a learned ``gamma`` per layer), so a reading
a wearable took off the wrist cannot draw the coach's attention the way a
clean one can; the softmax temperature is set by the sensitivity dial and by
how engaged the person is right now — a stressed reading sharpens the look,
an assertive dial widens it. The last position is read out through two
heads: where the next reading is expected to sit against baseline, and four
emphases for the reply — reassure, act, escalate, monitor.

What it writes. The attention row over the readings, the temperature and the
emphases go into the prompt as sentences, and into ``condition_conditioning``
as a row per reply — indices, weights, trust and times only. No values, no
note text, no condition name: the same rule `user_continuity` keeps.

How it learns. ``train`` replays the stored readings into (window → next
reading) pairs, labels each by re-running the product's own detector on the
reading that followed, and fits the weights by Adam on hand-written
gradients, inside `finetune._no_egress`. Loss before and after are kept; the
weights are sealed under AES-GCM with a key derived for this install
(``JIM_MODEL_KEY``, else from the database path). It runs from a door, from
`finetune.train`, and on its own every sixteenth reading.
"""

from __future__ import annotations

import hashlib
import json
import os

import numpy as np

from . import db

CONFIG = {"d_in": 10, "d_ctx": 12, "d_model": 16, "heads": 2, "layers": 2,
          "d_ff": 32, "window": 12}
EMPHASES = ("reassure", "act", "escalate", "monitor")
WEIGHTS_VERSION = 1
TRAIN_EVERY = 16          # readings between the passes ingest runs on its own
_LR = 0.01
_ADAM_B1, _ADAM_B2, _ADAM_EPS = 0.9, 0.999, 1e-8
_MAX_SAMPLES = 400
_GRADE_TRUST = {"ok": 1.0, "suspect": 0.45, "implausible": 0.15}
_TAU_BY_SENSITIVITY = {"cautious": 0.7, "balanced": 1.0, "assertive": 1.3}
_CONDITION_SLOTS = 8


# -- features ----------------------------------------------------------------

def _unit(value, lo: float, hi: float, missing: float) -> float:
    if value is None:
        return missing
    try:
        v = float(value)
    except (TypeError, ValueError):
        return missing
    return float(min(1.0, max(0.0, (v - lo) / (hi - lo))))


def trust_of(detail: dict) -> float:
    """How far the stored reading can be believed — the per-reading scalar
    the attention is biased by."""
    if detail.get("signal_confidence") is not None:
        return float(min(1.0, max(0.0, detail["signal_confidence"])))
    return _GRADE_TRUST.get(detail.get("signal_grade"), 1.0)


def features(details: list[dict], resting: float) -> np.ndarray:
    T = len(details)
    rows = np.zeros((T, CONFIG["d_in"]))
    resting = float(resting or 60)
    for i, d in enumerate(details):
        hr = d.get("heart_rate")
        dev = 0.5 if hr is None else min(1.0, max(0.0, 0.5 + (float(hr) - resting) / resting))
        rows[i] = (
            dev,
            _unit(d.get("hrv"), 0, 100, 0.5),
            _unit(d.get("respiratory_rate"), 0, 30, 0.4),
            _unit(d.get("blood_oxygen"), 98, 88, 0.0),          # deficit
            _unit(d.get("stress_level"), 0, 1, 0.0),
            _unit(d.get("activity_level"), 0, 10, 0.0),
            1.0 if (d.get("note") or "").strip() else 0.0,
            trust_of(d),
            (i + 1) / T,
            _unit(d.get("body_temperature"), 34.8, 38.8, 0.5),
        )
    return rows


def context(known: list[str] | None, sensitivity: str | None) -> np.ndarray:
    """The known condition and the dial, as the vector that rides every
    position: eight hashed condition slots, three for the dial, one for
    'any condition declared'."""
    c = np.zeros(CONFIG["d_ctx"])
    for name in known or []:
        slot = int(hashlib.sha256(str(name).lower().encode()).hexdigest(), 16)
        c[slot % _CONDITION_SLOTS] = 1.0
    c[_CONDITION_SLOTS + ("cautious", "balanced", "assertive").index(
        sensitivity if sensitivity in _TAU_BY_SENSITIVITY else "balanced")] = 1.0
    c[_CONDITION_SLOTS + 3] = 1.0 if known else 0.0
    return c


def temperature(sensitivity: str | None, engagement: float) -> float:
    """Softmax temperature: the dial sets the base, the current degree of
    engagement (the latest reading's stress, 0..1) sharpens it."""
    base = _TAU_BY_SENSITIVITY.get(sensitivity or "balanced", 1.0)
    e = min(1.0, max(0.0, float(engagement or 0.0)))
    return round(min(1.6, max(0.4, base - 0.3 * e)), 4)


# -- parameters --------------------------------------------------------------

def _seed(user_id: str) -> int:
    return int.from_bytes(hashlib.sha256(user_id.encode()).digest()[:4], "big")


def init_params(seed: int, config: dict = CONFIG) -> dict:
    rng = np.random.default_rng(seed)
    d, dff, din, dctx, L = (config["d_model"], config["d_ff"], config["d_in"],
                            config["d_ctx"], config["layers"])

    def w(*shape, scale=None):
        scale = scale or 1 / np.sqrt(shape[0])
        return rng.normal(0, scale, shape)

    p = {"W_in": w(din, d), "W_ctx": w(dctx, d, scale=0.2), "b_in": np.zeros(d),
         "P": w(config["window"], d, scale=0.1),
         "w_dev": w(d, 1), "b_dev": np.zeros(1),
         "W_emph": w(d, len(EMPHASES)), "b_emph": np.zeros(len(EMPHASES))}
    for l in range(L):
        p[f"Wq{l}"], p[f"Wk{l}"], p[f"Wv{l}"], p[f"Wo{l}"] = (
            w(d, d), w(d, d), w(d, d), w(d, d))
        p[f"W1{l}"], p[f"b1{l}"] = w(d, dff), np.zeros(dff)
        p[f"W2{l}"], p[f"b2{l}"] = w(dff, d), np.zeros(d)
        p[f"gamma{l}"] = np.array([1.0])     # trust bias on the logits
    return p


def _softmax(z):
    z = z - z.max(axis=-1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(axis=-1, keepdims=True)


def _sigmoid(z):
    return 1 / (1 + np.exp(-z))


# -- forward / backward --------------------------------------------------------

def forward(p: dict, X: np.ndarray, c: np.ndarray, trust: np.ndarray,
            tau: float, config: dict = CONFIG) -> dict:
    T = X.shape[0]
    Hh, d = config["heads"], config["d_model"]
    dk = d // Hh
    cache = {"X": X, "c": c, "trust": trust, "tau": tau, "layers": []}
    H = X @ p["W_in"] + p["b_in"] + p["P"][:T] + (c @ p["W_ctx"])[None, :]
    for l in range(config["layers"]):
        Q, K, V = H @ p[f"Wq{l}"], H @ p[f"Wk{l}"], H @ p[f"Wv{l}"]
        Qh = Q.reshape(T, Hh, dk).transpose(1, 0, 2)
        Kh = K.reshape(T, Hh, dk).transpose(1, 0, 2)
        Vh = V.reshape(T, Hh, dk).transpose(1, 0, 2)
        S_raw = Qh @ Kh.transpose(0, 2, 1) / np.sqrt(dk)
        # The claim, literally: each reading's logit carries its trust, and
        # the row is sharpened or widened by the dial and the current state.
        S = (S_raw + p[f"gamma{l}"][0] * trust[None, None, :]) / tau
        A = _softmax(S)
        Oh = A @ Vh
        Ocat = Oh.transpose(1, 0, 2).reshape(T, d)
        H1 = H + Ocat @ p[f"Wo{l}"]
        G = np.tanh(H1 @ p[f"W1{l}"] + p[f"b1{l}"])
        H2 = H1 + G @ p[f"W2{l}"] + p[f"b2{l}"]
        cache["layers"].append({"H": H, "Qh": Qh, "Kh": Kh, "Vh": Vh, "A": A,
                                "Ocat": Ocat, "H1": H1, "G": G})
        H = H2
    h = H[-1]
    cache.update({"h": h,
                  "y_dev": _sigmoid(h @ p["w_dev"] + p["b_dev"])[0],
                  "y_emph": _sigmoid(h @ p["W_emph"] + p["b_emph"])})
    return cache


def loss_of(cache: dict, t_dev: float, t_emph: np.ndarray) -> float:
    return float((cache["y_dev"] - t_dev) ** 2
                 + np.mean((cache["y_emph"] - t_emph) ** 2))


def backward(p: dict, cache: dict, t_dev: float, t_emph: np.ndarray,
             config: dict = CONFIG) -> dict:
    g = {k: np.zeros_like(v) for k, v in p.items()}
    Hh, d = config["heads"], config["d_model"]
    dk = d // Hh
    T = cache["X"].shape[0]
    trust, tau = cache["trust"], cache["tau"]
    h, y_dev, y_emph = cache["h"], cache["y_dev"], cache["y_emph"]

    dz = 2 * (y_dev - t_dev) * y_dev * (1 - y_dev)
    g["w_dev"] = (h * dz)[:, None]
    g["b_dev"] = np.array([dz])
    dh = p["w_dev"][:, 0] * dz
    dze = 2 * (y_emph - t_emph) / len(EMPHASES) * y_emph * (1 - y_emph)
    g["W_emph"] = np.outer(h, dze)
    g["b_emph"] = dze
    dh = dh + p["W_emph"] @ dze

    dH2 = np.zeros((T, d))
    dH2[-1] = dh
    for l in reversed(range(config["layers"])):
        c = cache["layers"][l]
        dF = dH2
        g[f"W2{l}"] = c["G"].T @ dF
        g[f"b2{l}"] = dF.sum(axis=0)
        dG = dF @ p[f"W2{l}"].T
        dZ1 = dG * (1 - c["G"] ** 2)
        g[f"W1{l}"] = c["H1"].T @ dZ1
        g[f"b1{l}"] = dZ1.sum(axis=0)
        dH1 = dH2 + dZ1 @ p[f"W1{l}"].T

        g[f"Wo{l}"] = c["Ocat"].T @ dH1
        dOcat = dH1 @ p[f"Wo{l}"].T
        dOh = dOcat.reshape(T, Hh, dk).transpose(1, 0, 2)
        A, Vh, Qh, Kh = c["A"], c["Vh"], c["Qh"], c["Kh"]
        dA = dOh @ Vh.transpose(0, 2, 1)
        dVh = A.transpose(0, 2, 1) @ dOh
        dS = A * (dA - (dA * A).sum(axis=-1, keepdims=True))
        g[f"gamma{l}"] = np.array([(dS * trust[None, None, :]).sum() / tau])
        dS_raw = dS / tau
        dQh = dS_raw @ Kh / np.sqrt(dk)
        dKh = dS_raw.transpose(0, 2, 1) @ Qh / np.sqrt(dk)
        dQ = dQh.transpose(1, 0, 2).reshape(T, d)
        dK = dKh.transpose(1, 0, 2).reshape(T, d)
        dV = dVh.transpose(1, 0, 2).reshape(T, d)
        H = c["H"]
        g[f"Wq{l}"], g[f"Wk{l}"], g[f"Wv{l}"] = H.T @ dQ, H.T @ dK, H.T @ dV
        dH2 = (dH1 + dQ @ p[f"Wq{l}"].T + dK @ p[f"Wk{l}"].T
               + dV @ p[f"Wv{l}"].T)

    dE = dH2
    g["W_in"] = cache["X"].T @ dE
    g["W_ctx"] = np.outer(cache["c"], dE.sum(axis=0))
    g["b_in"] = dE.sum(axis=0)
    g["P"][:T] = dE
    return g


class Adam:
    def __init__(self, p: dict, lr: float = _LR):
        self.lr, self.t = lr, 0
        self.m = {k: np.zeros_like(v) for k, v in p.items()}
        self.v = {k: np.zeros_like(v) for k, v in p.items()}

    def step(self, p: dict, g: dict) -> None:
        self.t += 1
        for k in p:
            self.m[k] = _ADAM_B1 * self.m[k] + (1 - _ADAM_B1) * g[k]
            self.v[k] = _ADAM_B2 * self.v[k] + (1 - _ADAM_B2) * g[k] ** 2
            m_hat = self.m[k] / (1 - _ADAM_B1 ** self.t)
            v_hat = self.v[k] / (1 - _ADAM_B2 ** self.t)
            p[k] = p[k] - self.lr * m_hat / (np.sqrt(v_hat) + _ADAM_EPS)


# -- sealing -----------------------------------------------------------------

def _key() -> bytes:
    """``JIM_MODEL_KEY`` when set; otherwise derived from the database path
    so a local install reads its own weights back without configuration.
    Either way the row is ciphertext, and a copied database is noise."""
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.hkdf import HKDF
    configured = os.environ.get("JIM_MODEL_KEY")
    ikm = (configured.encode() if configured else
           hashlib.sha256(f"jim-condition-net::{db.db_path()}".encode()).digest())
    return HKDF(algorithm=hashes.SHA256(), length=32, salt=None,
                info=b"jim-condition-net").derive(ikm)


def _pack(p: dict) -> bytes:
    names = sorted(p)
    header = json.dumps({"config": CONFIG, "version": WEIGHTS_VERSION,
                         "names": names,
                         "shapes": [list(p[k].shape) for k in names]}).encode()
    body = np.concatenate([p[k].astype(np.float64).ravel() for k in names]).tobytes()
    return len(header).to_bytes(4, "big") + header + body


def _unpack(plain: bytes) -> dict:
    n = int.from_bytes(plain[:4], "big")
    header = json.loads(plain[4:4 + n])
    flat = np.frombuffer(plain[4 + n:], dtype=np.float64)
    out, at = {}, 0
    for name, shape in zip(header["names"], header["shapes"]):
        size = int(np.prod(shape)) if shape else 1
        out[name] = flat[at:at + size].reshape(shape).copy()
        at += size
    return out


def seal(user_id: str, p: dict) -> bytes:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    nonce = os.urandom(12)
    return nonce + AESGCM(_key()).encrypt(nonce, _pack(p), user_id.encode())


def unseal(user_id: str, blob: bytes) -> dict:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    return _unpack(AESGCM(_key()).decrypt(bytes(blob[:12]), bytes(blob[12:]),
                                          user_id.encode()))


_loaded: dict = {}


def load(user_id: str) -> tuple[dict, int]:
    row = db.connect().execute(
        "SELECT blob, version, updated_at FROM condition_weights WHERE user_id=?",
        (user_id,)).fetchone()
    if row is None:
        return init_params(_seed(user_id)), 0
    key = (db.db_path(), user_id)
    hit = _loaded.get(key)
    if hit is None or hit[0] != row["updated_at"]:
        hit = (row["updated_at"], unseal(user_id, row["blob"]), row["version"])
        _loaded[key] = hit
    return {k: v.copy() for k, v in hit[1].items()}, hit[2]


def status(user_id: str) -> dict:
    row = db.connect().execute(
        "SELECT version, trained_on, loss_before, loss_after, updated_at,"
        " length(blob) AS bytes FROM condition_weights WHERE user_id=?",
        (user_id,)).fetchone()
    base = {"user_id": user_id, "config": CONFIG,
            "emphasis_names": list(EMPHASES),
            "parameters": int(sum(v.size for v in init_params(0).values())),
            "encrypted_at_rest": True, "external_transmission": False,
            "trains_every_readings": TRAIN_EVERY}
    if row is None:
        return {**base, "trained": False, "weights_build": 0, "trained_on": 0,
                "loss_before": None, "loss_after": None, "updated_at": None,
                "sealed_bytes": 0}
    return {**base, "trained": True, "weights_build": row["version"],
            "trained_on": row["trained_on"], "loss_before": row["loss_before"],
            "loss_after": row["loss_after"], "updated_at": row["updated_at"],
            "sealed_bytes": row["bytes"]}


# -- the readings --------------------------------------------------------------

def readings(user_id: str, limit: int | None = None, pdi=None) -> list[dict]:
    """The stored biometric readings, oldest first, each with its time.
    Vaulted rows are read back through the vault when one is given and
    skipped otherwise — a key is not a reading."""
    limit = limit or CONFIG["window"]
    rows = db.connect().execute(
        "SELECT detail, created_at FROM events WHERE user_id=? AND"
        " type='biometric' ORDER BY created_at DESC, rowid DESC LIMIT ?",
        (user_id, limit)).fetchall()
    out = []
    for r in rows:
        try:
            detail = json.loads(r["detail"] or "{}")
        except ValueError:
            continue
        if detail.get("vaulted"):
            if pdi is None:
                continue
            raw = pdi.get(detail["pdi_key"])
            detail = json.loads(raw) if raw else {}
        if isinstance(detail, dict) and detail:
            out.append({**detail, "_at": r["created_at"]})
    return list(reversed(out))


def _person(user_id: str) -> tuple[list[str], str, float]:
    row = db.connect().execute(
        "SELECT known_conditions, sensitivity, resting_heart_rate FROM users"
        " WHERE id=?", (user_id,)).fetchone()
    if row is None:
        return [], "balanced", 60.0
    base = db.connect().execute(
        "SELECT value FROM baselines WHERE user_id=? AND metric='heart_rate'",
        (user_id,)).fetchone()
    resting = (base["value"] if base else None) or row["resting_heart_rate"] or 60
    try:
        known = json.loads(row["known_conditions"] or "[]")
    except ValueError:
        known = []
    return list(known), row["sensitivity"] or "balanced", float(resting)


# -- inference ---------------------------------------------------------------

def condition(user_id: str, details: list[dict] | None = None, *,
              pdi=None) -> dict | None:
    """Run the network over the person's recent readings. None when there is
    nothing to attend to yet."""
    details = readings(user_id, pdi=pdi) if details is None else details
    details = details[-CONFIG["window"]:]
    if not details:
        return None
    known, sensitivity, resting = _person(user_id)
    trust = np.array([trust_of(d) for d in details])
    engagement = _unit(details[-1].get("stress_level"), 0, 1, 0.0)
    tau = temperature(sensitivity, engagement)
    p, version = load(user_id)
    cache = forward(p, features(details, resting), context(known, sensitivity),
                    trust, tau)
    row = cache["layers"][-1]["A"][:, -1, :].mean(axis=0)
    return {"version": version, "temperature": tau,
            "sensitivity": sensitivity, "known_conditions": len(known),
            "engagement": round(engagement, 4),
            "predicted_deviation": round(float(cache["y_dev"]) - 0.5, 4),
            "emphases": {n: round(float(v), 4)
                         for n, v in zip(EMPHASES, cache["y_emph"])},
            "attention": [{"reading": i + 1, "weight": round(float(w), 4),
                           "trust": round(float(t), 3),
                           "read_at": d.get("_at")}
                          for i, (w, t, d) in enumerate(zip(row, trust, details))]}


def render(c: dict) -> str:
    top = sorted(c["attention"], key=lambda a: -a["weight"])[:3]
    attended = "; ".join(
        f"reading {a['reading']} of {len(c['attention'])} "
        f"(weight {a['weight']:.2f}, trust {a['trust']:.2f})" for a in top)
    emph = ", ".join(f"{k} {v:.2f}" for k, v in c["emphases"].items())
    state = f"trained weights v{c['version']}" if c["version"] else "initial weights"
    lean = c["predicted_deviation"]
    where = ("above" if lean > 0.02 else "below" if lean < -0.02 else "at")
    return (f"Condition-conditioned attention (condition network, {state}; "
            f"temperature {c['temperature']:.2f} from the {c['sensitivity']} "
            f"dial and current engagement {c['engagement']:.2f}; "
            f"{c['known_conditions']} declared condition(s) in context). Over "
            f"the recent readings the network attends most to — {attended}. "
            f"The next reading is expected {where} baseline "
            f"({lean:+.2f}). Emphases for this reply — {emph}. Weight your "
            "focus accordingly; who you are, what you will not do, and every "
            "safety path stay exactly as they are.")


def record(user_id: str, surface: str, c: dict) -> str:
    conn = db.connect()
    # Commit only what this call opened: a caller mid-transaction keeps
    # its own commit, and a call that opened the write must not leave the
    # lock held for a request on another thread to run into.
    opened = not conn.in_transaction
    cid = db.new_id("cond")
    conn.execute(
        "INSERT INTO condition_conditioning (id, user_id, surface,"
        " weights_version, temperature, engagement, predicted_deviation,"
        " attention, emphases, created_at) VALUES (?,?,?,?,?,?,?,?,?,?)",
        (cid, user_id, surface, c["version"], c["temperature"],
         c["engagement"], c["predicted_deviation"],
         json.dumps(c["attention"]), json.dumps(c["emphases"]), db.utcnow()))
    if opened:
        conn.commit()
    return cid


def prompt_lines(user_id: str, surface: str = "coach", pdi=None) -> list[str]:
    """The line the speaking surfaces append: run the network, record the
    conditioning, render it. Empty when there are no readings yet."""
    c = condition(user_id, pdi=pdi)
    if c is None:
        return []
    record(user_id, surface, c)
    return [render(c)]


def conditioning_of(user_id: str, limit: int = 20) -> list[dict]:
    rows = db.connect().execute(
        "SELECT * FROM condition_conditioning WHERE user_id=?"
        " ORDER BY created_at DESC, rowid DESC LIMIT ?",
        (user_id, limit)).fetchall()
    out = []
    for r in rows:
        item = dict(r)
        item["attention"] = json.loads(item["attention"])
        item["emphases"] = json.loads(item["emphases"])
        out.append(item)
    return out


# -- training ------------------------------------------------------------------

def _label(detail: dict, known: list[str], sensitivity: str) -> np.ndarray:
    """What the reading that followed called for, by the product's own
    detector: reassure / act / escalate / monitor."""
    from . import conditions
    found = conditions.detect({k: v for k, v in detail.items()
                               if not k.startswith("_")},
                              detail.get("note"), known=known,
                              sensitivity=sensitivity)
    if found is None:
        return np.array([1.0, 0.0, 0.0, 0.2])
    return {"info": np.array([0.5, 0.0, 0.0, 1.0]),
            "guidance": np.array([0.0, 1.0, 0.0, 1.0]),
            "critical": np.array([0.0, 1.0, 1.0, 1.0])}.get(
                found.severity, np.array([0.0, 1.0, 0.0, 1.0]))


def _samples(user_id: str, pdi=None) -> list[dict]:
    details = readings(user_id, limit=_MAX_SAMPLES + CONFIG["window"], pdi=pdi)
    known, sensitivity, resting = _person(user_id)
    samples = []
    for t in range(len(details) - 1):
        lo = max(0, t + 1 - CONFIG["window"])
        window, nxt = details[lo:t + 1], details[t + 1]
        samples.append({
            "window": window, "known": known, "sensitivity": sensitivity,
            "resting": resting,
            "engagement": _unit(window[-1].get("stress_level"), 0, 1, 0.0),
            "t_dev": float(features([nxt], resting)[0, 0]),
            "t_emph": _label(nxt, known, sensitivity)})
    return samples[-_MAX_SAMPLES:]


def _run(p: dict, s: dict) -> dict:
    return forward(p, features(s["window"], s["resting"]),
                   context(s["known"], s["sensitivity"]),
                   np.array([trust_of(d) for d in s["window"]]),
                   temperature(s["sensitivity"], s["engagement"]))


def _mean_loss(p: dict, samples: list[dict]) -> float:
    return sum(loss_of(_run(p, s), s["t_dev"], s["t_emph"])
               for s in samples) / len(samples)


def train(user_id: str, *, epochs: int = 8, pdi=None) -> dict:
    """Claim 26 for the attention layers: fit them to this person's own
    readings, on this machine, with the network blocked, and seal them."""
    from . import finetune
    samples = _samples(user_id, pdi=pdi)
    p, version = load(user_id)
    if not samples:
        return {"trained": False, "samples": 0, "training_steps": 0,
                "loss_before": None, "loss_after": None, "weights_build": version,
                "reason": "fewer than two readings on record"}
    original = finetune._no_egress()
    try:
        loss_before = _mean_loss(p, samples)
        opt, steps = Adam(p), 0
        for _ in range(epochs):
            for s in samples:
                opt.step(p, backward(p, _run(p, s), s["t_dev"], s["t_emph"]))
                steps += 1
        loss_after = _mean_loss(p, samples)
    finally:
        finetune._restore(original)
    conn = db.connect()
    conn.execute(
        "INSERT INTO condition_weights (user_id, blob, version, trained_on,"
        " loss_before, loss_after, updated_at) VALUES (?,?,?,?,?,?,?)"
        " ON CONFLICT (user_id) DO UPDATE SET blob=excluded.blob,"
        " version=condition_weights.version+1, trained_on=excluded.trained_on,"
        " loss_before=excluded.loss_before, loss_after=excluded.loss_after,"
        " updated_at=excluded.updated_at",
        (user_id, seal(user_id, p), 1, len(samples),
         round(loss_before, 6), round(loss_after, 6), db.utcnow()))
    conn.commit()
    # `weights_build`, `training_steps`: one wire name, one type — `version`
    # is a string on /health and `steps` a list on the playbook.
    return {"trained": True, "samples": len(samples), "training_steps": steps,
            "loss_before": round(loss_before, 6),
            "loss_after": round(loss_after, 6),
            "weights_build": status(user_id)["weights_build"],
            "encrypted_at_rest": True, "external_transmission": False}


def maybe_train(user_id: str, pdi=None) -> dict | None:
    """The pass ingest runs on its own: every ``TRAIN_EVERY`` readings, and
    never in a way that can break the reading being taken."""
    n = db.connect().execute(
        "SELECT COUNT(*) FROM events WHERE user_id=? AND type='biometric'",
        (user_id,)).fetchone()[0]
    if n < 2 or n % TRAIN_EVERY:
        return None
    try:
        return train(user_id, pdi=pdi)
    except Exception:  # noqa: BLE001 — a learning pass never stops a reading
        return None
