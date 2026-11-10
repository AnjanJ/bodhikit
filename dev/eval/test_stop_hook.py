#!/usr/bin/env python3
"""Deterministic tests for scripts/bodhi-stop-hook.py (1.18.0). Same
conventions as test_bodhi_state.py: black-box subprocess runs, asserting on
what the hook prints. Run by dev/check.sh."""

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import shutil
import time

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
# Pin the script's clock to this suite's (the hook spawns bodhi-state).
os.environ["BODHI_TODAY"] = __import__("datetime").date.today().isoformat()

HOOK = os.path.join(REPO, "scripts", "bodhi-stop-hook.py")
PASS = 0
FAIL = 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"ok    {name}")
    else:
        FAIL += 1
        print(f"FAIL  {name}  {detail}")


def run_hook(payload, env=None):
    """HOME is sandboxed by default so the contributor's real ~/.bodhikit
    config and learning projects never leak into a test."""
    if env is None:
        env = os.environ.copy()
        env["HOME"] = tempfile.mkdtemp(prefix="bodhi-hook-home-")
    r = subprocess.run([sys.executable, HOOK], input=json.dumps(payload),
                       capture_output=True, text=True, timeout=60, env=env)
    assert r.returncode == 0, f"hook must always exit 0: {r.stderr}"
    return r.stdout.strip()


def make_project(root, name, sr=None):
    proj = os.path.join(root, "learningWithBodhi", name)
    os.makedirs(os.path.join(proj, ".bodhi"))
    with open(os.path.join(proj, ".bodhi", "state.json"), "w") as f:
        json.dump({"version": 2, "projectName": name, "sessionDates": []}, f)
    with open(os.path.join(proj, ".bodhi", "spaced-review.json"), "w") as f:
        json.dump(sr or {"version": 3, "concepts": [], "sessionHistory": []}, f)
    return proj


BROKEN_SR = {"version": 3, "sessionHistory": [], "concepts": [
    {"name": "Joins", "module": "A", "box": "three", "bloomLevel": 0,
     "feynmanPassed": False, "consecutiveCorrectAtL4Plus": 0,
     "reviewHistory": [], "nextReview": "2026-01-01"}]}


def t_block_on_broken():
    with tempfile.TemporaryDirectory() as root:
        proj = make_project(root, "sql", BROKEN_SR)
        out = run_hook({"cwd": root, "hook_event_name": "Stop"})
        check("hook: broken project blocks the stop", out.startswith("{"), out[:80])
        d = json.loads(out) if out else {}
        check("hook: decision is block", d.get("decision") == "block", d)
        check("hook: reason names the project and the field",
              proj in d.get("reason", "") and "box" in d.get("reason", ""), d)
        # a clean project does not block
        with open(os.path.join(proj, ".bodhi", "spaced-review.json"), "w") as f:
            json.dump({"version": 3, "concepts": [], "sessionHistory": []}, f)
        out = run_hook({"cwd": root})
        check("hook: clean project is silent", out == "", out)


def t_reentry_and_stale():
    with tempfile.TemporaryDirectory() as root:
        proj = make_project(root, "sql", BROKEN_SR)
        out = run_hook({"cwd": root, "stop_hook_active": True})
        check("hook: stop_hook_active short-circuits", out == "", out)
        old = time.time() - 8 * 3600
        for name in os.listdir(os.path.join(proj, ".bodhi")):
            os.utime(os.path.join(proj, ".bodhi", name), (old, old))
        out = run_hook({"cwd": root})
        check("hook: a project untouched for 8h is not verified", out == "", out)


def t_configured_roots():
    """A per-repo .bodhikit/config.json projectRoot is verified; the global
    ~/.bodhikit/config.json searchPaths are NOT (a project studied in another
    terminal must not block this session's stop)."""
    with tempfile.TemporaryDirectory() as root:
        home = os.path.join(root, "home")
        elsewhere = os.path.join(root, "elsewhere")
        cwd = os.path.join(root, "repo")
        os.makedirs(os.path.join(home, ".bodhikit"))
        os.makedirs(cwd)
        proj = make_project(elsewhere, "sql", BROKEN_SR)
        with open(os.path.join(home, ".bodhikit", "config.json"), "w") as f:
            json.dump({"searchPaths": ["$PWD", elsewhere]}, f)
        env = os.environ.copy()
        env["HOME"] = home
        out = run_hook({"cwd": cwd}, env=env)
        check("hook: global searchPaths are not walked (session-scoped)",
              out == "", out[:120])
        # per-repo projectRoot
        os.makedirs(os.path.join(cwd, ".bodhikit"))
        with open(os.path.join(cwd, ".bodhikit", "config.json"), "w") as f:
            json.dump({"projectRoot": os.path.join(root, "study")}, f)
        proj2 = make_project(os.path.join(root, "study"), "rust", BROKEN_SR)
        out = run_hook({"cwd": os.path.join(cwd)}, env={**env, "HOME": os.path.join(root, "nohome")})
        check("hook: per-repo projectRoot is verified",
              proj2 in (json.loads(out).get("reason", "") if out else ""), out[:120])


def t_bounded_search():
    """A wide, deep tree with no projects must finish inside the budget."""
    with tempfile.TemporaryDirectory() as root:
        for a in range(12):
            for b in range(12):
                for c in range(6):
                    os.makedirs(os.path.join(root, f"a{a}", f"b{b}", f"c{c}", "d", "e"))
        # a project below MAX_DEPTH is ignored; one at depth 2 is found
        make_project(os.path.join(root, "a0", "b0", "c0", "d"), "deep", BROKEN_SR)
        proj = make_project(root, "shallow", BROKEN_SR)
        t0 = time.monotonic()
        out = run_hook({"cwd": root})
        elapsed = time.monotonic() - t0
        check("hook: bounded search finishes quickly", elapsed < 15, f"{elapsed:.1f}s")
        reason = json.loads(out).get("reason", "") if out else ""
        check("hook: shallow project found", proj in reason, reason[:120])
        check("hook: project beyond MAX_DEPTH not walked", "deep" not in reason)


def t_failure_reasons():
    spec = importlib.util.spec_from_file_location("hook", HOOK)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    check("reasons: verify errors list",
          mod.failure_reasons('{"ok": false, "errors": ["a", "b"]}', "") == ["a", "b"])
    check("reasons: die error field",
          mod.failure_reasons('{"ok": false, "error": "boom"}', "") == ["boom"])
    check("reasons: traceback falls back to last stderr line",
          mod.failure_reasons("", "Traceback...\nKeyError: 'name'\n") == ["KeyError: 'name'"])
    check("reasons: never blank",
          mod.failure_reasons("", "") == ["verify failed without output"])



def write_transcript(root, commands, cwd):
    """A minimal session transcript: one Bash tool_use per command."""
    path = os.path.join(root, "transcript.jsonl")
    with open(path, "w") as f:
        for cmd in commands:
            f.write(json.dumps({"type": "assistant", "cwd": cwd, "message": {"content": [
                {"type": "tool_use", "name": "Bash", "input": {"command": cmd}}]}}) + "\n")
    return path


def t_revision_sheet_required():
    """A project THIS SESSION closed (transcript shows touch-state) must have
    today's revision sheet before the session can stop (1.18.1: scoped by
    transcript — the Stop event fires every turn, and other sessions may
    have studied the same project today)."""
    import datetime
    today = datetime.date.today().isoformat()
    with tempfile.TemporaryDirectory() as root:
        studied = {"version": 3, "sessionHistory": [], "concepts": [
            {"name": "Joins", "module": "A", "box": 2, "bloomLevel": 3,
             "feynmanPassed": False, "consecutiveCorrectAtL4Plus": 0,
             "nextReview": today, "lastReviewed": today,
             "reviewHistory": [{"date": today, "result": "correct",
                                "bloomLevel": 3, "source": "teach"}]}]}
        proj = make_project(root, "sql", studied)
        # no transcript: another session's study is never this one's to write
        out = run_hook({"cwd": root})
        check("sheet: without a transcript the stop is silent", out == "", out[:120])
        # this session only recorded a review (mid-session): not yet
        tp = write_transcript(root, [f'"$R/scripts/bodhi-state" --project "{proj}" record-review --concept Joins --result correct --tested-bloom 3'], root)
        out = run_hook({"cwd": root, "transcript_path": tp})
        check("sheet: a review without touch-state does not block (mid-session)", out == "", out[:120])
        # another project's closing write: not this project's sheet
        tp = write_transcript(root, [f'"$R/scripts/bodhi-state" --project "{os.path.join(root, "learningWithBodhi", "other")}" touch-state --activity x'], root)
        out = run_hook({"cwd": root, "transcript_path": tp})
        check("sheet: touch-state on another project does not block this one", out == "", out[:120])
        # this session closed this project (relative --project resolved against cwd)
        tp = write_transcript(root, ['"$R/scripts/bodhi-state" --project learningWithBodhi/sql touch-state --activity "done"'], root)
        out = run_hook({"cwd": root, "transcript_path": tp})
        d = json.loads(out) if out else {}
        check("sheet: this session's touch-state + no sheet blocks the stop",
              d.get("decision") == "block" and "revision sheet" in d.get("reason", ""), out[:120])
        check("sheet: reason names the file and the concept",
              f"revision/{today}-joins.md" in d.get("reason", "") and "Joins" in d.get("reason", ""), d)
        # argparse also accepts --project=<path>; a skill that uses it must
        # not escape the sheet requirement (1.18.x: the regex matched only
        # the space-separated form)
        for form in (f'--project={proj}', f'--project="{proj}"', f"--project='{proj}'"):
            tp = write_transcript(root, [f'"$R/scripts/bodhi-state" {form} touch-state --activity x'], root)
            out = run_hook({"cwd": root, "transcript_path": tp})
            d = json.loads(out) if out else {}
            check(f"sheet: the {form.split('=')[0]}= form is detected ({form[10:12]}…)",
                  d.get("decision") == "block" and "revision sheet" in d.get("reason", ""), out[:120])
        os.makedirs(os.path.join(proj, "revision"))
        with open(os.path.join(proj, "revision", f"{today}-joins.md"), "w") as f:
            f.write("# Revision — Joins\n")
        out = run_hook({"cwd": root, "transcript_path": tp})
        check("sheet: with today's sheet the stop is silent", out == "", out)
        # nothing studied today (old review only): no sheet required
        studied["concepts"][0]["reviewHistory"][0]["date"] = "2026-01-01"
        proj2 = make_project(root, "rust", studied)
        os.utime(os.path.join(proj2, ".bodhi", "state.json"), None)
        tp = write_transcript(root, [f'"$R/scripts/bodhi-state" --project "{proj2}" touch-state --activity x'], root)
        out = run_hook({"cwd": os.path.join(root, "learningWithBodhi", "rust"), "transcript_path": tp})
        check("sheet: a project with no study today needs no sheet", out == "", out)

def t_touched_outside_cwd():
    """learn-anything/REQ-38: a cloud chat's working folder is /home/claude,
    and the learner's project is a copy staged elsewhere (/mnt/user-data/...).
    A project this session closed is checked wherever it is; one it never
    closed is not, and a project under cwd keeps its reason word for word."""
    import datetime
    today = datetime.date.today().isoformat()
    studied = {"version": 3, "sessionHistory": [], "concepts": [
        {"name": "Joins", "module": "A", "box": 2, "bloomLevel": 3,
         "feynmanPassed": False, "consecutiveCorrectAtL4Plus": 0,
         "nextReview": today, "lastReviewed": today,
         "reviewHistory": [{"date": today, "result": "correct",
                            "bloomLevel": 3, "source": "quiz"}]}]}
    copy_note = "bring that folder's `revision/` over"
    with tempfile.TemporaryDirectory() as root:
        cwd = os.path.join(root, "home", "claude")
        os.makedirs(cwd)
        staged = make_project(os.path.join(root, "mnt", "user-data", "uploads"), "sql", studied)
        out = run_hook({"cwd": cwd})
        check("outside: without a transcript a staged copy is silent", out == "", out[:120])
        tp = write_transcript(root, [f'"$R/scripts/bodhi-state" --project "{staged}" record-review --concept Joins --result correct'], cwd)
        out = run_hook({"cwd": cwd, "transcript_path": tp})
        check("outside: a copy the session never closed is silent", out == "", out[:120])
        tp = write_transcript(root, [f'"$R/scripts/bodhi-state" --project "{staged}" touch-state --activity probe'], cwd)
        out = run_hook({"cwd": cwd, "transcript_path": tp})
        d = json.loads(out) if out else {}
        reason = d.get("reason", "")
        check("outside: a copy this session closed blocks without today's sheet",
              d.get("decision") == "block" and f"{staged}: write revision/{today}-joins.md" in reason, out[:160])
        check("outside: the reason says to bring the learner's revision/ over", copy_note in reason, reason[-300:])
        os.makedirs(os.path.join(staged, "revision"))
        with open(os.path.join(staged, "revision", f"{today}-joins.md"), "w") as f:
            f.write("# Revision — Joins\n")
        out = run_hook({"cwd": cwd, "transcript_path": tp})
        check("outside: with today's sheet in the copy the stop is silent", out == "", out[:120])
        broken = make_project(os.path.join(root, "mnt", "user-data", "outputs"), "rust", BROKEN_SR)
        tp = write_transcript(root, [f'"$R/scripts/bodhi-state" --project "{broken}" touch-state --activity probe'], cwd)
        out = run_hook({"cwd": cwd, "transcript_path": tp})
        d = json.loads(out) if out else {}
        check("outside: a broken copy this session closed fails verify",
              d.get("decision") == "block" and broken in d.get("reason", "") and "schema verification" in d.get("reason", ""), out[:160])
    with tempfile.TemporaryDirectory() as root:
        proj = make_project(root, "sql", studied)
        tp = write_transcript(root, [f'"$R/scripts/bodhi-state" --project "{proj}" touch-state --activity done'], root)
        out = run_hook({"cwd": root, "transcript_path": tp})
        reason = json.loads(out).get("reason", "") if out else ""
        expected = (
            "This session studied a project and has not written today's revision sheet:\n"
            f"{proj}: write revision/{today}-joins.md  (studied today: Joins)\n"
            "Write it now from this session, following "
            "skills/reflect/references/revision-sheet.md in the BodhiKit plugin "
            "(run `bodhi-state --project <project> revision-brief` for the "
            "concepts, results and next-review dates; outcome clauses, the worked "
            "example, where the learner slipped, two self-test prompts with "
            "answers, next reviews, free links only from .bodhi/resources.md or "
            "official docs). Then stop.")
        check("outside: a project under cwd keeps its reason word for word", reason == expected, reason)


def t_shell_variables():
    """learn-anything/REQ-38, from the 2026-10-22 rerun: the cloud chat set a
    shell variable and passed `--project $S/sql-deep-dive` in the same
    command, so the transcript never names the path outright."""
    import datetime
    today = datetime.date.today().isoformat()
    studied = {"version": 3, "sessionHistory": [], "concepts": [
        {"name": "Joins", "module": "A", "box": 2, "bloomLevel": 3,
         "feynmanPassed": False, "consecutiveCorrectAtL4Plus": 0,
         "nextReview": today, "lastReviewed": today,
         "reviewHistory": [{"date": today, "result": "correct",
                            "bloomLevel": 3, "source": "quiz"}]}]}
    with tempfile.TemporaryDirectory() as root:
        cwd = os.path.join(root, "home", "claude")
        os.makedirs(cwd)
        scratch = os.path.join(root, "tmp", "scratchpad", "probe2")
        proj = make_project(scratch, "sql", studied)
        rel = os.path.relpath(proj, scratch)
        live = (f"S={scratch}; rm -rf $S; mkdir -p $S/{rel} && "
                f"cp -a /mnt/user-data/uploads/learningWithBodhi/sql/.bodhi $S/{rel}/ && "
                f'"$R/scripts/bodhi-state" --project $S/{rel} touch-state --activity probe; '
                'echo "exit=$?"; mkdir -p /mnt/user-data/outputs')
        for label, cmd in (
                ("the live command", live),
                ("${S} in quotes", f'export S="{scratch}" && "$R/scripts/bodhi-state" --project "${{S}}/{rel}" touch-state --activity x'),
        ):
            tp = write_transcript(root, [cmd], cwd)
            out = run_hook({"cwd": cwd, "transcript_path": tp})
            d = json.loads(out) if out else {}
            check(f"variables: {label} names the project",
                  d.get("decision") == "block" and proj in d.get("reason", ""), out[:160])
        tp = write_transcript(root, [f'"$R/scripts/bodhi-state" --project $UNSET/{rel} touch-state --activity x'], cwd)
        out = run_hook({"cwd": cwd, "transcript_path": tp})
        check("variables: an unassigned variable names nothing", out == "", out[:120])


# --- The learning vault (spec learning-vault) ---------------------------------

TODAY = os.environ["BODHI_TODAY"]
STATE = os.path.join(REPO, "scripts", "bodhi-state")
NO_CLOUD = os.path.join(tempfile.gettempdir(), "bodhi-no-cloud-marker")


def vault_env(cloud=None):
    env = os.environ.copy()
    env["HOME"] = tempfile.mkdtemp(prefix="bodhi-hook-home-")
    env["BODHI_CLOUD_MARKER"] = cloud or NO_CLOUD
    return env


def learner_with_course(root, name="sql", studied=True, sheet=True):
    """root/learningWithBodhi with a profile, its projects list and one
    course; with `studied`, a review dated today, and with `sheet`, today's
    revision sheet, so a session that ran touch-state can close."""
    lwb = os.path.join(root, "learningWithBodhi")
    os.makedirs(lwb, exist_ok=True)
    if not os.path.exists(os.path.join(lwb, ".bodhi-profile.json")):
        with open(os.path.join(lwb, ".bodhi-profile.json"), "w") as f:
            json.dump({"version": 2, "cumulativeStats": {}}, f)
    lp = os.path.join(lwb, ".bodhi-profile.projects.json")
    lists = {"version": 2, "activeProjects": [], "completedProjects": []}
    if os.path.exists(lp):
        with open(lp) as f:
            lists = json.load(f)
    lists["activeProjects"].append({"name": name, "topic": name, "startedAt": TODAY,
                                    "currentPhase": "1", "currentModule": "A",
                                    "bloomLevel": 1, "pace": "steady", "status": "active",
                                    "trackPurpose": "test"})
    with open(lp, "w") as f:
        json.dump(lists, f)
    review = [{"date": TODAY, "result": "correct", "bloomLevel": 3, "source": "teach"}]
    proj = make_project(root, name, {"version": 3, "sessionHistory": [], "concepts": [
        {"name": "Joins", "module": "A", "box": 2, "bloomLevel": 3,
         "feynmanPassed": False, "consecutiveCorrectAtL4Plus": 0,
         "nextReview": TODAY, "lastReviewed": TODAY,
         "reviewHistory": review if studied else []}]})
    if sheet:
        os.makedirs(os.path.join(proj, "revision"))
        with open(os.path.join(proj, "revision", f"{TODAY}-joins.md"), "w") as f:
            f.write("# Revision — Joins\n")
    return lwb, proj


def notes_of(lwb):
    p = os.path.join(lwb, ".bodhi-notes.json")
    if not os.path.exists(p):
        return None
    with open(p) as f:
        return json.load(f)


def state_cmd(proj, *argv, env=None):
    r = subprocess.run([sys.executable, STATE, "--project", proj, *argv],
                       capture_output=True, text=True, env=env)
    assert r.returncode == 0, r.stdout + r.stderr
    return json.loads(r.stdout)


def write_session(root, cwd, commands=(), typed=None, skill=None):
    """A transcript: an optional typed command, an optional Skill call, then
    one Bash tool_use per command."""
    path = os.path.join(root, "transcript.jsonl")
    with open(path, "w") as f:
        if typed:
            f.write(json.dumps({"type": "user", "cwd": cwd, "message": {
                "role": "user", "content": f"<command-message>{typed}</command-message>\n"
                f"<command-name>/{typed}</command-name>\n<command-args></command-args>"}}) + "\n")
        if skill:
            f.write(json.dumps({"type": "assistant", "cwd": cwd, "message": {"content": [
                {"type": "tool_use", "name": "Skill", "input": {"skill": skill}}]}}) + "\n")
        for cmd in commands:
            f.write(json.dumps({"type": "assistant", "cwd": cwd, "message": {"content": [
                {"type": "tool_use", "name": "Bash", "input": {"command": cmd}}]}}) + "\n")
    return path


def touch(proj):
    return f'"$R/scripts/bodhi-state" --project "{proj}" touch-state --activity x'


def system_message(out):
    d = json.loads(out) if out else {}
    return d.get("systemMessage", ""), d


def internal_name(text):
    sys.path.insert(0, os.path.join(REPO, "dev", "eval"))
    import assert_scenario
    m = assert_scenario.INTERNAL_NAME_RE.search(text)
    return m.group(1) if m else None


def t_no_notes_file_same_as_before():
    """learning-vault/REQ-7: with no notes file and no offer moment, the hook
    prints what it printed before and writes nothing new."""
    with tempfile.TemporaryDirectory() as root:
        lwb, proj = learner_with_course(root)
        before = sorted(os.listdir(proj)) + sorted(os.listdir(lwb))
        tp = write_session(root, root, [touch(proj)])
        out = run_hook({"cwd": root, "transcript_path": tp}, env=vault_env())
        check("no notes: a closed session stops silently", out == "", out[:200])
        check("no notes: no new file", sorted(os.listdir(proj)) + sorted(os.listdir(lwb))
              == before, os.listdir(proj))
        out = run_hook({"cwd": root, "transcript_path": tp, "stop_hook_active": True},
                       env=vault_env())
        check("no notes: the re-entry stop is silent too", out == "", out[:200])


def t_offer_after_learn():
    """learning-vault/REQ-8, learning-vault/REQ-10: the turn that registered a new course and
    gave its first step ends with the offer once, through systemMessage,
    never a block; the offer is recorded and not made again."""
    with tempfile.TemporaryDirectory() as root:
        lwb, proj = learner_with_course(root, studied=False, sheet=False)
        cmds = [f'"$R/scripts/bodhi-state" --project "{proj}" profile-add-project '
                f'--name sql --topic SQL --bloom 1 --pace steady --track-purpose x', touch(proj)]
        tp = write_session(root, root, cmds)
        out = run_hook({"cwd": root, "transcript_path": tp}, env=vault_env())
        msg, d = system_message(out)
        check("offer after /learn: made, naming the command", "/bodhikit:notes-setup" in msg, out)
        check("offer after /learn: never a block", "decision" not in d, d)
        check("offer after /learn: a statement, not a question", "?" not in msg, msg)
        check("offer after /learn: no engine names", internal_name(msg) is None,
              internal_name(msg))
        check("offer after /learn: recorded", (notes_of(lwb) or {}).get("offerMadeOn") == TODAY,
              notes_of(lwb))
        out = run_hook({"cwd": root, "transcript_path": tp}, env=vault_env())
        check("offer after /learn: not made twice", "notes-setup" not in out, out)


def t_offer_after_continue():
    """learning-vault/REQ-9: a session begun with /continue that reaches
    session close ends with the offer, whether /continue was typed or
    called through the Skill tool; not before the sheet exists."""
    for label, kw in (("typed", {"typed": "bodhikit:continue"}),
                      ("Skill call", {"skill": "bodhikit:continue"})):
        with tempfile.TemporaryDirectory() as root:
            lwb, proj = learner_with_course(root, sheet=False)
            tp = write_session(root, root, [touch(proj)], **kw)
            out = run_hook({"cwd": root, "transcript_path": tp}, env=vault_env())
            d = json.loads(out) if out else {}
            check(f"offer after /continue ({label}): no offer while the sheet is owed",
                  d.get("decision") == "block" and "notes-setup" not in out
                  and notes_of(lwb) is None, out[:200])
            os.makedirs(os.path.join(proj, "revision"))
            with open(os.path.join(proj, "revision", f"{TODAY}-joins.md"), "w") as f:
                f.write("# Revision — Joins\n")
            out = run_hook({"cwd": root, "transcript_path": tp}, env=vault_env())
            msg, d = system_message(out)
            check(f"offer after /continue ({label}): made at session close",
                  "/bodhikit:notes-setup" in msg and "decision" not in d, out)
    with tempfile.TemporaryDirectory() as root:
        lwb, proj = learner_with_course(root)
        tp = write_session(root, root, [touch(proj)], typed="bodhikit:quiz")
        out = run_hook({"cwd": root, "transcript_path": tp}, env=vault_env())
        check("no offer after a session begun with another command", out == "", out)


def t_offer_not_with_a_choice():
    """learning-vault/REQ-8, learning-vault/REQ-9: a learner who already chose (here: files
    only) is not offered, even with no offer on record."""
    with tempfile.TemporaryDirectory() as root:
        lwb, proj = learner_with_course(root)
        state_cmd(proj, "notes-set", "--choice", "files", env=vault_env())
        tp = write_session(root, root, [touch(proj)], typed="bodhikit:continue")
        out = run_hook({"cwd": root, "transcript_path": tp}, env=vault_env())
        check("a learner with a choice is not offered", "notes-setup" not in out, out)
        check("files only: the session close writes Syllabus.md",
              os.path.exists(os.path.join(proj, "Syllabus.md")))


def t_no_offer_in_cloud_chat():
    """learning-vault/REQ-38: in a cloud chat sprint 1 makes no offer and
    writes nothing."""
    with tempfile.TemporaryDirectory() as root, tempfile.TemporaryDirectory() as marker:
        lwb, proj = learner_with_course(root)
        tp = write_session(root, root, [touch(proj)], typed="bodhikit:continue")
        out = run_hook({"cwd": root, "transcript_path": tp}, env=vault_env(cloud=marker))
        check("cloud chat: no offer", out == "", out)
        check("cloud chat: nothing recorded", notes_of(lwb) is None)


NOTES_WORDS = ("notes-setup", "notes-sync", "notes-set", "notes-show", "notes-offered",
               ".bodhi-notes.json", "Syllabus.md", "Learn with Bodhi")


def t_existing_skills_unchanged():
    """learning-vault/REQ-11: the offer and the session-close writes reach the
    learner with no change to the text of any existing SKILL.md: no skill but
    /notes-setup names the feature. (A byte comparison with a release would
    also catch unrelated edits, such as another spec's.)"""
    r = subprocess.run(["git", "-C", REPO, "ls-tree", "-r", "--name-only", "v1.26.1",
                        "skills/"], capture_output=True, text=True)
    names = [n for n in r.stdout.split() if n.endswith("/SKILL.md")]
    check("the skills of release 1.26.1 are listed from git", r.returncode == 0
          and len(names) > 30, r.stderr[-200:])
    named = []
    for n in names:
        with open(os.path.join(REPO, n), encoding="utf-8") as f:
            text = f.read()
        named += [f"{n}: {w}" for w in NOTES_WORDS if w in text]
    check("no SKILL.md that 1.26.1 shipped names the notes feature", not named, named)


def t_copy_failure_reported():
    """learning-vault/REQ-26: when the copy cannot be written the session still
    closes (exit 0, no block) and the learner is told it did not happen and
    why."""
    with tempfile.TemporaryDirectory() as root:
        lwb, proj = learner_with_course(root)
        vault = os.path.join(root, "vault")
        os.makedirs(vault)
        state_cmd(proj, "notes-set", "--choice", "vault", "--app", "obsidian",
                  "--location", vault, env=vault_env())
        shutil.rmtree(vault)
        tp = write_session(root, root, [touch(proj)])
        out = run_hook({"cwd": root, "transcript_path": tp}, env=vault_env())
        msg, d = system_message(out)
        check("copy failure: the stop is not blocked", "decision" not in d, d)
        check("copy failure: the learner is told, with the reason",
              "could not copy" in msg and "not there" in msg, msg)
        check("copy failure: no engine names", internal_name(msg) is None, internal_name(msg))


def t_saved_only_after_success():
    """learning-vault/REQ-27: a course's first arrival in the vault is
    announced only after it was written; a failed copy announces nothing."""
    with tempfile.TemporaryDirectory() as root:
        lwb, proj = learner_with_course(root)
        vault = os.path.join(root, "vault")
        os.makedirs(vault)
        state_cmd(proj, "notes-set", "--choice", "vault", "--app", "obsidian",
                  "--location", vault, env=vault_env())
        _, proj2 = learner_with_course(root, name="chess")
        tp = write_session(root, root, [touch(proj2)])
        out = run_hook({"cwd": root, "transcript_path": tp}, env=vault_env())
        msg, _ = system_message(out)
        check("first arrival: announced once written",
              "chess" in msg and "now in" in msg and os.path.exists(
                  os.path.join(vault, "Learn with Bodhi", "chess", "Syllabus.md")), out)
        out = run_hook({"cwd": root, "transcript_path": tp}, env=vault_env())
        check("first arrival: not announced again", out == "", out)
        _, proj3 = learner_with_course(root, name="art")
        shutil.rmtree(vault)
        tp = write_session(root, root, [touch(proj3)])
        out = run_hook({"cwd": root, "transcript_path": tp}, env=vault_env())
        msg, _ = system_message(out)
        check("failed copy: nothing announced as saved", "now in" not in msg, msg)


def main():
    for t in (t_block_on_broken, t_reentry_and_stale, t_configured_roots,
              t_bounded_search, t_failure_reasons, t_revision_sheet_required,
              t_touched_outside_cwd, t_shell_variables,
              t_no_notes_file_same_as_before, t_offer_after_learn, t_offer_after_continue,
              t_offer_not_with_a_choice, t_no_offer_in_cloud_chat, t_existing_skills_unchanged,
              t_copy_failure_reported, t_saved_only_after_success):
        t()
    print(f"\n{PASS} passed, {FAIL} failed")
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
