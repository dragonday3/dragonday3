#!/usr/bin/env python3
"""Generate the GitHub profile image: assets/terminal.svg

One Kali Linux terminal running tmux, five panes:
  0 neofetch   skull logo + profile
  1 nmap       Kairavi's repos shown as open services
  2 redops     kill chain, animated sweep
  3 grc        5x5 likelihood x impact risk matrix + frameworks
  4 git log    live recent commits (tools/recent_commits.json, written by the Action) + cert roadmap

Self-contained SVG, stdlib only. CSS animations play inside GitHub's image proxy.
Run:  py -3.10 tools/gen.py
"""
import os, html, json

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "assets", "terminal.svg")

C = dict(
    bg="#0b0f17", bar="#151b26", border="#263042", text="#d0d7e2", dim="#6b7a90",
    blue="#367bf0", red="#ff4757", green="#2ed573", yellow="#ffd32a", cyan="#22c7d6",
    orange="#ff9f43", magenta="#c56cf0", tmux="#2ed573",
)
FONT = "'JetBrains Mono','Fira Code','Cascadia Code','DejaVu Sans Mono',ui-monospace,monospace"
FS, LH = 13, 18
CW = FS * 0.6                     # monospace advance
W, H = 1200, 780
TOP, STATUS = 34, 26              # window title bar, tmux status bar
MID = 380                         # y where the bottom row of panes starts

_delay = [0.0]


def esc(s):
    return html.escape(s, quote=True)


def T(x, y, spans, size=FS, anim=True, weight=None, anchor=None):
    """Text line. spans = str or [(text, color), ...]. anim=True fades it in after the previous line."""
    if isinstance(spans, str):
        spans = [(spans, "text")]
    inner = "".join(f'<tspan fill="{C.get(k, k)}">{esc(s)}</tspan>' for s, k in spans)
    st = ""
    if anim:
        _delay[0] += 0.12
        st = f' class="l" style="animation-delay:{_delay[0]:.2f}s"'
    w = f' font-weight="{weight}"' if weight else ""
    a = f' text-anchor="{anchor}"' if anchor else ""
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}"{w}{a}{st} xml:space="preserve">{inner}</text>'


def prompt(x, y, path, cmd):
    """Kali root-style zsh prompt: blue frame, red user@host."""
    return [
        T(x, y, [("┌──(", "blue"), ("kairavi㉿kali", "red"), (")-[", "blue"), (path, "text"), ("]", "blue")], weight="bold"),
        T(x, y + LH, [("└─", "blue"), ("$ ", "red"), (cmd, "text")]),
    ]


def recent_commits():
    try:
        with open(os.path.join(HERE, "recent_commits.json"), encoding="utf-8") as f:
            return [c for c in json.load(f) if c.get("msg")][:5]
    except (OSError, ValueError):
        return []


def clip(s, n):
    return s if len(s) <= n else s[: n - 1] + "…"


# ── panes ───────────────────────────────────────────────────────────────────
def pane_neofetch(x, y):
    out = prompt(x, y, "~", "neofetch")
    skull = [
        "     _______     ",
        "  .-'       '-.  ",
        " /   _     _   \\ ",
        "|   (o)   (o)   |",
        "|      / \\      |",
        " \\    '---'    / ",
        "  '-._|||||_.-'  ",
        "     |_|_|_|     ",
    ]
    info = [
        [("kairavi", "red"), ("@", "text"), ("kali", "red")],
        [("─" * 16, "dim")],
        [("name      ", "blue"), ("Kairavi Shah", "text")],
        [("role      ", "blue"), ("Red Team · GRC", "text")],
        [("focus     ", "blue"), ("offsec · vuln research", "text")],
        [("          ", "blue"), ("risk governance", "text")],
        [("shell     ", "blue"), ("zsh · python3", "text")],
        [("arsenal   ", "blue"), ("nmap burp msf wireshark", "text")],
        [("frameworks", "blue"), (" NIST·ISO27001·CIS", "text")],
        [("          ", "blue"), ("MITRE ATT&CK · OWASP", "text")],
    ]
    by = y + 2 * LH + 14
    for i, row in enumerate(skull):
        out.append(T(x, by + i * LH, [(row, "red")]))
    for i, row in enumerate(info):
        out.append(T(x + 19 * CW, by + i * LH, row))
    sy = by + len(info) * LH + 6
    for i, k in enumerate(["bg", "red", "green", "yellow", "blue", "magenta", "cyan", "text"]):
        out.append(f'<rect x="{x + 19 * CW + i * 22:.1f}" y="{sy:.1f}" width="20" height="12" fill="{C[k]}" stroke="{C["border"]}"/>')
    return out


SERVICES = [  # port, repo, description (from each repo's README)
    ("22/tcp", "reconmap", "passive attack-surface intel · CT logs · shodan"),
    ("80/tcp", "apifuzz", "OpenAPI spec → OWASP API Top 10 findings · SARIF"),
    ("443/tcp", "vulnsight", "evidence-based vuln assessment · risk scoring"),
    ("4444/tcp", "redops", "red team campaigns · ATT&CK TTPs · OPSEC checks"),
    ("8443/tcp", "credchain", "solidity credential verification · sepolia"),
    ("31337/tcp", "stego", "PyQt6 image steganography · password lock"),
]


def pane_nmap(x, y):
    out = prompt(x, y, "~/recon", "nmap -sV --script=vuln github.com/dragonday3")
    yy = y + 2 * LH + 10
    out.append(T(x, yy, [("Starting Nmap 7.95 ( https://nmap.org )", "dim")]))
    out.append(T(x, yy + LH, [("Nmap scan report for ", "text"), ("github.com/dragonday3", "cyan")]))
    out.append(T(x, yy + 2 * LH, [("Host is up (0.0031s latency).", "text")]))
    out.append(T(x, yy + 3.5 * LH, [("PORT       STATE  SERVICE     VERSION", "yellow")], weight="bold"))
    for i, (port, name, desc) in enumerate(SERVICES):
        out.append(T(x, yy + (4.5 + i) * LH, [
            (f"{port:<11}", "text"), ("open   ", "green"), (f"{name:<12}", "red"), (desc, "text")]))
    ey = yy + (5 + len(SERVICES)) * LH
    out.append(T(x, ey, [("| vulners: ", "dim"), ("built from scratch in python — no black-box wrappers", "magenta")]))
    out.append(T(x, ey + LH, [("|_ ", "dim"), ("understand the attack before you automate it.", "magenta")]))
    out.append(T(x, ey + 2.5 * LH, [("Nmap done: ", "text"), (f"{len(SERVICES)} services up", "green"), (" · scanned in 0.42 seconds", "text")]))
    return out


STAGES = ["recon", "weaponize", "deliver", "exploit", "persist", "lateral", "exfil"]
ASK = ["what can an attacker see?", "what exploits fit the surface?", "how does the payload land?",
       "where does execution occur?", "how does an attacker stay?", "what else is reachable?",
       "what leaves the network?"]


def pane_killchain(x, y, w):
    out = prompt(x, y, "~/redops", "redops chain --mode=assume-breach")
    yy = y + 2 * LH + 12
    bh = 24
    for i, (s, q) in enumerate(zip(STAGES, ASK)):
        ry = yy + i * (bh + 6)
        out.append(f'<rect x="{x:.1f}" y="{ry:.1f}" width="{w - 24:.1f}" height="{bh}" rx="3" fill="none" stroke="{C["border"]}"/>')
        out.append(T(x + 8, ry + 16, [(f"{i + 1}. ", "dim"), (f"{s:<10}", "red"), (q, "text")], anim=False))
    # sweep highlight walking down the chain
    out.append(f'<rect class="sweep" x="{x:.1f}" y="{yy:.1f}" width="{w - 24:.1f}" height="{bh}" rx="3" '
               f'fill="{C["red"]}" fill-opacity="0.16" stroke="{C["red"]}"/>')
    out.append(T(x, yy + 7 * (bh + 6) + 14, [("[+] ", "green"), ("build the chain. then break every link.", "text")]))
    return out


def pane_grc(x, y):
    out = prompt(x, y, "~/grc", "grc risk --matrix --framework nist-csf")
    yy = y + 2 * LH + 12
    cell, gap = 26, 3
    gx = x + 24
    for li in range(5):           # likelihood rows, 5 at the top
        L = 5 - li
        out.append(T(x + 6, yy + li * (cell + gap) + 20, [(str(L), "dim")], anim=False))
        for i in range(5):
            score = L * (i + 1)
            col = "green" if score <= 4 else "yellow" if score <= 9 else "orange" if score <= 14 else "red"
            cls = ' class="hot"' if score >= 15 else ""
            out.append(f'<rect{cls} x="{gx + i * (cell + gap):.1f}" y="{yy + li * (cell + gap):.1f}" '
                       f'width="{cell}" height="{cell}" rx="3" fill="{C[col]}" fill-opacity="0.55"/>')
    by = yy + 5 * (cell + gap) + 14
    out.append(T(gx, by, [("impact →", "dim")], anim=False))
    out.append(T(x - 2, yy - 6, [("L", "dim")], anim=False))
    tx = gx + 5 * (cell + gap) + 14
    rows = [
        [("NIST  ", "blue"), ("ID·PR·DE·RS·RC", "text")],
        [("ISO   ", "blue"), ("27001 ISMS", "text")],
        [("CIS   ", "blue"), ("v8 IG1→IG3", "text")],
        [("MITRE ", "blue"), ("ATT&CK TTPs", "text")],
        [("OWASP ", "blue"), ("Top10 · API", "text")],
    ]
    for i, r in enumerate(rows):
        out.append(T(tx, yy + 14 + i * (LH + 8), r, size=12))
    out.append(T(x, by + LH + 4, [("risk = threat × vuln × impact", "yellow")], size=12))
    out.append(T(x, by + 2 * LH + 4, [("[+] ", "green"), ("governance turns process into accountability", "text")], size=12))
    return out


CERTS = [("CompTIA Security+", "in progress", "yellow"), ("CEH", "queued", "dim"),
         ("OSCP", "target", "red"), ("CISM / CRISC", "grc track", "blue")]


def pane_git(x, y, w):
    out = prompt(x, y, "~", "git log --all --oneline -5")
    yy = y + 2 * LH + 10
    n = int((w - 24) / CW)
    commits = recent_commits()
    if not commits:
        out.append(T(x, yy, [("no public commits yet", "dim")]))
    for i, c in enumerate(commits):
        out.append(T(x, yy + i * 2 * LH, [(c["sha"], "yellow"), (" " + c.get("date", ""), "dim"), (" (" + c["repo"] + ")", "cyan")]))
        out.append(T(x + 2 * CW, yy + (i * 2 + 1) * LH, [(clip(c["msg"], n - 4), "text")]))
    cy = yy + 10 * LH
    out.append(T(x, cy, [("$ ", "red"), ("cat certs.txt", "text")]))
    for i, (name, state, col) in enumerate(CERTS):
        out.append(T(x, cy + (i + 1) * LH, [("[ ] ", "dim"), (f"{name:<19}", "text"), ("# " + state, col)]))
    py = cy + 5 * LH + 2
    out.append(T(x, py, [("$ ", "red")]))
    out.append(f'<rect class="cur" x="{x + 2 * CW:.1f}" y="{py - 12:.1f}" width="{CW:.1f}" height="15" fill="{C["text"]}"/>')
    return out


# ── assemble ────────────────────────────────────────────────────────────────
def build():
    _delay[0] = 0.0
    p = 14                                     # pane padding
    bot = H - STATUS
    cols = [0, 400, 800, W]
    panes = []
    panes += pane_neofetch(p, TOP + p + 12)
    panes += pane_nmap(470 + p, TOP + p + 12)
    panes += pane_killchain(cols[0] + p, MID + p + 12, cols[1] - cols[0])
    panes += pane_grc(cols[1] + p, MID + p + 12)
    panes += pane_git(cols[2] + p, MID + p + 12, cols[3] - cols[2])
    end = _delay[0] + 0.3

    sep = C["border"]
    lines = [
        f'<line x1="470" y1="{TOP}" x2="470" y2="{MID}" stroke="{C["tmux"]}"/>',   # active pane = nmap
        f'<line x1="0" y1="{MID}" x2="{W}" y2="{MID}" stroke="{sep}"/>',
        f'<line x1="{cols[1]}" y1="{MID}" x2="{cols[1]}" y2="{bot}" stroke="{sep}"/>',
        f'<line x1="{cols[2]}" y1="{MID}" x2="{cols[2]}" y2="{bot}" stroke="{sep}"/>',
    ]
    title = [
        f'<rect width="{W}" height="{TOP}" fill="{C["bar"]}"/>',
        T(W / 2, 22, [("kairavi@kali: ~/recon", "text")], anim=False, anchor="middle"),
        T(16, 22, [("▣ ", "blue"), ("File  Actions  Edit  View  Help", "dim")], size=12, anim=False),
    ] + [f'<circle cx="{W - 20 - i * 22}" cy="17" r="6" fill="{C[k]}"/>' for i, k in enumerate(["red", "yellow", "green"])]
    status = [
        f'<rect y="{bot}" width="{W}" height="{STATUS}" fill="{C["tmux"]}"/>',
        T(10, bot + 18, [("[kairavi] 0:neofetch  1:nmap*  2:redops  3:grc  4:git", "#0b0f17")], anim=False, weight="bold"),
        T(W - 10, bot + 18, [('"kali" · the quieter you become, the more you are able to hear', "#0b0f17")],
          anim=False, anchor="end"),
    ]

    css = f"""
text{{font-family:{FONT};}}
.l{{opacity:0;animation:in .25s ease forwards;}}
@keyframes in{{to{{opacity:1;}}}}
.cur{{animation:blink 1s steps(1) infinite;animation-delay:{end:.2f}s;opacity:0;}}
@keyframes blink{{0%{{opacity:1;}}50%{{opacity:0;}}}}
.sweep{{animation:sweep 7s steps(7) infinite;}}
@keyframes sweep{{from{{transform:translateY(0);}}to{{transform:translateY({7 * 30}px);}}}}
.hot{{animation:hot 2s ease-in-out infinite alternate;}}
@keyframes hot{{to{{fill-opacity:.95;}}}}
"""
    body = "\n".join(title + lines + panes + status)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
            f'role="img" aria-label="Kairavi Shah — red team and GRC, Kali tmux terminal">\n'
            f'<style>{css}</style>\n'
            f'<rect width="{W}" height="{H}" rx="10" fill="{C["bg"]}" stroke="{C["border"]}"/>\n{body}\n</svg>\n')


if __name__ == "__main__":
    svg = build()
    assert svg.count("<text") > 60 and "kairavi㉿kali" in svg
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(svg)
    print("wrote", os.path.normpath(OUT), len(svg), "bytes")
