import os, json, csv, random
from datetime import datetime
from collections import Counter
from functools import reduce

from nicegui import ui, app

# ── DB ────────────────────
DATA_FILE = "campus_data.json"
_db = {
    "students": {}, "courses": {}, "events": {}, "fees": {},
    "records_file": "student_records.csv",
    "next_sid": 1001, "next_cid": 201,
}

def save_db():
    with open(DATA_FILE, "w") as f:
        json.dump(_db, f, indent=2)

def load_db():
    global _db
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            try:
                _db.update(json.load(f))
            except json.JSONDecodeError:
                pass

load_db()

GRADE_TABLE = [
    (90, 101, "A", "Excellent",        "#a3a3a3"),
    (75,  90, "B", "Very Good",        "#a3a3a3"),
    (60,  75, "C", "Good",             "#a3a3a3"),
    (40,  60, "D", "Average",          "#d97706"),
    ( 0,  40, "F", "Needs Improvement","#dc2626"),
]

def evaluate_grade(score):
    for lo, hi, grade, remark, colour in GRADE_TABLE:
        if lo <= score < hi:
            return grade, remark, colour
    return "F", "Needs Improvement", "#dc2626"

MAX_COURSES_PER_STUDENT = 5

# ── GLOBAL CSS ────────────────────────────────
GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=DM+Sans:wght@300;400;500;600&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --bg:        #0f0f0f;
  --bg-raised: #141414;
  --bg-subtle: #1a1a1a;
  --border:    #242424;
  --border-lo: #1c1c1c;
  --text:      #e8e8e8;
  --text-2:    #888;
  --text-3:    #555;
  --accent:    #d97706;
  --danger:    #dc2626;
  --mono:      'IBM Plex Mono', monospace;
  --sans:      'DM Sans', sans-serif;
}

html, body {
  background: var(--bg);
  color: var(--text);
  font-family: var(--sans);
  font-size: 14px;
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
}

.q-field__control {
  background: var(--bg-raised) !important;
  border: 1px solid var(--border) !important;
  border-radius: 4px !important;
  box-shadow: none !important;
}
.q-field__control:hover { border-color: #333 !important; }
.q-field--focused .q-field__control { border-color: var(--accent) !important; }
.q-field__native, .q-field__input, .q-field__prefix, .q-field__suffix {
  color: var(--text) !important;
  font-family: var(--sans) !important;
  font-size: 13px !important;
}
.q-field__label { color: var(--text-2) !important; font-size: 12px !important; }
.q-field__bottom { display: none !important; }
.q-select__dropdown-icon { color: var(--text-3) !important; }

.q-table__container, .q-table { background: transparent !important; }
.q-table thead th {
  background: var(--bg-subtle) !important;
  color: var(--text-3) !important;
  font-family: var(--mono) !important;
  font-size: 10px !important;
  font-weight: 500 !important;
  letter-spacing: 0.08em !important;
  text-transform: uppercase !important;
  border-bottom: 1px solid var(--border) !important;
  padding: 8px 12px !important;
}
.q-table tbody td {
  color: var(--text) !important;
  font-size: 13px !important;
  border-bottom: 1px solid var(--border-lo) !important;
  padding: 9px 12px !important;
}
.q-table tbody tr:hover td { background: var(--bg-subtle) !important; }
.q-table { border: 1px solid var(--border) !important; border-radius: 4px !important; }

::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }

.q-notification { font-family: var(--sans) !important; font-size: 13px !important; border-radius: 4px !important; }

.q-menu { background: var(--bg-raised) !important; border: 1px solid var(--border) !important; border-radius: 4px !important; box-shadow: 0 4px 16px rgba(0,0,0,0.6) !important; }
.q-item { color: var(--text) !important; font-size: 13px !important; }
.q-item:hover { background: var(--bg-subtle) !important; }
.q-item--active { color: var(--accent) !important; background: transparent !important; }

.q-separator { background: var(--border) !important; }
.q-header { box-shadow: none !important; border-bottom: 1px solid var(--border) !important; }
.q-field--type-number input[type=number]::-webkit-inner-spin-button { opacity: 0.3; }
</style>
"""

GRADE_COLORS = {"A": "#e8e8e8", "B": "#e8e8e8", "C": "#a3a3a3", "D": "#d97706", "F": "#dc2626"}

def grade_color(g): return GRADE_COLORS.get(g, "#888")


# ── PRIMITIVES ────────────

def shell(title: str):
    ui.add_head_html(GLOBAL_CSS)
    ui.add_head_html(f"<title>{title} — SCIS</title>")


def sidebar(active: str):
    nav_items = [
        ("Overview",      "/"),
        ("Register",      "/register"),
        ("Enroll",        "/enroll"),
        ("Records",       "/records"),
        ("Sort & Search", "/sort"),
        ("Fees",          "/fees"),
        ("Files",         "/files"),
        ("Directory",     "/directory"),
        ("Analytics",     "/analytics"),
    ]
    with ui.left_drawer(fixed=True).style(
        "background:#0f0f0f; border-right:1px solid #1c1c1c; "
        "width:200px; padding:0; display:flex; flex-direction:column;"
    ):
        with ui.element("div").style("padding:20px 20px 16px; border-bottom:1px solid #1c1c1c;"):
            ui.label("SCIS").style(
                "font-family:var(--mono); font-size:13px; font-weight:500; "
                "color:#e8e8e8; letter-spacing:0.12em;"
            )
            ui.label("Campus Information").style("font-size:11px; color:#555; margin-top:2px;")

        with ui.element("div").style("padding:20px 20px 6px;"):
            ui.label("MODULES").style(
                "font-family:var(--mono); font-size:10px; color:#444; letter-spacing:0.1em;"
            )

        for label, path in nav_items:
            is_active = active == label
            border = "border-left:2px solid #d97706;" if is_active else "border-left:2px solid transparent;"
            color  = "#e8e8e8" if is_active else "#666"
            bg     = "background:#141414;" if is_active else ""
            with ui.element("div").style(
                f"padding:7px 18px 7px 18px; cursor:pointer; {border} {bg}"
                "transition:background 0.1s;"
            ).on("click", lambda p=path: ui.navigate.to(p)):
                ui.label(label).style(
                    f"font-size:13px; color:{color}; font-weight:{'500' if is_active else '400'};"
                )

        with ui.element("div").style("margin-top:auto; padding:16px 20px; border-top:1px solid #1c1c1c;"):
            ns = len(_db["students"]); nc = len(_db["courses"])
            ui.label(f"{ns} students · {nc} courses").style("font-size:11px; color:#444; font-family:var(--mono);")
            ui.label(datetime.now().strftime("%d %b %Y")).style("font-size:11px; color:#333; margin-top:2px;")


def main_col():
    return ui.element("div").style(
        "padding:36px 40px; max-width:900px; width:100%; display:flex; flex-direction:column; gap:0;"
    )


def page_title(title: str, sub: str = ""):
    with ui.element("div").style("margin-bottom:28px; padding-bottom:20px; border-bottom:1px solid #1c1c1c;"):
        ui.label(title).style("font-size:20px; font-weight:600; color:#e8e8e8; letter-spacing:-0.01em;")
        if sub:
            ui.label(sub).style("font-size:12px; color:#555; font-family:var(--mono); margin-top:4px; letter-spacing:0.04em;")


def section_label(text: str, margin_top: int = 28):
    ui.label(text).style(
        f"font-family:var(--mono); font-size:10px; color:#444; letter-spacing:0.1em; "
        f"text-transform:uppercase; margin-top:{margin_top}px; margin-bottom:12px; display:block;"
    )


def stat_row(stats: list):
    with ui.element("div").style(
        "display:flex; gap:0; border:1px solid #1c1c1c; border-radius:4px; overflow:hidden; margin-bottom:24px;"
    ):
        for i, stat in enumerate(stats):
            label, value = stat[0], stat[1]
            color = stat[2] if len(stat) > 2 else "#e8e8e8"
            border = "border-left:1px solid #1c1c1c;" if i > 0 else ""
            with ui.element("div").style(f"padding:14px 20px; flex:1; {border}"):
                ui.label(label).style("font-family:var(--mono); font-size:10px; color:#444; letter-spacing:0.08em; text-transform:uppercase;")
                ui.label(str(value)).style(f"font-size:22px; font-weight:600; color:{color}; margin-top:3px; font-family:var(--mono);")


def inline_bar(value: float, color: str = "#d97706", max_val: float = 100):
    pct = min(100, max(0, value / max_val * 100))
    with ui.element("div").style("width:80px; height:3px; background:#1c1c1c; border-radius:1px; overflow:hidden; display:inline-block; vertical-align:middle;"):
        ui.element("div").style(f"width:{pct}%; height:100%; background:{color};")


def btn(label: str, on_click=None, danger=False, secondary=False):
    if danger:
        style = "background:transparent; border:1px solid #3a1a1a; color:#dc2626;"
    elif secondary:
        style = "background:transparent; border:1px solid #242424; color:#888;"
    else:
        style = "background:#d97706; border:1px solid #d97706; color:#0f0f0f; font-weight:600;"

    b = ui.button(label).style(
        f"{style} font-family:var(--sans); font-size:13px; padding:7px 16px; "
        f"border-radius:4px; cursor:pointer; transition:opacity 0.1s; letter-spacing:0;"
    ).props("flat no-caps")
    if on_click:
        b.on("click", on_click)
    return b


def notice(msg: str, kind: str = "ok"):
    types = {"ok": "positive", "err": "negative", "warn": "warning"}
    ui.notify(msg, type=types.get(kind, "info"), position="bottom-right", timeout=3000,
              classes="text-sm")


def data_table(columns, rows, row_key="id"):
    return ui.table(columns=columns, rows=rows, row_key=row_key).style("width:100%;").props("dark flat dense")


# ── PAGES ───────────

@ui.page("/")
def page_dashboard():
    shell("Overview")
    sidebar("Overview")
    with main_col():
        page_title("Overview", "DAYANANDA SAGAR COLLEGE OF ENGINEERING")

        ns = len(_db["students"])
        nc = len(_db["courses"])
        ne = sum(len(v["enrolled"]) for v in _db["courses"].values())
        nf = len(_db["fees"])

        stat_row([
            ("Students",    ns,  "#e8e8e8"),
            ("Courses",     nc,  "#e8e8e8"),
            ("Enrollments", ne,  "#e8e8e8"),
            ("Fee Records", nf,  "#e8e8e8"),
        ])

        if _db["students"]:
            gc = Counter(s["grade"] for s in _db["students"].values())
            section_label("Grade Distribution", margin_top=0)

            with ui.element("div").style(
                "border:1px solid #1c1c1c; border-radius:4px; overflow:hidden;"
            ):
                with ui.element("div").style(
                    "display:grid; grid-template-columns:60px 1fr 80px 120px; "
                    "background:#141414; padding:8px 12px; border-bottom:1px solid #1c1c1c;"
                ):
                    for h in ["Grade", "Distribution", "Count", "Remark"]:
                        ui.label(h).style("font-family:var(--mono); font-size:10px; color:#444; text-transform:uppercase; letter-spacing:0.08em;")

                grade_remarks = {"A":"Excellent","B":"Very Good","C":"Good","D":"Average","F":"Needs Improvement"}
                total_s = max(ns, 1)
                for g in ["A","B","C","D","F"]:
                    cnt = gc.get(g, 0)
                    pct = cnt / total_s * 100
                    col = grade_color(g)
                    border = "border-bottom:1px solid #1a1a1a;"
                    with ui.element("div").style(
                        f"display:grid; grid-template-columns:60px 1fr 80px 120px; "
                        f"align-items:center; padding:9px 12px; {border}"
                    ):
                        ui.label(g).style(f"font-family:var(--mono); font-weight:500; color:{col}; font-size:13px;")
                        with ui.element("div").style("display:flex; align-items:center; gap:8px;"):
                            with ui.element("div").style("width:160px; height:2px; background:#1a1a1a; border-radius:1px; overflow:hidden;"):
                                ui.element("div").style(f"width:{pct}%; height:100%; background:{col};")
                        ui.label(str(cnt)).style("font-family:var(--mono); font-size:12px; color:#666;")
                        ui.label(grade_remarks[g]).style("font-size:12px; color:#555;")

        section_label("Modules")
        modules = [
            ("01", "Student Registration",   "/register",  "Register students, evaluate grades"),
            ("02", "Course Enrollment",      "/enroll",    "Enroll students into courses"),
            ("03", "Records & Events",       "/records",   "View records, event participation"),
            ("04", "Sort & Search",          "/sort",      "Sorting algorithms and ID lookup"),
            ("05", "Fee Calculation",        "/fees",      "Compute and store fee breakdowns"),
            ("06", "Academic Records File",  "/files",     "Export records to CSV"),
            ("07", "Directory Scanner",      "/directory", "Inspect the file system tree"),
            ("08", "Performance Analytics",  "/analytics", "Subject-wise score analysis"),
        ]
        with ui.element("div").style("border:1px solid #1c1c1c; border-radius:4px; overflow:hidden;"):
            for i, (num, name, path, desc) in enumerate(modules):
                border = "border-bottom:1px solid #1a1a1a;" if i < len(modules)-1 else ""
                with ui.element("div").style(
                    f"display:flex; align-items:center; gap:16px; padding:11px 16px; "
                    f"cursor:pointer; {border} transition:background 0.1s;"
                ).on("click", lambda p=path: ui.navigate.to(p)):
                    ui.label(num).style("font-family:var(--mono); font-size:11px; color:#333; width:24px; flex-shrink:0;")
                    ui.label(name).style("font-size:13px; color:#c8c8c8; font-weight:500; width:200px; flex-shrink:0;")
                    ui.label(desc).style("font-size:12px; color:#555;")


@ui.page("/register")
def page_register():
    shell("Register")
    sidebar("Register")
    result_ref = {"el": None}

    with main_col():
        page_title("Student Registration", "LAB 01 — GRADE EVALUATION")

        with ui.element("div").style("max-width:440px;"):
            with ui.element("div").style("display:flex; flex-direction:column; gap:14px;"):
                name_in  = ui.input("Full name").props("outlined dark").style("width:100%;")
                score_in = ui.number("Exam score", min=0, max=100).props("outlined dark").style("width:100%;")

            with ui.element("div").style("margin-top:16px; display:flex; gap:8px;"):
                def do_register():
                    name  = (name_in.value or "").strip()
                    score = score_in.value
                    if not name:
                        notice("Name is required.", "err"); return
                    if score is None or not (0 <= float(score) <= 100):
                        notice("Score must be 0–100.", "err"); return

                    grade, remark, col = evaluate_grade(float(score))
                    sid = str(_db["next_sid"]); _db["next_sid"] += 1
                    _db["students"][sid] = {
                        "name": name, "age": 20, "score": float(score),
                        "grade": grade, "remark": remark, "grades": [float(score)],
                    }
                    save_db()
                    notice(f"Registered {name} as #{sid}", "ok")

                    result_area.clear()
                    with result_area:
                        with ui.element("div").style(
                            "margin-top:24px; border:1px solid #1c1c1c; border-radius:4px; overflow:hidden;"
                        ):
                            with ui.element("div").style("background:#141414; padding:10px 16px; border-bottom:1px solid #1c1c1c;"):
                                ui.label(f"Registered — #{sid}").style("font-family:var(--mono); font-size:11px; color:#555; letter-spacing:0.08em;")
                            rows_info = [
                                ("Name",   name),
                                ("Score",  f"{score:.1f} / 100"),
                                ("Grade",  grade),
                                ("Remark", remark),
                            ]
                            for j, (lbl, val) in enumerate(rows_info):
                                border = "border-bottom:1px solid #1a1a1a;" if j < len(rows_info)-1 else ""
                                col_val = grade_color(grade) if lbl in ("Grade", "Remark") else "#e8e8e8"
                                with ui.element("div").style(
                                    f"display:flex; justify-content:space-between; align-items:center; "
                                    f"padding:10px 16px; {border}"
                                ):
                                    ui.label(lbl).style("font-size:12px; color:#555;")
                                    ui.label(val).style(f"font-size:13px; font-weight:500; color:{col_val}; font-family:var(--mono);")
                            with ui.element("div").style("padding:12px 16px; background:#0d0d0d;"):
                                ui.label("Score").style("font-family:var(--mono); font-size:10px; color:#333; text-transform:uppercase; letter-spacing:0.08em; margin-bottom:6px; display:block;")
                                with ui.element("div").style("display:flex; align-items:center; gap:10px;"):
                                    with ui.element("div").style("flex:1; height:3px; background:#1a1a1a; border-radius:1px; overflow:hidden;"):
                                        ui.element("div").style(f"width:{score}%; height:100%; background:{grade_color(grade)};")
                                    ui.label(f"{score:.0f}%").style(f"font-family:var(--mono); font-size:11px; color:{grade_color(grade)};")
                    name_in.value = ""; score_in.value = None

                btn("Register student", on_click=do_register)

        result_area = ui.column().style("width:100%; max-width:440px;")

        section_label("Registered Students")
        rows_data = [
            {"id": sid, "name": s["name"], "score": f"{s['score']:.1f}",
             "grade": s["grade"], "remark": s["remark"]}
            for sid, s in _db["students"].items()
        ]
        cols = [
            {"name":"id",     "label":"ID",     "field":"id",     "align":"left"},
            {"name":"name",   "label":"Name",   "field":"name",   "align":"left"},
            {"name":"score",  "label":"Score",  "field":"score",  "align":"left"},
            {"name":"grade",  "label":"Grade",  "field":"grade",  "align":"left"},
            {"name":"remark", "label":"Remark", "field":"remark", "align":"left"},
        ]
        data_table(cols, rows_data)


@ui.page("/enroll")
def page_enroll():
    shell("Enroll")
    sidebar("Enroll")

    with main_col():
        page_title("Course Enrollment", "LAB 02 — COURSE MANAGEMENT")

        if not _db["students"]:
            ui.label("No students registered yet.").style("color:#555; font-size:13px;")
            return

        student_options = {sid: f"{sid} — {s['name']}" for sid, s in _db["students"].items()}

        with ui.element("div").style("max-width:440px; display:flex; flex-direction:column; gap:14px;"):
            sel_sid  = ui.select(options=student_options, label="Student").props("outlined dark").style("width:100%;")
            cname_in = ui.input("Course name").props("outlined dark").style("width:100%;")
            cred_in  = ui.number("Credits", min=1, max=20, value=3).props("outlined dark").style("width:100%;")

        enroll_summary = ui.column().style("width:100%; margin-top:16px;")

        def refresh_summary():
            sid = sel_sid.value
            if not sid: return
            enrolled = [(cid, _db["courses"][cid]) for cid in _db["courses"] if sid in _db["courses"][cid]["enrolled"]]
            total_cr  = sum(c["credits"] for _, c in enrolled)
            enroll_summary.clear()
            with enroll_summary:
                with ui.element("div").style("display:flex; gap:24px; margin-bottom:14px;"):
                    for lbl, val in [("Enrolled", f"{len(enrolled)}/{MAX_COURSES_PER_STUDENT}"), ("Total credits", str(total_cr))]:
                        with ui.element("div"):
                            ui.label(lbl).style("font-family:var(--mono); font-size:10px; color:#444; text-transform:uppercase; letter-spacing:0.08em;")
                            ui.label(val).style("font-family:var(--mono); font-size:18px; color:#e8e8e8; margin-top:2px;")
                if enrolled:
                    rows_e = [{"n": i+1, "course": c["name"], "credits": c["credits"]} for i,(_, c) in enumerate(enrolled)]
                    data_table(
                        [{"name":"n","label":"#","field":"n","align":"left"},
                         {"name":"course","label":"Course","field":"course","align":"left"},
                         {"name":"credits","label":"Credits","field":"credits","align":"left"}],
                        rows_e, row_key="n"
                    )

        def do_enroll():
            sid = sel_sid.value
            cname = (cname_in.value or "").strip()
            credits = cred_in.value
            if not sid:   notice("Select a student.", "err"); return
            if not cname: notice("Course name required.", "err"); return
            if not credits or credits < 1: notice("Credits must be ≥ 1.", "err"); return

            already = [cid for cid in _db["courses"] if sid in _db["courses"][cid]["enrolled"]]
            if len(already) >= MAX_COURSES_PER_STUDENT:
                notice(f"Student is at the {MAX_COURSES_PER_STUDENT}-course limit.", "warn"); return

            cid = next((k for k,v in _db["courses"].items() if v["name"].lower()==cname.lower()), None)
            if not cid:
                cid = str(_db["next_cid"]); _db["next_cid"] += 1
                _db["courses"][cid] = {"name": cname, "credits": int(credits), "enrolled": []}
            if sid not in _db["courses"][cid]["enrolled"]:
                _db["courses"][cid]["enrolled"].append(sid)
            save_db()
            notice(f"Enrolled in '{cname}'", "ok")
            cname_in.value = ""
            refresh_summary()

        sel_sid.on("update:model-value", lambda _: refresh_summary())

        with ui.element("div").style("margin-top:16px; margin-bottom:24px;"):
            btn("Add enrollment", on_click=do_enroll)

        enroll_summary

        section_label("All Courses")
        all_rows = []
        for cid, c in _db["courses"].items():
            names = ", ".join(_db["students"].get(s,{}).get("name","?") for s in c["enrolled"]) or "—"
            all_rows.append({"id":cid,"course":c["name"],"credits":c["credits"],"students":names})
        data_table(
            [{"name":"id","label":"ID","field":"id","align":"left"},
             {"name":"course","label":"Course","field":"course","align":"left"},
             {"name":"credits","label":"Credits","field":"credits","align":"left"},
             {"name":"students","label":"Students","field":"students","align":"left"}],
            all_rows
        )


DEFAULT_EVENTS = ["Tech Fest", "Sports Meet", "Cultural Night"]

@ui.page("/records")
def page_records():
    shell("Records")
    sidebar("Records")

    with main_col():
        page_title("Student Records & Events", "LAB 03 — RECORDS & EVENT PARTICIPATION")

        if not _db["students"]:
            ui.label("No students registered yet.").style("color:#555; font-size:13px;")
            return

        if not _db["events"]:
            for e in DEFAULT_EVENTS:
                _db["events"][e] = {"participants": []}
        sids = list(_db["students"].keys())
        for ev in _db["events"].values():
            if not ev["participants"] and sids:
                ev["participants"] = random.sample(sids, max(1, len(sids)//2))
        save_db()

        section_label("Student Records", margin_top=0)
        rows = []
        for sid, s in _db["students"].items():
            avg = sum(s["grades"]) / len(s["grades"]) if s["grades"] else 0
            rows.append({"id":sid,"name":s["name"],"avg":f"{avg:.1f}","grade":s["grade"],"remark":s["remark"]})
        data_table(
            [{"name":"id","label":"ID","field":"id","align":"left"},
             {"name":"name","label":"Name","field":"name","align":"left"},
             {"name":"avg","label":"Avg Score","field":"avg","align":"left"},
             {"name":"grade","label":"Grade","field":"grade","align":"left"},
             {"name":"remark","label":"Remark","field":"remark","align":"left"}],
            rows
        )

        section_label("Event Participation")
        event_sets = {n: set(ev["participants"]) for n, ev in _db["events"].items()}
        def sname(s): return _db["students"].get(s, {}).get("name", s)

        ev_rows = []
        for ename, pset in event_sets.items():
            ev_rows.append({"event": ename, "participants": ", ".join(sname(s) for s in pset) or "—", "count": len(pset)})
        data_table(
            [{"name":"event","label":"Event","field":"event","align":"left"},
             {"name":"count","label":"Count","field":"count","align":"left"},
             {"name":"participants","label":"Participants","field":"participants","align":"left"}],
            ev_rows, row_key="event"
        )

        if len(event_sets) >= 2:
            section_label("Set Analysis")
            all_sets = list(event_sets.values())
            common = all_sets[0]
            for s in all_sets[1:]: common = common & s
            union = reduce(lambda a,b: a|b, all_sets)

            with ui.element("div").style("border:1px solid #1c1c1c; border-radius:4px; overflow:hidden;"):
                for lbl, pset in [("Common to all events", common), ("All unique participants", union)]:
                    with ui.element("div").style("display:flex; justify-content:space-between; padding:10px 14px; border-bottom:1px solid #1a1a1a;"):
                        ui.label(lbl).style("font-size:12px; color:#555;")
                        ui.label(", ".join(sname(s) for s in pset) or "None").style("font-size:12px; color:#e8e8e8; font-family:var(--mono);")


def bubble_sort(arr):
    a = arr[:]
    for i in range(len(a)):
        for j in range(len(a)-i-1):
            if a[j] > a[j+1]: a[j],a[j+1] = a[j+1],a[j]
    return a

def selection_sort(arr):
    a = arr[:]
    for i in range(len(a)):
        mi = i
        for j in range(i+1,len(a)):
            if a[j] < a[mi]: mi = j
        a[i],a[mi] = a[mi],a[i]
    return a

def linear_search(arr, t):
    for i,v in enumerate(arr):
        if v==t: return i
    return -1

def binary_search(arr, t):
    lo,hi = 0,len(arr)-1
    while lo<=hi:
        mid=(lo+hi)//2
        if arr[mid]==t: return mid
        elif arr[mid]<t: lo=mid+1
        else: hi=mid-1
    return -1


@ui.page("/sort")
def page_sort():
    shell("Sort & Search")
    sidebar("Sort & Search")

    with main_col():
        page_title("Sort & Search", "LAB 04 — ALGORITHMS")

        if not _db["students"]:
            ui.label("No students registered yet.").style("color:#555; font-size:13px;")
            return

        ids = [int(sid) for sid in _db["students"]]
        sorted_b = bubble_sort(ids)
        sorted_s = selection_sort(ids)

        section_label("Sort Results", margin_top=0)
        sort_rows = [
            {"algo": "Original",       "ids": "  ".join(str(x) for x in ids)},
            {"algo": "Bubble Sort",    "ids": "  ".join(str(x) for x in sorted_b)},
            {"algo": "Selection Sort", "ids": "  ".join(str(x) for x in sorted_s)},
        ]
        data_table(
            [{"name":"algo","label":"Algorithm","field":"algo","align":"left"},
             {"name":"ids","label":"ID Sequence","field":"ids","align":"left"}],
            sort_rows, row_key="algo"
        )

        section_label("Distribution")
        mn, mx = min(sorted_b), max(sorted_b)
        span = mx - mn if mx != mn else 1
        with ui.element("div").style("border:1px solid #1c1c1c; border-radius:4px; overflow:hidden;"):
            for i, sid in enumerate(sorted_b):
                name = _db["students"][str(sid)]["name"]
                pct  = int((sid - mn) / span * 100)
                border = "border-bottom:1px solid #1a1a1a;" if i < len(sorted_b)-1 else ""
                with ui.element("div").style(
                    f"display:grid; grid-template-columns:56px 1fr 140px; align-items:center; "
                    f"gap:12px; padding:8px 14px; {border}"
                ):
                    ui.label(str(sid)).style("font-family:var(--mono); font-size:12px; color:#555;")
                    with ui.element("div").style("height:2px; background:#1a1a1a; border-radius:1px; overflow:hidden;"):
                        ui.element("div").style(f"width:{max(pct,2)}%; height:100%; background:#d97706;")
                    ui.label(name).style("font-size:12px; color:#888;")

        section_label("Search")
        with ui.element("div").style("max-width:320px; display:flex; gap:10px; align-items:flex-end;"):
            search_in = ui.number("Student ID").props("outlined dark").style("flex:1;")
            result_label = ui.label("").style("font-family:var(--mono); font-size:12px; color:#555; margin-top:10px;")

        def do_search():
            if search_in.value is None: return
            target = int(search_in.value)
            li = linear_search(sorted_b, target)
            bi = binary_search(sorted_b, target)
            if li != -1:
                result_label.set_text(f"Found · Linear index {li} · Binary index {bi}")
                result_label.style("font-family:var(--mono); font-size:12px; color:#d97706; margin-top:10px;")
            else:
                result_label.set_text(f"Not found — ID {target} does not exist")
                result_label.style("font-family:var(--mono); font-size:12px; color:#dc2626; margin-top:10px;")

        with ui.element("div").style("margin-top:10px; display:flex; gap:8px; align-items:center;"):
            btn("Search", on_click=do_search)
            result_label


@ui.page("/fees")
def page_fees():
    shell("Fees")
    sidebar("Fees")

    with main_col():
        page_title("Fee Calculator", "LAB 05 — FEE MANAGEMENT")

        if not _db["students"]:
            ui.label("No students registered yet.").style("color:#555; font-size:13px;")
            return

        student_options = {sid: f"{sid} — {s['name']}" for sid,s in _db["students"].items()}

        with ui.element("div").style("max-width:440px; display:flex; flex-direction:column; gap:14px;"):
            sel = ui.select(options=student_options, label="Student").props("outlined dark").style("width:100%;")
            t_in  = ui.number("Tuition fee (₹)",   value=50000).props("outlined dark").style("width:100%;")
            h_in  = ui.number("Hostel fee (₹)",    value=0).props("outlined dark").style("width:100%;")
            tr_in = ui.number("Transport fee (₹)", value=0).props("outlined dark").style("width:100%;")

        receipt_area = ui.column().style("max-width:440px; width:100%;")

        def calc_fee():
            sid = sel.value
            if not sid: notice("Select a student.", "err"); return
            t, h, tr = t_in.value or 0, h_in.value or 0, tr_in.value or 0
            total = t + h + tr
            _db["fees"][sid] = {"tuition":t,"hostel":h,"transport":tr,"total":total}
            save_db()
            name = _db["students"][sid]["name"]
            notice(f"Fee saved for {name}", "ok")

            receipt_area.clear()
            with receipt_area:
                with ui.element("div").style(
                    "margin-top:20px; border:1px solid #1c1c1c; border-radius:4px; overflow:hidden;"
                ):
                    with ui.element("div").style("background:#141414; padding:10px 16px; border-bottom:1px solid #1c1c1c;"):
                        ui.label(f"Receipt — {name} · #{sid}").style("font-family:var(--mono); font-size:11px; color:#555; letter-spacing:0.06em;")
                    items = [("Tuition", t), ("Hostel", h), ("Transport", tr)]
                    max_amt = max(t, 1)
                    for lbl, amt in items:
                        pct = int(amt / max_amt * 100)
                        with ui.element("div").style("display:flex; align-items:center; gap:12px; padding:10px 16px; border-bottom:1px solid #1a1a1a;"):
                            ui.label(lbl).style("font-size:12px; color:#555; width:80px; flex-shrink:0;")
                            with ui.element("div").style("flex:1; height:2px; background:#1a1a1a; border-radius:1px; overflow:hidden;"):
                                ui.element("div").style(f"width:{pct}%; height:100%; background:#555;")
                            ui.label(f"₹{amt:,.0f}").style("font-family:var(--mono); font-size:12px; color:#888; width:90px; text-align:right; flex-shrink:0;")
                    with ui.element("div").style("display:flex; justify-content:space-between; padding:12px 16px;"):
                        ui.label("Total").style("font-size:13px; font-weight:600; color:#e8e8e8;")
                        ui.label(f"₹{total:,.0f}").style("font-family:var(--mono); font-size:16px; font-weight:600; color:#d97706;")

        with ui.element("div").style("margin-top:16px; margin-bottom:0;"):
            btn("Calculate & save", on_click=calc_fee)

        receipt_area

        if _db["fees"]:
            section_label("Fee History")
            fee_rows = []
            for sid, fee in _db["fees"].items():
                name = _db["students"].get(sid, {}).get("name", "?")
                fee_rows.append({
                    "id":sid,"name":name,
                    "tuition":f"₹{fee['tuition']:,.0f}",
                    "hostel":f"₹{fee['hostel']:,.0f}",
                    "transport":f"₹{fee['transport']:,.0f}",
                    "total":f"₹{fee['total']:,.0f}"
                })
            data_table(
                [{"name":"id","label":"ID","field":"id","align":"left"},
                 {"name":"name","label":"Name","field":"name","align":"left"},
                 {"name":"tuition","label":"Tuition","field":"tuition","align":"left"},
                 {"name":"hostel","label":"Hostel","field":"hostel","align":"left"},
                 {"name":"transport","label":"Transport","field":"transport","align":"left"},
                 {"name":"total","label":"Total","field":"total","align":"left"}],
                fee_rows
            )


@ui.page("/files")
def page_files():
    shell("Files")
    sidebar("Files")

    with main_col():
        page_title("Academic Records", "LAB 06 — FILE HANDLING & CSV EXPORT")

        table_area = ui.column().style("width:100%;")
        stats_area = ui.column().style("width:100%;")

        def write_and_show():
            if not _db["students"]:
                notice("No students to export.", "warn"); return
            filepath = _db["records_file"]
            with open(filepath, "w", newline="") as f:
                w = csv.writer(f)
                w.writerow(["ID","Name","Score","Grade","Remark","Total_Fee"])
                for sid, s in _db["students"].items():
                    fee = _db["fees"].get(sid, {}).get("total", 0)
                    w.writerow([sid, s["name"], s["score"], s["grade"], s["remark"], fee])

            rows, scores = [], []
            with open(filepath) as f:
                for row in csv.DictReader(f):
                    rows.append({"id":row["ID"],"name":row["Name"],"score":row["Score"],"grade":row["Grade"],"remark":row["Remark"],"fee":f"₹{float(row['Total_Fee']):,.0f}"})
                    scores.append(float(row["Score"]))

            notice(f"Exported → {filepath}", "ok")
            table_area.clear(); stats_area.clear()

            with table_area:
                section_label("Exported Records")
                data_table(
                    [{"name":"id","label":"ID","field":"id","align":"left"},
                     {"name":"name","label":"Name","field":"name","align":"left"},
                     {"name":"score","label":"Score","field":"score","align":"left"},
                     {"name":"grade","label":"Grade","field":"grade","align":"left"},
                     {"name":"remark","label":"Remark","field":"remark","align":"left"},
                     {"name":"fee","label":"Total Fee","field":"fee","align":"left"}],
                    rows
                )

            with stats_area:
                if scores:
                    avg = sum(scores)/len(scores)
                    top = max(rows, key=lambda r: float(r["score"]))
                    gc  = Counter(r["grade"] for r in rows)
                    section_label("Summary")
                    stat_row([
                        ("Students",      len(rows),    "#e8e8e8"),
                        ("Avg Score",     f"{avg:.1f}", "#e8e8e8"),
                        ("Top Performer", top["name"],  "#d97706"),
                    ])

        with ui.element("div").style("margin-bottom:8px;"):
            ui.label("Writes all student records to student_records.csv.").style("font-size:13px; color:#555; margin-bottom:16px; display:block;")
            btn("Export CSV", on_click=write_and_show)

        table_area
        stats_area


def build_tree(path, prefix="", is_last=True):
    connector = "└── " if is_last else "├── "
    name = os.path.basename(path) or path
    entries = [(prefix + connector, name, os.path.isdir(path))]
    if os.path.isdir(path):
        try:
            children = sorted(os.listdir(path))
        except PermissionError:
            return entries
        sub = prefix + ("    " if is_last else "│   ")
        for i, child in enumerate(children):
            entries += build_tree(os.path.join(path, child), sub, i==len(children)-1)
    return entries


@ui.page("/directory")
def page_directory():
    shell("Directory")
    sidebar("Directory")

    with main_col():
        page_title("Directory Scanner", "LAB 07 — FILE SYSTEM EXPLORER")

        with ui.element("div").style("max-width:440px; display:flex; gap:10px; align-items:flex-end; margin-bottom:16px;"):
            path_in = ui.input("Path", value=".").props("outlined dark").style("flex:1;")
            btn("Scan", on_click=lambda: do_scan())

        tree_area = ui.column().style("width:100%;")

        def do_scan():
            target = (path_in.value or ".").strip()
            tree_area.clear()
            with tree_area:
                if not os.path.exists(target):
                    ui.label(f"Path not found: {target}").style("font-family:var(--mono); font-size:12px; color:#dc2626;")
                    return
                try:
                    entries = build_tree(target)
                    tf = sum(len(files) for _,_,files in os.walk(target))
                    td = sum(len(dirs)  for _,dirs,_ in os.walk(target))

                    section_label("Tree")
                    with ui.element("div").style(
                        "border:1px solid #1c1c1c; border-radius:4px; overflow:hidden; "
                        "background:#0d0d0d; padding:14px 16px; overflow-x:auto;"
                    ):
                        for indent, name, is_dir in entries:
                            col = "#888" if is_dir else "#555"
                            ui.label(indent + name).style(
                                f"font-family:var(--mono); font-size:12px; color:{col}; "
                                "white-space:pre; display:block; line-height:1.8;"
                            )
                    stat_row([("Directories", td, "#e8e8e8"), ("Files", tf, "#e8e8e8")])
                except Exception as e:
                    ui.label(f"Error: {e}").style("font-family:var(--mono); font-size:12px; color:#dc2626;")

        tree_area


@ui.page("/analytics")
def page_analytics():
    shell("Analytics")
    sidebar("Analytics")

    with main_col():
        page_title("Performance Analytics", "LAB 08 — SUBJECT-WISE ANALYSIS")

        if not _db["students"]:
            ui.label("No students registered yet.").style("color:#555; font-size:13px;")
            return

        subjects = ["Math", "Science", "English"]

        student_data = []
        for sid, s in _db["students"].items():
            base = s["score"]
            row = {"name": s["name"], "sid": sid}
            for subj in subjects:
                row[subj] = max(0, min(100, base + random.randint(-8, 8)))
            student_data.append(row)

        section_label("Subject Averages", margin_top=0)
        avgs = {subj: sum(r[subj] for r in student_data)/len(student_data) for subj in subjects}
        tops = {subj: max(student_data, key=lambda r: r[subj])["name"] for subj in subjects}

        stat_row([(subj, f"{avgs[subj]:.1f}", "#e8e8e8") for subj in subjects])

        with ui.element("div").style("border:1px solid #1c1c1c; border-radius:4px; overflow:hidden; margin-bottom:24px;"):
            for i, subj in enumerate(subjects):
                border = "border-bottom:1px solid #1a1a1a;" if i < len(subjects)-1 else ""
                with ui.element("div").style(f"display:flex; justify-content:space-between; padding:9px 14px; {border}"):
                    ui.label(f"Top in {subj}").style("font-size:12px; color:#555;")
                    ui.label(tops[subj]).style("font-family:var(--mono); font-size:12px; color:#d97706;")

        section_label("Raw Data")
        rows_t = [{"name": r["name"], **{s: r[s] for s in subjects}} for r in student_data]
        data_table(
            [{"name":"name","label":"Name","field":"name","align":"left"}] +
            [{"name":s,"label":s,"field":s,"align":"left"} for s in subjects],
            rows_t, row_key="name"
        )

        section_label("Score Comparison")
        with ui.element("div").style("border:1px solid #1c1c1c; border-radius:4px; overflow:hidden;"):
            with ui.element("div").style(
                "display:grid; grid-template-columns:140px repeat(3, 1fr); gap:0; "
                "background:#141414; padding:8px 14px; border-bottom:1px solid #1c1c1c;"
            ):
                ui.label("Student").style("font-family:var(--mono); font-size:10px; color:#444; text-transform:uppercase; letter-spacing:0.08em;")
                for s in subjects:
                    ui.label(s).style("font-family:var(--mono); font-size:10px; color:#444; text-transform:uppercase; letter-spacing:0.08em;")

            for i, r in enumerate(student_data):
                border = "border-bottom:1px solid #1a1a1a;" if i < len(student_data)-1 else ""
                with ui.element("div").style(
                    f"display:grid; grid-template-columns:140px repeat(3, 1fr); "
                    f"gap:0; align-items:center; padding:10px 14px; {border}"
                ):
                    ui.label(r["name"]).style("font-size:12px; color:#888;")
                    for j, subj in enumerate(subjects):
                        val = r[subj]
                        with ui.element("div").style("display:flex; align-items:center; gap:8px; padding-right:12px;"):
                            with ui.element("div").style("flex:1; height:2px; background:#1a1a1a; border-radius:1px; overflow:hidden;"):
                                bar_col = "#d97706" if val >= 75 else "#333"
                                ui.element("div").style(f"width:{val}%; height:100%; background:{bar_col};")
                            ui.label(str(val)).style("font-family:var(--mono); font-size:11px; color:#555; width:26px; text-align:right; flex-shrink:0;")


# ── RUN ───────────────
ui.run(title="SCIS", host="0.0.0.0", port=8080, dark=True, reload=False, favicon="🎓")