#!/usr/bin/env python3
"""Deterministic tests for scripts/bodhi-state.

Run: python3 dev/eval/test_bodhi_state.py
Exit 0 = all pass. Part of the pre-tag checklist (and dev/check.sh).

These tests cover the contracts the 1.10.x dogfood passes caught executors
violating: unknown-field preservation, Leitner math, the bloomLevel ratchet,
the counter reset rules, sessionHistory vocabulary, migration idempotency
with backup, and the gate verdict logic (including the 1.11.0 recency rule).
"""

import datetime
import json
import os
import shutil
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPT = os.path.join(REPO, "scripts", "bodhi-state")
TODAY = datetime.date.today()
# Pin the script's clock to the suite's: the 12 s run used to race midnight
# against its own date.today(). Individual tests override this per call for
# date travel (see t_date_travel).
os.environ["BODHI_TODAY"] = TODAY.isoformat()

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


def run(project, *argv, expect_fail=False, on=None):
    """`on` = an ISO date to run the command as if it were that day."""
    env = dict(os.environ, BODHI_TODAY=on) if on else None
    r = subprocess.run([sys.executable, SCRIPT, "--project", project, *argv],
                       capture_output=True, text=True, env=env)
    if not expect_fail and r.returncode != 0:
        raise AssertionError(f"bodhi-state {' '.join(argv)} failed:\n{r.stdout}\n{r.stderr}")
    if expect_fail and r.returncode == 0:
        raise AssertionError(f"bodhi-state {' '.join(argv)} unexpectedly succeeded")
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        return {"_raw": r.stdout}


def make_project(root, spaced_review=None, state=None):
    proj = os.path.join(root, "proj")
    os.makedirs(os.path.join(proj, ".bodhi"))
    if state is None:
        state = {"version": 2, "projectName": "proj", "topic": "testing",
                 "createdAt": "2026-01-01T10:00:00", "lastSessionAt": "2026-01-01T10:00:00",
                 "totalSessions": 1, "sessionDates": ["2026-01-01"], "currentStreak": 1,
                 "currentPhase": "1", "currentModule": "Module B", "currentModuleIndex": 1,
                 "lastActivity": "seed", "overallCompletion": 10,
                 "customField": "must-survive"}
    with open(os.path.join(proj, ".bodhi", "state.json"), "w") as f:
        json.dump(state, f, indent=2)
    if spaced_review is not None:
        with open(os.path.join(proj, ".bodhi", "spaced-review.json"), "w") as f:
            json.dump(spaced_review, f, indent=2)
    return proj


def read_sr(proj):
    with open(os.path.join(proj, ".bodhi", "spaced-review.json")) as f:
        return json.load(f)


def read_state(proj):
    with open(os.path.join(proj, ".bodhi", "state.json")) as f:
        return json.load(f)


V2_SR = {
    "version": 2,
    "lastReviewCheck": "2026-05-01T10:00:00",
    "concepts": [
        {"name": "B-tree indexes", "module": "Module A", "introduced": "2026-04-01",
         "box": 3, "nextReview": "2026-05-08", "lastReviewed": "2026-05-01",
         "question": "How does a B-tree index speed up reads?",
         "lastResult": "solid recall",
         "precisionGap": "confuses clustered vs non-clustered",  # non-canonical
         "reviewHistory": [
             {"date": "2026-04-20", "result": "correct"},
             {"date": "2026-05-01", "result": "correct"},
         ]},
        {"name": "Query planning", "module": "Module A", "introduced": "2026-04-10",
         "box": 1, "nextReview": "2026-05-02", "lastReviewed": "2026-05-01",
         "question": "", "lastResult": "missed",
         "reviewHistory": [{"date": "2026-05-01", "result": "incorrect"}]},
    ],
    "sessionHistory": [
        {"date": "2026-05-01", "type": "spaced-review", "conceptsReviewed": 2,
         "passes": 1, "misses": 1,
         "habitObservations": {"hedging": "says 'kind of' a lot"}},  # non-canonical
    ],
}


def t_migrate():
    with tempfile.TemporaryDirectory() as root:
        proj = make_project(root, spaced_review=json.loads(json.dumps(V2_SR)))
        out = run(proj, "migrate-spaced-review")
        check("migrate: reports migrated", out.get("action") == "migrated", out)
        sr = read_sr(proj)
        check("migrate: version 3", sr["version"] == 3)
        check("migrate: v3 fields on every concept",
              all(all(k in c for k in ("bloomLevel", "feynmanPassed",
                                       "consecutiveCorrectAtL4Plus"))
                  for c in sr["concepts"]))
        check("migrate: non-canonical concept field preserved",
              sr["concepts"][0].get("precisionGap") == "confuses clustered vs non-clustered")
        check("migrate: non-canonical sessionHistory field preserved",
              sr["sessionHistory"][0].get("habitObservations", {}).get("hedging") is not None)
        backup = os.path.join(proj, ".bodhi", ".pre-1.10-backup", "spaced-review.json")
        check("migrate: backup exists", os.path.exists(backup))
        with open(backup) as f:
            check("migrate: backup is pre-v3", json.load(f)["version"] == 2)
        marker = os.path.join(proj, ".bodhi", ".migration-1.10.md")
        check("migrate: marker written", os.path.exists(marker))
        out2 = run(proj, "migrate-spaced-review")
        check("migrate: idempotent second run", out2.get("action") == "noop", out2)


def t_record_review():
    with tempfile.TemporaryDirectory() as root:
        proj = make_project(root, spaced_review=json.loads(json.dumps(V2_SR)))
        run(proj, "migrate-spaced-review")
        # correct at L4 with confidence: box 3->4, ratchet, counter+1
        out = run(proj, "record-review", "--concept", "B-tree indexes",
                  "--result", "correct", "--tested-bloom", "4",
                  "--confidence", "sure", "--source", "quiz")
        sr = read_sr(proj)
        c = sr["concepts"][0]
        check("review: box promoted", c["box"] == 4, out)
        check("review: bloom ratchet up", c["bloomLevel"] == 4)
        check("review: counter incremented", c["consecutiveCorrectAtL4Plus"] == 1)
        check("review: nextReview = today + 14",
              c["nextReview"] == (TODAY + datetime.timedelta(days=14)).isoformat())
        check("review: history has confidence",
              c["reviewHistory"][-1].get("confidence") == "sure")
        check("review: non-canonical field survives write",
              c.get("precisionGap") is not None)
        # correct at L2: bloom NOT demoted, counter unchanged
        run(proj, "record-review", "--concept", "B-tree indexes",
            "--result", "correct", "--tested-bloom", "2")
        c = read_sr(proj)["concepts"][0]
        check("review: bloom never demotes", c["bloomLevel"] == 4)
        check("review: counter unchanged on low-level correct",
              c["consecutiveCorrectAtL4Plus"] == 1)
        check("review: box capped at 5", c["box"] == 5)
        run(proj, "record-review", "--concept", "B-tree indexes",
            "--result", "correct", "--tested-bloom", "5")
        check("review: box stays at 5", read_sr(proj)["concepts"][0]["box"] == 5)
        # incorrect: box 1, counter reset, bloom preserved
        run(proj, "record-review", "--concept", "B-tree indexes",
            "--result", "incorrect", "--tested-bloom", "4", "--confidence", "sure")
        c = read_sr(proj)["concepts"][0]
        check("review: incorrect demotes to box 1", c["box"] == 1)
        check("review: incorrect resets counter", c["consecutiveCorrectAtL4Plus"] == 0)
        check("review: incorrect preserves bloom", c["bloomLevel"] == 5)
        check("review: incorrect nextReview tomorrow",
              c["nextReview"] == (TODAY + datetime.timedelta(days=1)).isoformat())
        # partial: box held, re-test tomorrow
        run(proj, "record-review", "--concept", "Query planning",
            "--result", "partial", "--tested-bloom", "3")
        c = read_sr(proj)["concepts"][1]
        check("review: partial holds box", c["box"] == 1)
        check("review: partial re-tests tomorrow",
              c["nextReview"] == (TODAY + datetime.timedelta(days=1)).isoformat())
        # auto-create with --module
        run(proj, "record-review", "--concept", "Write-ahead log",
            "--result", "correct", "--tested-bloom", "3", "--module", "Module B")
        check("review: auto-created concept",
              any(c["name"] == "Write-ahead log" for c in read_sr(proj)["concepts"]))
        # untracked without module fails
        run(proj, "record-review", "--concept", "Ghost", "--result", "correct",
            expect_fail=True)


def t_sessions_and_forget():
    with tempfile.TemporaryDirectory() as root:
        proj = make_project(root, spaced_review=json.loads(json.dumps(V2_SR)))
        run(proj, "migrate-spaced-review")
        out = run(proj, "record-session", "--type", "quiz",
                  "--data", '{"conceptsReviewed": 2, "passes": 1, "misses": 1}')
        check("session: recorded", out["entry"]["type"] == "quiz")
        run(proj, "record-session", "--type", "made-up-type", expect_fail=True)
        check("session: invalid type rejected", True)
        run(proj, "record-session", "--type", "other", expect_fail=True)
        check("session: other without subtype rejected", True)
        run(proj, "record-session", "--type", "other", "--subtype", "midnight-cram")
        out = run(proj, "forget", "--concepts", "B-tree indexes, Query planning",
                  "--note", "felt shaky after a week off")
        sr = read_sr(proj)
        check("forget: both demoted",
              all(c["box"] == 1 for c in sr["concepts"][:2]), out)
        check("forget: bloom preserved",
              sr["concepts"][0]["bloomLevel"] == 0 or "bloomLevel" in sr["concepts"][0])
        check("forget: sessionHistory learner-forget entry",
              sr["sessionHistory"][-1]["type"] == "learner-forget")
        check("forget: state lastActivity updated",
              "Demoted" in read_state(proj)["lastActivity"])
        run(proj, "forget", "--concepts", "Nonexistent", expect_fail=True)
        # assessment-history append
        out = run(proj, "record-assessment", "--trigger", "evaluate",
                  "--data", '{"topic": "sql", "overallNote": "steady growth"}')
        check("assessment: entry appended", out["entries"] == 1, out)
        hist = os.path.join(proj, ".bodhi", "assessment-history.json")
        with open(hist) as f:
            e = json.load(f)["entries"][0]
        check("assessment: date + trigger stamped",
              e["trigger"] == "evaluate" and e["date"] == TODAY.isoformat())
        run(proj, "record-assessment", "--trigger", "bogus", "--data", "{}",
            expect_fail=True)


def t_touch_state_and_profile():
    with tempfile.TemporaryDirectory() as root:
        proj = make_project(root)
        out = run(proj, "touch-state", "--activity", "Taught indexing basics",
                  "--module", "Module C", "--completion", "25")
        st = read_state(proj)
        check("state: new session counted", st["totalSessions"] == 2, out)
        check("state: streak reset after gap", st["currentStreak"] == 1)
        check("state: previousModule recorded", st["previousModule"] == "Module B")
        check("state: custom field preserved", st["customField"] == "must-survive")
        check("state: completion set", st["overallCompletion"] == 25)
        out2 = run(proj, "touch-state", "--activity", "Second touch today")
        check("state: same-day touch does not double-count",
              read_state(proj)["totalSessions"] == 2, out2)
        # profile
        with open(os.path.join(root, ".bodhi-profile.json"), "w") as f:
            json.dump({"version": 2, "cumulativeStats": {"totalExercises": 7},
                       "custom": "keep"}, f)
        out3 = run(proj, "bump-profile", "--counter", "totalExercises")
        check("profile: counter bumped", out3["value"] == 8)
        with open(os.path.join(root, ".bodhi-profile.json")) as f:
            check("profile: unknown field preserved", json.load(f)["custom"] == "keep")
        run(proj, "bump-profile", "--counter", "notACounter", expect_fail=True)


def t_gate_check():
    with tempfile.TemporaryDirectory() as root:
        sr = json.loads(json.dumps(V2_SR))
        # Module A concepts; current module is Module B with no work yet -> fires
        proj = make_project(root, spaced_review=sr)
        run(proj, "migrate-spaced-review")
        # 1.15.x: with nothing declared and no previousModule tracked, the gate
        # declines to fire instead of inferring a prior module from concept
        # dates (honest-review #11 — a guessed gate is worse than no gate).
        out = run(proj, "gate-check")
        check("gate: no declaration + no previousModule = declines to fire",
              out["fires"] is False and "--prereqs" in out.get("reason", ""), out)
        out = run(proj, "gate-check", "--prior-module", "Module A")
        check("gate: fires on first session of new module", out["fires"] is True, out)
        check("gate: prior-module source reported",
              out["prerequisiteSource"] == "prior-module", out)
        # bloomLevel 0 everywhere -> no-opinion, verdict clear
        check("gate: legacy fallthrough (bloom 0 = no opinion)",
              out["verdict"] == "clear"
              and all(p["status"] == "no-opinion" for p in out["prerequisites"]), out)
        # Classify: B-tree to bloom 3 with recent review -> satisfied
        run(proj, "record-review", "--concept", "B-tree indexes",
            "--result", "correct", "--tested-bloom", "3")
        out = run(proj, "gate-check", "--prior-module", "Module A")
        btree = [p for p in out["prerequisites"] if p["name"] == "B-tree indexes"][0]
        check("gate: bloom>=3 recent = satisfied", btree["status"] == "satisfied")
        # Query planning at bloom 2, box 1, no strong evidence -> gap
        run(proj, "record-review", "--concept", "Query planning",
            "--result", "incorrect", "--tested-bloom", "2")
        run(proj, "record-review", "--concept", "Query planning",
            "--result", "correct", "--tested-bloom", "2")
        out = run(proj, "gate-check", "--prior-module", "Module A")
        qp = [p for p in out["prerequisites"] if p["name"] == "Query planning"][0]
        check("gate: low bloom without evidence = gap", qp["status"] == "gap", out)
        check("gate: verdict offer when gaps exist", out["verdict"] == "offer")
        # Stale: bloom 3 but box 1 and lastReviewed 90 days ago -> stale-reconfirm
        srdata = read_sr(proj)
        c = srdata["concepts"][0]
        c["box"] = 1
        c["lastReviewed"] = (TODAY - datetime.timedelta(days=90)).isoformat()
        with open(os.path.join(proj, ".bodhi", "spaced-review.json"), "w") as f:
            json.dump(srdata, f)
        out = run(proj, "gate-check", "--prior-module", "Module A")
        btree = [p for p in out["prerequisites"] if p["name"] == "B-tree indexes"][0]
        check("gate: bloom>=3 but stale evidence = stale-reconfirm (1.11.0 recency rule)",
              btree["status"] == "stale-reconfirm", out)
        # Apply-equivalent: bloom 2, box 3, last two correct
        srdata = read_sr(proj)
        c = srdata["concepts"][1]
        c["bloomLevel"] = 2
        c["box"] = 3
        c["reviewHistory"] = [{"date": "2026-05-01", "result": "correct"},
                              {"date": "2026-05-20", "result": "correct"}]
        with open(os.path.join(proj, ".bodhi", "spaced-review.json"), "w") as f:
            json.dump(srdata, f)
        out = run(proj, "gate-check", "--prior-module", "Module A")
        qp = [p for p in out["prerequisites"] if p["name"] == "Query planning"][0]
        check("gate: strong v2 evidence = apply-equivalent", qp["status"] == "apply-equivalent")
        # Continuation session: concept exists for current module -> does not fire
        run(proj, "add-concept", "--concept", "Replication lag", "--module", "Module B")
        out = run(proj, "gate-check")
        check("gate: continuation session does not fire", out["fires"] is False)
        # Declared prereqs path
        out = run(proj, "gate-check", "--module", "Module Z",
                  "--prereqs", "B-tree indexes")
        check("gate: declared prereq list respected",
              out["fires"] and len(out["prerequisites"]) == 1
              and out["prerequisiteSource"] == "declared")


def t_mastery_due_calibration():
    with tempfile.TemporaryDirectory() as root:
        proj = make_project(root, spaced_review=json.loads(json.dumps(V2_SR)))
        run(proj, "migrate-spaced-review")
        out = run(proj, "mastery")
        check("mastery: legacy module shows null (not 0%)",
              out["modules"]["Module A"]["masteryPct"] is None, out)
        check("mastery: rollup buckets", out["retentionRollup"]["building"] == 1
              and out["retentionRollup"]["needs_review"] == 1)
        out = run(proj, "due")
        check("due: overdue concepts listed", out["dueToday"] == 2, out)
        run(proj, "record-review", "--concept", "B-tree indexes",
            "--result", "correct", "--tested-bloom", "4", "--confidence", "sure")
        run(proj, "record-review", "--concept", "Query planning",
            "--result", "incorrect", "--tested-bloom", "3", "--confidence", "sure")
        run(proj, "record-review", "--concept", "Query planning",
            "--result", "correct", "--tested-bloom", "2", "--confidence", "guessing")
        out = run(proj, "calibration")
        check("calibration: tagged answers counted", out["taggedAnswers"] == 3, out)
        check("calibration: overconfident event captured",
              out["overconfidentEvents"] and
              out["overconfidentEvents"][-1]["concept"] == "Query planning")
        check("calibration: underconfidence rate computed",
              out["underconfidenceRate"] == 1.0)
        # set-feynman + mastery formula end-to-end
        run(proj, "set-feynman", "--concept", "B-tree indexes")
        for _ in range(3):
            run(proj, "record-review", "--concept", "B-tree indexes",
                "--result", "correct", "--tested-bloom", "5")
        out = run(proj, "mastery")
        check("mastery: formula reaches mastered",
              out["modules"]["Module A"]["masteryPct"] == 50, out)


def t_retry_and_relearning():
    with tempfile.TemporaryDirectory() as root:
        proj = make_project(root, spaced_review=json.loads(json.dumps(V2_SR)))
        run(proj, "migrate-spaced-review")
        # Miss -> Box 1, review tomorrow
        run(proj, "record-review", "--concept", "B-tree indexes",
            "--result", "incorrect", "--tested-bloom", "3", "--source", "quiz")
        c = read_sr(proj)["concepts"][0]
        tomorrow = (TODAY + datetime.timedelta(days=1)).isoformat()
        check("retry: miss demoted to box 1", c["box"] == 1 and c["nextReview"] == tomorrow)
        # Successful relearning retry: history entry, NO box/schedule movement
        out = run(proj, "record-review", "--concept", "B-tree indexes",
                  "--result", "correct", "--tested-bloom", "3", "--retry",
                  "--source", "quiz")
        c = read_sr(proj)["concepts"][0]
        check("retry: box unchanged", c["box"] == 1, out)
        check("retry: nextReview still tomorrow (demotion stands)",
              c["nextReview"] == tomorrow)
        check("retry: counter unchanged", c["consecutiveCorrectAtL4Plus"] == 0)
        check("retry: history entry flagged",
              c["reviewHistory"][-1].get("retry") is True
              and c["reviewHistory"][-1]["result"] == "correct")
        check("retry: bloom not ratcheted by retry", c["bloomLevel"] == 0)


def t_partial_breaks_streak():
    # 1.11.2 — "3 consecutive correct at L4+" means uninterrupted corrects.
    # A partial retrieval is not a correct one: it must reset the counter
    # (previously correct/partial/correct/correct counted as 3 "consecutive").
    with tempfile.TemporaryDirectory() as root:
        proj = make_project(root, spaced_review=json.loads(json.dumps(V2_SR)))
        run(proj, "migrate-spaced-review")
        run(proj, "record-review", "--concept", "B-tree indexes",
            "--result", "correct", "--tested-bloom", "4")
        c = read_sr(proj)["concepts"][0]
        check("streak: correct at L4 increments", c["consecutiveCorrectAtL4Plus"] == 1)
        box_after_correct = c["box"]
        run(proj, "record-review", "--concept", "B-tree indexes",
            "--result", "partial", "--tested-bloom", "4")
        c = read_sr(proj)["concepts"][0]
        check("streak: partial resets counter", c["consecutiveCorrectAtL4Plus"] == 0, c)
        check("streak: partial still holds box (no Leitner demotion)",
              c["box"] == box_after_correct)
        run(proj, "record-review", "--concept", "B-tree indexes",
            "--result", "correct", "--tested-bloom", "4")
        run(proj, "record-review", "--concept", "B-tree indexes",
            "--result", "correct", "--tested-bloom", "4")
        c = read_sr(proj)["concepts"][0]
        check("streak: rebuilt from zero after the partial",
              c["consecutiveCorrectAtL4Plus"] == 2, c)
        # A partial RETRY is a relearning rep: no counter movement of any kind.
        run(proj, "record-review", "--concept", "B-tree indexes",
            "--result", "partial", "--tested-bloom", "4", "--retry")
        c = read_sr(proj)["concepts"][0]
        check("streak: partial retry does not touch the counter",
              c["consecutiveCorrectAtL4Plus"] == 2, c)


def t_touch_state_profile_bump():
    with tempfile.TemporaryDirectory() as root:
        proj = make_project(root)
        with open(os.path.join(root, ".bodhi-profile.json"), "w") as f:
            json.dump({"version": 2, "cumulativeStats": {"totalSessions": 6}}, f)
        out = run(proj, "touch-state", "--activity", "first touch today")
        check("bump: first touch of the day bumps profile",
              out["profileSessionsBumped"] is True, out)
        out2 = run(proj, "touch-state", "--activity", "second touch today")
        check("bump: same-day touch does not re-bump",
              out2["profileSessionsBumped"] is False, out2)
        with open(os.path.join(root, ".bodhi-profile.json")) as f:
            check("bump: profile counter incremented exactly once",
                  json.load(f)["cumulativeStats"]["totalSessions"] == 7)


def t_data_reserved_keys():
    with tempfile.TemporaryDirectory() as root:
        proj = make_project(root, spaced_review=json.loads(json.dumps(V2_SR)))
        run(proj, "migrate-spaced-review")
        run(proj, "record-session", "--type", "quiz",
            "--data", '{"type": "hax", "date": "1999-01-01", "notes": "kept"}')
        e = read_sr(proj)["sessionHistory"][-1]
        check("reserved: --data cannot override type", e["type"] == "quiz", e)
        check("reserved: --data cannot override date", e["date"] == TODAY.isoformat())
        check("reserved: non-reserved keys kept", e.get("notes") == "kept")
        r = subprocess.run([sys.executable, SCRIPT, "--project", proj, "verify"],
                           capture_output=True, text=True)
        check("reserved: verify stays clean after the write", r.returncode == 0)


def t_migrate_stale_backup():
    with tempfile.TemporaryDirectory() as root:
        proj = make_project(root, spaced_review=json.loads(json.dumps(V2_SR)))
        run(proj, "migrate-spaced-review")
        # Simulate a sync-restore: live file back at v2 with an EXTRA concept,
        # while the old (smaller) backup is still on disk.
        sr = json.loads(json.dumps(V2_SR))
        sr["concepts"].append({"name": "Extra", "module": "Module A",
                               "introduced": "2026-06-01", "box": 1,
                               "nextReview": "2026-06-02", "lastReviewed": None,
                               "reviewHistory": []})
        with open(os.path.join(proj, ".bodhi", "spaced-review.json"), "w") as f:
            json.dump(sr, f)
        os.remove(os.path.join(proj, ".bodhi", ".migration-1.10.md"))
        out = run(proj, "migrate-spaced-review")
        check("stale-backup: re-migration succeeds against this run's input",
              out.get("action") == "migrated" and out["concepts"] == 3, out)
        check("stale-backup: extra concept survived",
              any(c["name"] == "Extra" for c in read_sr(proj)["concepts"]))
        backup = os.path.join(proj, ".bodhi", ".pre-1.10-backup", "spaced-review.json")
        with open(backup) as f:
            check("stale-backup: original backup never overwritten",
                  len(json.load(f)["concepts"]) == 2)


def t_forget_comma_names():
    with tempfile.TemporaryDirectory() as root:
        proj = make_project(root, spaced_review=json.loads(json.dumps(V2_SR)))
        run(proj, "migrate-spaced-review")
        run(proj, "add-concept", "--concept", "ACID, isolation levels",
            "--module", "Module A")
        out = run(proj, "forget", "--concept", "ACID, isolation levels")
        check("forget: comma-containing name demotable via --concept",
              out["concepts"] == ["ACID, isolation levels"], out)
        out = run(proj, "forget", "--concept", "B-tree indexes",
                  "--concept", "Query planning")
        check("forget: repeatable --concept demotes both", len(out["concepts"]) == 2)


def t_robustness():
    with tempfile.TemporaryDirectory() as root:
        proj = make_project(root, spaced_review=json.loads(json.dumps(V2_SR)))
        run(proj, "migrate-spaced-review")
        # Corrupt JSON -> clean die, no traceback
        srp = os.path.join(proj, ".bodhi", "spaced-review.json")
        good = open(srp).read()
        open(srp, "w").write(good[:50])
        r = subprocess.run([sys.executable, SCRIPT, "--project", proj, "due"],
                           capture_output=True, text=True)
        check("robust: corrupt JSON dies cleanly", r.returncode == 1
              and "Traceback" not in r.stderr and "not valid JSON" in r.stderr,
              r.stderr[:120])
        open(srp, "w").write(good)
        # Unparseable nextReview surfaced by due + flagged by verify
        sr = read_sr(proj)
        sr["concepts"][0]["nextReview"] = "not-a-date"
        with open(srp, "w") as f:
            json.dump(sr, f)
        out = run(proj, "due")
        check("robust: unparseable nextReview surfaced",
              out.get("unparseableDates")
              and out["unparseableDates"][0]["name"] == "B-tree indexes", out)
        r = subprocess.run([sys.executable, SCRIPT, "--project", proj, "verify"],
                           capture_output=True, text=True)
        check("robust: verify errors on unparseable nextReview", r.returncode == 1)
        sr["concepts"][0]["nextReview"] = "2026-06-01"
        # Case-insensitive duplicate -> verify error
        sr["concepts"].append(dict(sr["concepts"][0], name="B-TREE INDEXES"))
        with open(srp, "w") as f:
            json.dump(sr, f)
        r = subprocess.run([sys.executable, SCRIPT, "--project", proj, "verify"],
                           capture_output=True, text=True)
        check("robust: duplicate names flagged",
              r.returncode == 1 and "duplicate" in r.stdout)
        # state.json as a list -> clean die
        spath = os.path.join(proj, ".bodhi", "state.json")
        sgood = open(spath).read()
        open(spath, "w").write("[1, 2]")
        r = subprocess.run([sys.executable, SCRIPT, "--project", proj, "gate-check"],
                           capture_output=True, text=True)
        check("robust: list-typed state.json dies cleanly",
              r.returncode == 1 and "Traceback" not in r.stderr)
        open(spath, "w").write(sgood)
        # gate-check with empty currentModule declines
        st = json.loads(sgood)
        st["currentModule"] = ""
        with open(spath, "w") as f:
            json.dump(st, f)
        out = run(proj, "gate-check")
        check("robust: empty currentModule declines to gate",
              out["fires"] is False and "currentModule" in out["reason"], out)
        # missing spaced-review.json -> verify warns
        os.remove(srp)
        r = subprocess.run([sys.executable, SCRIPT, "--project", proj, "verify"],
                           capture_output=True, text=True)
        outj = json.loads(r.stdout)
        check("robust: missing spaced-review warned",
              any("missing" in w for w in outj["warnings"]), outj)


def t_concurrency():
    with tempfile.TemporaryDirectory() as root:
        proj = make_project(root, spaced_review=json.loads(json.dumps(V2_SR)))
        run(proj, "migrate-spaced-review")
        for i in range(8):
            run(proj, "add-concept", "--concept", f"c{i}", "--module", "Module B")
        procs = [subprocess.Popen(
            [sys.executable, SCRIPT, "--project", proj, "record-review",
             "--concept", f"c{i}", "--result", "correct", "--tested-bloom", "2"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            for i in range(8)]
        errs = []
        for p in procs:
            _, err = p.communicate()
            if p.returncode != 0 or "Traceback" in err:
                errs.append(err[:120])
        check("concurrency: 8 parallel writers, zero failures", not errs, errs)
        sr = read_sr(proj)
        lost = [f"c{i}" for i in range(8)
                if next(c for c in sr["concepts"] if c["name"] == f"c{i}")["box"] != 2]
        check("concurrency: zero lost updates", not lost, lost)


def t_history_cap():
    with tempfile.TemporaryDirectory() as root:
        proj = make_project(root, spaced_review=json.loads(json.dumps(V2_SR)))
        run(proj, "migrate-spaced-review")
        sr = read_sr(proj)
        sr["concepts"][0]["reviewHistory"] = [
            {"date": "2026-01-01", "result": "correct"} for _ in range(105)]
        with open(os.path.join(proj, ".bodhi", "spaced-review.json"), "w") as f:
            json.dump(sr, f)
        run(proj, "record-review", "--concept", "B-tree indexes",
            "--result", "correct", "--tested-bloom", "2")
        c = read_sr(proj)["concepts"][0]
        check("cap: history capped at 100", len(c["reviewHistory"]) == 100,
              len(c["reviewHistory"]))
        check("cap: archived count recorded", c.get("reviewHistoryArchived") == 6)
        check("cap: newest entry kept",
              c["reviewHistory"][-1]["date"] == TODAY.isoformat())


def t_mastery_blocked_on_feynman():
    with tempfile.TemporaryDirectory() as root:
        proj = make_project(root, spaced_review=json.loads(json.dumps(V2_SR)))
        run(proj, "migrate-spaced-review")
        for _ in range(3):
            run(proj, "record-review", "--concept", "B-tree indexes",
                "--result", "correct", "--tested-bloom", "5")
        out = run(proj, "mastery")
        check("blocked: quiz-only concept named",
              out["blockedOnFeynman"] == ["B-tree indexes"], out)
        run(proj, "set-feynman", "--concept", "B-tree indexes")
        out = run(proj, "mastery")
        check("blocked: cleared after the gate", out["blockedOnFeynman"] == [])


RETENTION_SR = {
    "version": 3, "lastReviewCheck": None,
    "concepts": [
        {"name": "Secret concept name", "module": "Module A",
         "introduced": "2026-01-01", "box": 2, "nextReview": "2026-03-01",
         "lastReviewed": "2026-02-13", "question": "a private question",
         "lastResult": "correct", "bloomLevel": 4, "feynmanPassed": True,
         "consecutiveCorrectAtL4Plus": 3,
         "reviewHistory": [
             # gaps: introduced->+1d, +3d, (retry excluded), +8d, +31d(no boxBefore)
             {"date": "2026-01-02", "result": "correct", "bloomLevel": 3,
              "boxBefore": 1, "confidence": "sure"},
             {"date": "2026-01-05", "result": "incorrect", "bloomLevel": 3,
              "boxBefore": 2},
             {"date": "2026-01-05", "result": "correct", "bloomLevel": 3,
              "boxBefore": 1, "retry": True},
             {"date": "2026-01-13", "result": "correct", "bloomLevel": 3,
              "boxBefore": 1},
             {"date": "2026-02-13", "result": "correct", "bloomLevel": 4},
         ]},
    ],
    "sessionHistory": [{"date": "2026-01-05", "type": "quiz",
                        "notes": "private session note"}],
}


def t_box_before():
    with tempfile.TemporaryDirectory() as root:
        proj = make_project(root, spaced_review=json.loads(json.dumps(V2_SR)))
        run(proj, "migrate-spaced-review")
        # B-tree indexes sits in box 3; the entry must record the box the
        # review was answered FROM, not the box it moved to.
        run(proj, "record-review", "--concept", "B-tree indexes",
            "--result", "correct", "--tested-bloom", "4")
        c = read_sr(proj)["concepts"][0]
        check("boxBefore: records pre-movement box",
              c["reviewHistory"][-1].get("boxBefore") == 3
              and c["box"] == 4, c["reviewHistory"][-1])
        run(proj, "record-review", "--concept", "B-tree indexes",
            "--result", "correct", "--tested-bloom", "3", "--retry")
        c = read_sr(proj)["concepts"][0]
        check("boxBefore: present on retry entries too",
              c["reviewHistory"][-1].get("boxBefore") == 4)


def t_retention():
    with tempfile.TemporaryDirectory() as root:
        proj = make_project(root,
                            spaced_review=json.loads(json.dumps(RETENTION_SR)))
        out = run(proj, "retention")
        check("retention: retries excluded from review count",
              out["reviews"] == 4 and out["relearningRetriesExcluded"] == 1, out)
        check("retention: overall success rate", out["overallSuccessRate"] == 0.75)
        gaps = out["byGap"]
        check("retention: 1d gap bucket (introduced -> first review)",
              gaps["1d"]["correct"] == 1 and gaps["1d"]["reviews"] == 1, gaps)
        check("retention: 2-3d gap bucket", gaps["2-3d"]["incorrect"] == 1)
        check("retention: 8-14d gap bucket (retry did not shift the gap)",
              gaps["8-14d"]["correct"] == 1)
        check("retention: 31d+ gap bucket", gaps["31d+"]["correct"] == 1)
        boxes = out["byBoxAtReview"]
        check("retention: by-box rates from boxBefore",
              boxes["1"]["correct"] == 2 and boxes["2"]["incorrect"] == 1, boxes)
        check("retention: legacy entries without boxBefore counted honestly",
              out["entriesWithoutBoxBefore"] == 1)


def t_export_anonymized():
    with tempfile.TemporaryDirectory() as root:
        proj = make_project(root,
                            spaced_review=json.loads(json.dumps(RETENTION_SR)))
        out = run(proj, "export-anonymized")
        blob = json.dumps(out)
        check("export: no concept names anywhere",
              "Secret" not in blob and "B-tree" not in blob)
        check("export: no questions or notes",
              "private" not in blob)
        check("export: no project name or topic",
              "proj" not in json.dumps({k: v for k, v in out.items() if k != "project"})
              and "testing" not in blob)
        check("export: counts correct",
              out["concepts"] == 1 and out["boxDistribution"]["2"] == 1
              and out["bloomDistribution"]["4"] == 1
              and out["feynmanPassed"] == 1, out)
        check("export: mastered computed via canonical formula",
              out["mastered"] == 0)  # box 2 < 4 blocks it
        check("export: session types counted, content dropped",
              out["sessionTypeCounts"] == {"quiz": 1})
        check("export: calibration events stripped",
              "overconfidentEvents" not in out["calibration"]
              and out["calibration"]["taggedAnswers"] == 1)
        check("export: retention embedded", out["retention"]["reviews"] == 4)
        check("export: project block has no free text",
              set(out["project"].keys()) == {"totalSessions", "currentStreak",
                                             "overallCompletion", "daysSinceStart"}
              and out["project"]["daysSinceStart"] is not None, out.get("project"))


# Modeled on drift found in real learning projects (2026-07-02 dogfood):
# pre-1.11.0 executors invented a parallel state.json schema — nested session
# bookkeeping, dict lastActivity/previousModule, plural *BloomLevels,
# duplicate sessionDates — and invented reviewHistory result vocabulary.
DRIFTED_STATE = {
    "version": 2, "projectName": "proj", "topic": "testing",
    "createdAt": "2026-06-01", "lastSessionAt": "2026-06-05",
    "session": {"totalSessions": 4,
                "sessionDates": ["2026-06-05", "2026-06-05", "2026-06-05", "2026-06-04"],
                "currentStreak": 1},
    "currentPhase": "1", "currentModule": 2, "currentModuleIndex": 0,
    "previousModule": {"id": "0.3", "name": "Module 0.3", "completedAt": "2026-06-05",
                       "outcomes": "rich narrative that must survive"},
    "lastActivity": {"type": "phase-complete", "name": "Phase 0 assessments",
                     "completed": True, "result": "long narrative " * 30},
    "nextActivity": {"type": "module-start", "name": "Module 1.1"},
    "initialBloomLevels": {"ruby": 0, "elixir": 0},
    "currentBloomLevels": {"ruby": 3, "elixir": 1},
    "pace": {"intent": "open-ended depth"},
    "weightDistribution": {"ai": 0.4, "elixir": 0.6},
    "overallCompletion": 5,
}

DRIFTED_SR = {
    "version": 3, "lastReviewCheck": None,
    "concepts": [
        {"name": "CSRF tokens", "module": "Module 0", "introduced": "2026-05-01",
         "box": 2, "nextReview": "2026-06-11", "lastReviewed": "2026-06-09",
         "question": "", "lastResult": "skipped", "bloomLevel": 0,
         "feynmanPassed": False, "consecutiveCorrectAtL4Plus": 0,
         "reviewHistory": [
             {"date": "2026-06-01", "result": "correct", "bloomLevel": 2},
             {"date": "2026-06-09", "result": "skipped",
              "note": "session consumed; rolled +2 days"},
         ]},
    ],
    "sessionHistory": [
        {"date": "2026-06-09", "type": "phase-0-reteach-partial",
         "notes": "invented type from the wild"},
    ],
}


def t_defer():
    with tempfile.TemporaryDirectory() as root:
        proj = make_project(root, spaced_review=json.loads(json.dumps(V2_SR)))
        run(proj, "migrate-spaced-review")
        before = read_sr(proj)["concepts"][0]
        out = run(proj, "defer", "--concept", "B-tree indexes", "--days", "2",
                  "--note", "session ran out")
        c = read_sr(proj)["concepts"][0]
        check("defer: nextReview rolled by --days",
              c["nextReview"] == (TODAY + datetime.timedelta(days=2)).isoformat(), out)
        check("defer: box untouched", c["box"] == before["box"])
        check("defer: lastReviewed untouched (no retrieval happened)",
              c["lastReviewed"] == before["lastReviewed"])
        entry = c["reviewHistory"][-1]
        check("defer: history entry is a deferral, not an outcome",
              entry.get("deferred") is True and "result" not in entry
              and entry.get("days") == 2, entry)
        out = run(proj, "retention")
        check("defer: retention excludes deferrals explicitly",
              out.get("deferralsExcluded") == 1 and out["entriesSkipped"] == 0, out)
        run(proj, "defer", "--concept", "Ghost", expect_fail=True)


def t_verify_flags_drift():
    with tempfile.TemporaryDirectory() as root:
        proj = make_project(root, spaced_review=json.loads(json.dumps(DRIFTED_SR)),
                            state=json.loads(json.dumps(DRIFTED_STATE)))
        r = subprocess.run([sys.executable, SCRIPT, "--project", proj, "verify"],
                           capture_output=True, text=True)
        out = json.loads(r.stdout)
        check("drift: verify fails on drifted files", r.returncode == 1)
        errs = " | ".join(out["errors"])
        check("drift: nested session bookkeeping flagged", "session" in errs.lower(), errs)
        check("drift: dict lastActivity flagged", "lastActivity" in errs, errs)
        check("drift: dict previousModule flagged", "previousModule" in errs, errs)
        check("drift: invented result vocabulary flagged",
              "skipped" in errs or "result" in errs, errs)
        check("drift: repair pointer names normalize", "normalize" in errs, errs)
        # A canonical deferral entry must NOT be flagged.
        sr = json.loads(json.dumps(V2_SR))
        sr["concepts"][0]["reviewHistory"].append(
            {"date": "2026-06-09", "deferred": True, "days": 2})
        proj2 = make_project(os.path.join(root, "p2"), spaced_review=sr)
        r = subprocess.run([sys.executable, SCRIPT, "--project", proj2, "verify"],
                           capture_output=True, text=True)
        check("drift: deferral entries pass verify", r.returncode == 0,
              r.stdout[:200])


def t_normalize():
    with tempfile.TemporaryDirectory() as root:
        proj = make_project(root, spaced_review=json.loads(json.dumps(DRIFTED_SR)),
                            state=json.loads(json.dumps(DRIFTED_STATE)))
        out = run(proj, "normalize")
        check("normalize: reports transforms", out.get("action") == "normalized", out)
        st = read_state(proj)
        check("normalize: session bookkeeping lifted to top level",
              st.get("totalSessions") == 4 and st.get("currentStreak") == 1
              and "session" not in st, st.get("totalSessions"))
        check("normalize: sessionDates deduped and sorted",
              st.get("sessionDates") == ["2026-06-04", "2026-06-05"])
        check("normalize: lastActivity stringified <=120 chars",
              isinstance(st.get("lastActivity"), str) and len(st["lastActivity"]) <= 120)
        check("normalize: original lastActivity preserved as legacy",
              isinstance(st.get("lastActivityLegacy"), dict))
        check("normalize: previousModule stringified, narrative preserved",
              st.get("previousModule") == "Module 0.3"
              and st.get("previousModuleLegacy", {}).get("outcomes"))
        check("normalize: numeric currentModule stringified",
              st.get("currentModule") == "2", st.get("currentModule"))
        check("normalize: plural bloom maps renamed to singular",
              st.get("currentBloomLevel", {}).get("ruby") == 3
              and "currentBloomLevels" not in st)
        check("normalize: unknown learner fields untouched",
              st.get("pace", {}).get("intent") == "open-ended depth"
              and st.get("weightDistribution", {}).get("ai") == 0.4
              and isinstance(st.get("nextActivity"), dict))
        sr = read_sr(proj)
        entry = sr["concepts"][0]["reviewHistory"][-1]
        check("normalize: invented 'skipped' result becomes a deferral",
              entry.get("deferred") is True and "result" not in entry
              and entry.get("note"), entry)
        sess = sr["sessionHistory"][-1]
        check("normalize: invented session type becomes other+subtype",
              sess["type"] == "other"
              and sess["subtype"] == "phase-0-reteach-partial", sess)
        backup_dir = os.path.join(proj, ".bodhi", ".pre-normalize-backup")
        check("normalize: backups written",
              os.path.exists(os.path.join(backup_dir, "state.json"))
              and os.path.exists(os.path.join(backup_dir, "spaced-review.json")))
        with open(os.path.join(backup_dir, "state.json")) as f:
            check("normalize: backup is the pre-normalize shape",
                  isinstance(json.load(f).get("session"), dict))
        r = subprocess.run([sys.executable, SCRIPT, "--project", proj, "verify"],
                           capture_output=True, text=True)
        check("normalize: verify clean afterwards", r.returncode == 0,
              r.stdout[:300])
        out2 = run(proj, "normalize")
        check("normalize: idempotent second run", out2.get("action") == "noop", out2)


def t_verify():
    with tempfile.TemporaryDirectory() as root:
        proj = make_project(root, spaced_review=json.loads(json.dumps(V2_SR)))
        r = subprocess.run([sys.executable, SCRIPT, "--project", proj, "verify"],
                           capture_output=True, text=True)
        out = json.loads(r.stdout)
        check("verify: v2 file passes with warning", r.returncode == 0
              and any("v2" in w for w in out["warnings"]), out)
        # Break it: invalid session type
        srdata = read_sr(proj)
        srdata["sessionHistory"].append({"date": "2026-06-01", "type": "invented"})
        with open(os.path.join(proj, ".bodhi", "spaced-review.json"), "w") as f:
            json.dump(srdata, f)
        r = subprocess.run([sys.executable, SCRIPT, "--project", proj, "verify"],
                           capture_output=True, text=True)
        check("verify: invalid session type fails", r.returncode == 1)


def t_last_activity_threshold():
    """Fidelity D1: one value for lastActivity length, not three.

    Before 1.14.x the guidance was spelled three different ways — touch-state
    truncated at 120, verify warned above 160, and the warning text claimed
    120. So a 140-char lastActivity passed silently while a 165-char one was
    told the limit was 120. The state-ops KB says 120; that value now wins in
    all three places.
    """
    with tempfile.TemporaryDirectory() as root:
        proj = make_project(root, spaced_review=json.loads(json.dumps(V2_SR)))
        # touch-state truncates at exactly the guidance value.
        run(proj, "touch-state", "--activity", "x" * 200)
        check("lastActivity: touch-state truncates to 120",
              len(read_state(proj)["lastActivity"]) == 120)
        # A hand-written 140-char value used to slip past verify (120 < 140 < 160).
        st = read_state(proj)
        st["lastActivity"] = "y" * 140
        with open(os.path.join(proj, ".bodhi", "state.json"), "w") as f:
            json.dump(st, f)
        out = run(proj, "verify")
        check("lastActivity: 140 chars now warns (was silent under the 160 check)",
              any("lastActivity" in w for w in out["warnings"]), out)
        # And the message quotes the value it actually enforces.
        check("lastActivity: warning states 120, not 160",
              any("120-char" in w for w in out["warnings"]), out)


def t_profile_project_list_shape():
    """P1: verify backstops the profile-list entry shape.

    Originally the projects list was the one write the script did not own;
    since 1.16.0 the profile-* subcommands own it, but the script-unavailable
    fallback can still hand-edit these files. verify cannot prevent a dropped
    field on that path, but it can refuse to call the result ok, which is
    what turns a silent hole into a caught one.
    """
    ACTIVE = {"name": "sql-deep-dive", "topic": "SQL", "startedAt": "2026-01-01",
              "currentPhase": "1", "currentModule": "Joins", "bloomLevel": 2,
              "pace": "open-ended", "status": "active", "trackPurpose": "depth"}
    COMPLETED = {"name": "react-basics", "completedAt": "2026-02-01",
                 "finalBloomLevel": 4, "trackPurpose": "foundation"}

    def write_lists(root, **over):
        payload = {"version": 2, "activeProjects": [dict(ACTIVE)],
                   "completedProjects": [dict(COMPLETED)]}
        payload.update(over)
        with open(os.path.join(root, ".bodhi-profile.json"), "w") as f:
            json.dump({"version": 2}, f)
        with open(os.path.join(root, ".bodhi-profile.projects.json"), "w") as f:
            json.dump(payload, f)

    with tempfile.TemporaryDirectory() as root:
        proj = make_project(root, spaced_review=json.loads(json.dumps(V2_SR)))
        write_lists(root)
        out = run(proj, "verify")
        check("profile list: well-formed entries verify clean", out["ok"] is True, out)

        # trackPurpose is the field the probe singled out as most likely to be
        # dropped by a careless rewrite — it carries no meaning to a model
        # skimming the entry, and nothing else in the file references it.
        thin = dict(ACTIVE)
        del thin["trackPurpose"]
        write_lists(root, activeProjects=[thin])
        out = run(proj, "verify", expect_fail=True)
        check("profile list: dropped trackPurpose now fails verify",
              out["ok"] is False, out)
        check("profile list: error names the entry and the missing field",
              any("sql-deep-dive" in e and "trackPurpose" in e
                  for e in out["errors"]), out)

        # completedProjects has its own (different, shorter) required set.
        thin_done = dict(COMPLETED)
        del thin_done["finalBloomLevel"]
        write_lists(root, completedProjects=[thin_done])
        out = run(proj, "verify", expect_fail=True)
        check("profile list: completedProjects shape checked too",
              any("finalBloomLevel" in e for e in out["errors"]), out)

        # An unnamed entry still has to be reportable — fall back to the index.
        write_lists(root, activeProjects=[{"topic": "SQL"}])
        out = run(proj, "verify", expect_fail=True)
        check("profile list: nameless entry reported by index",
              any("index 0" in e for e in out["errors"]), out)

        # Extra fields are the learner's/future schema's business, not an error.
        fat = dict(ACTIVE)
        fat["someFutureField"] = "keep"
        write_lists(root, activeProjects=[fat])
        check("profile list: unknown extra fields are not errors",
              run(proj, "verify")["ok"] is True)

        # Absent lists are legal (a profile before the first /learn append).
        write_lists(root, activeProjects=None)
        payload = {"version": 2, "completedProjects": [dict(COMPLETED)]}
        with open(os.path.join(root, ".bodhi-profile.projects.json"), "w") as f:
            json.dump(payload, f)
        check("profile list: missing activeProjects key is not an error",
              run(proj, "verify")["ok"] is True)

        # And the whole file being absent stays legal — verify is scoped to a
        # project; a solo project may never have had a cross-project profile.
        os.remove(os.path.join(root, ".bodhi-profile.projects.json"))
        check("profile list: absent list file is not an error",
              run(proj, "verify")["ok"] is True)


def t_session_brief():
    with tempfile.TemporaryDirectory() as root:
        proj = make_project(root, spaced_review=json.loads(json.dumps(V2_SR)))
        # Untracked concept -> first exposure, pretest applies.
        out = run(proj, "session-brief", "--concept", "CTEs")
        check("brief: untracked is first exposure",
              out["tracked"] is False and out["firstExposure"] is True
              and out["pretestApplies"] is True and out["isReteach"] is False, out)
        # Tracked, bloomLevel 0 (v2 legacy) but WITH real history -> not first
        # exposure (the pretest research covers untaught material only).
        out = run(proj, "session-brief", "--concept", "B-tree indexes")
        check("brief: legacy history blocks first exposure",
              out["tracked"] is True and out["firstExposure"] is False, out)
        check("brief: healthy box-3 concept is not a reteach",
              out["isReteach"] is False, out)
        # Box-1 concept with an incorrect latest result -> targeted re-teach.
        out = run(proj, "session-brief", "--concept", "Query planning")
        check("brief: demoted concept is a reteach",
              out["isReteach"] is True and out["box"] == 1, out)
        # Tracked via add-concept but never reviewed -> still first exposure,
        # and a deferral does not change that (scheduling, not exposure).
        run(proj, "add-concept", "--concept", "Window functions", "--module", "Module B")
        run(proj, "defer", "--concept", "Window functions")
        out = run(proj, "session-brief", "--concept", "Window functions")
        check("brief: deferral-only history stays first exposure",
              out["firstExposure"] is True and out["pretestApplies"] is True, out)
        # currentModule surfaces from state.json.
        check("brief: carries currentModule", out["currentModule"] == "Module B", out)


def t_crossed_bloom3():
    with tempfile.TemporaryDirectory() as root:
        proj = make_project(root, spaced_review=json.loads(json.dumps(V2_SR)))
        out = run(proj, "record-review", "--concept", "B-tree indexes",
                  "--result", "correct", "--tested-bloom", "4")
        check("crossedBloom3: reported on the crossing write",
              out.get("crossedBloom3") is True, out)
        out = run(proj, "record-review", "--concept", "B-tree indexes",
                  "--result", "correct", "--tested-bloom", "5")
        check("crossedBloom3: false once already past 3",
              out.get("crossedBloom3") is False, out)
        out = run(proj, "record-review", "--concept", "Query planning",
                  "--result", "correct", "--tested-bloom", "2")
        check("crossedBloom3: false below the line",
              out.get("crossedBloom3") is False, out)
        out = run(proj, "record-review", "--concept", "Query planning",
                  "--result", "incorrect", "--tested-bloom", "3")
        check("crossedBloom3: false on incorrect (no ratchet movement)",
              out.get("crossedBloom3") is False, out)


def t_snapshot():
    with tempfile.TemporaryDirectory() as root:
        proj = make_project(root, spaced_review=json.loads(json.dumps(V2_SR)))
        out = run(proj, "snapshot")
        check("snapshot: project position from state.json",
              out["project"]["currentModule"] == "Module B"
              and out["project"]["overallCompletion"] == 10, out)
        check("snapshot: cadence totals",
              out["cadence"]["totalSessions"] == 1
              and out["cadence"]["daysSinceLastSession"] == (TODAY - datetime.date(2026, 1, 1)).days,
              out["cadence"])
        check("snapshot: both seeded concepts counted and due",
              out["review"]["concepts"] == 2 and out["review"]["dueToday"] == 2,
              out["review"])
        check("snapshot: box distribution",
              out["review"]["boxDistribution"]["3"] == 1
              and out["review"]["boxDistribution"]["1"] == 1, out["review"])
        check("snapshot: legacy module masteryPct is null (display rule)",
              out["mastery"]["modules"]["Module A"]["masteryPct"] is None,
              out["mastery"])
        check("snapshot: retention rollup tiers",
              out["review"]["retentionRollup"] == {"strong": 0, "building": 1,
                                                   "needs_review": 1}
              and out["review"]["retentionConcepts"]["building"] == ["B-tree indexes"],
              out["review"])
        check("snapshot: bloom maps carried for growth trajectory",
              "initialBloomLevel" in out["project"]
              and "currentBloomLevel" in out["project"], out["project"])
        check("snapshot: blockedOnFeynman present",
              out["mastery"]["blockedOnFeynman"] == [], out["mastery"])
        check("snapshot: calibration carries no per-concept event lists",
              "overconfidentEvents" not in out["calibration"], out["calibration"])
        # Unparseable schedule is surfaced, never silently skipped.
        srdata = read_sr(proj)
        srdata["concepts"][0]["nextReview"] = "soonish"
        with open(os.path.join(proj, ".bodhi", "spaced-review.json"), "w") as f:
            json.dump(srdata, f)
        out = run(proj, "snapshot")
        check("snapshot: unparseable nextReview surfaced",
              out["review"]["unparseableDates"] == 1, out["review"])


def t_due_never_taught():
    # Reproduces the teaching-starvation bug: /learn seeds assessed concepts
    # into the Leitner system that were never taught, and /continue quizzed
    # them because `due` gave no taught/untaught signal. `due` now flags each
    # concept `neverTaught` (no reviewHistory entry with source=="teach") so
    # /continue can route first-teaching to /teach instead of /quiz.
    with tempfile.TemporaryDirectory() as root:
        proj = make_project(root)
        # Two seeded-but-untaught concepts.
        run(proj, "add-concept", "--concept", "Seeded A", "--module", "Module 1")
        run(proj, "add-concept", "--concept", "Seeded B", "--module", "Module 1")
        # A quiz review does NOT count as teaching (this is the real-data case:
        # a concept assessed high and quizzed, but never taught).
        run(proj, "record-review", "--concept", "Seeded B",
            "--result", "correct", "--tested-bloom", "4", "--source", "quiz")
        # A concept that WAS taught.
        run(proj, "add-concept", "--concept", "Taught C", "--module", "Module 1")
        run(proj, "record-review", "--concept", "Taught C",
            "--result", "correct", "--tested-bloom", "3", "--source", "teach")
        # Make all three due today (fresh concepts review tomorrow).
        yesterday = (TODAY - datetime.timedelta(days=1)).isoformat()
        srdata = read_sr(proj)
        for c in srdata["concepts"]:
            c["nextReview"] = yesterday
        with open(os.path.join(proj, ".bodhi", "spaced-review.json"), "w") as f:
            json.dump(srdata, f)
        out = run(proj, "due")
        flags = {c["name"]: c["neverTaught"] for c in out["concepts"]}
        check("due: freshly seeded concept flagged neverTaught",
              flags.get("Seeded A") is True, out)
        check("due: quizzed-but-untaught concept still neverTaught "
              "(source=quiz is not teaching)",
              flags.get("Seeded B") is True, out)
        check("due: taught concept flagged neverTaught=False",
              flags.get("Taught C") is False, out)
        check("due: neverTaughtCount rollup counts only untaught",
              out["neverTaughtCount"] == 2, out)
        # After a teach review, the flag flips. (Re-backdate: a correct review
        # pushes nextReview forward, which would drop it from the due list.)
        run(proj, "record-review", "--concept", "Seeded A",
            "--result", "correct", "--tested-bloom", "2", "--source", "teach")
        srdata = read_sr(proj)
        for c in srdata["concepts"]:
            c["nextReview"] = yesterday
        with open(os.path.join(proj, ".bodhi", "spaced-review.json"), "w") as f:
            json.dump(srdata, f)
        out = run(proj, "due")
        flags = {c["name"]: c["neverTaught"] for c in out["concepts"]}
        check("due: neverTaught clears once the concept is taught",
              flags.get("Seeded A") is False, out)
        check("due: neverTaughtCount drops after teaching",
              out["neverTaughtCount"] == 1, out)


def t_concept_tiers():
    # Follow-up F-1: the blooms-taxonomy KB declared `familiar` and `introduced`
    # tiers that no code computed, so /progress inferred one tier per module
    # from two booleans (any classified? all mastered?) and rendered a module of
    # near-mastered concepts identically to one of freshly-introduced ones.
    # `mastery` and `snapshot` now return the real per-module distribution.
    with tempfile.TemporaryDirectory() as root:
        proj = make_project(root)
        # One concept per tier, placed on the boundaries that separate them.
        concepts = [
            # mastered: all four conjuncts.
            ("mastered", 4, 4, 3, True),
            # familiar: apply rung reached AND one retrieval survived a delay.
            ("familiar-min", 3, 2, 0, False),
            # familiar, NOT mastered: every conjunct but the box. The box is
            # load-bearing on its own — high bloom + streak + Feynman is still
            # only `familiar` until retrieval survives spacing.
            ("familiar-box-short", 5, 2, 9, True),
            # introduced: classified, but below the apply rung. A high box does
            # not promote it — Bloom 2 means the apply rung was never reached.
            ("introduced-low-bloom", 2, 5, 0, False),
            # introduced: apply rung reached but box 1 — no delay survived yet.
            ("introduced-box-1", 3, 1, 0, False),
            # unclassified: no v3 writer has classified it. Not `introduced`:
            # nothing has been observed, which is why masteryPct stays null.
            ("unclassified", 0, 1, 0, False),
        ]
        for name, bloom, box, streak, feyn in concepts:
            run(proj, "add-concept", "--concept", name, "--module", "M")
        srdata = read_sr(proj)
        by_name = {c["name"]: c for c in srdata["concepts"]}
        for name, bloom, box, streak, feyn in concepts:
            c = by_name[name]
            c["bloomLevel"], c["box"] = bloom, box
            c["consecutiveCorrectAtL4Plus"], c["feynmanPassed"] = streak, feyn
        with open(os.path.join(proj, ".bodhi", "spaced-review.json"), "w") as f:
            json.dump(srdata, f, indent=2)

        expected = {"unclassified": 1, "introduced": 2, "familiar": 2, "mastered": 1}
        out = run(proj, "mastery")
        tiers = out["modules"]["M"]["tiers"]
        check("mastery: per-module tier distribution matches the KB ladder",
              tiers == expected, tiers)
        check("mastery: tiers sum to the module's concept count",
              sum(tiers.values()) == out["modules"]["M"]["concepts"], out["modules"]["M"])
        check("mastery: tiers.mastered agrees with the mastered count "
              "(one home for the four-conjunct formula)",
              tiers["mastered"] == out["modules"]["M"]["mastered"], out["modules"]["M"])
        check("mastery: unclassified is excluded from classified",
              out["modules"]["M"]["classified"] == 5, out["modules"]["M"])

        # snapshot must not fork the computation — /progress reads snapshot,
        # and a second implementation is how the rollup tiers drifted before.
        snap = run(proj, "snapshot")
        check("snapshot: reports the same tier distribution as mastery",
              snap["mastery"]["modules"]["M"]["tiers"] == expected,
              snap["mastery"]["modules"]["M"])

    # A module nobody has reached yet stays null, and every concept in it is
    # `unclassified` — never `introduced`, which would imply it was attempted.
    with tempfile.TemporaryDirectory() as root:
        proj = make_project(root, spaced_review=json.loads(json.dumps(V2_SR)))
        run(proj, "migrate-spaced-review")
        out = run(proj, "mastery")
        for mod, row in out["modules"].items():
            check(f"mastery: untouched module {mod!r} is all-unclassified",
                  row["tiers"]["unclassified"] == row["concepts"], row)
            check(f"mastery: untouched module {mod!r} keeps masteryPct null",
                  row["masteryPct"] is None, row)


def t_park():
    """park (1.16.0, honest-review #6): learner-deprioritized concepts leave
    rotation without inventing an outcome, and come back with their box."""
    with tempfile.TemporaryDirectory() as root:
        proj = make_project(root, spaced_review=json.loads(json.dumps(V2_SR)))
        run(proj, "migrate-spaced-review")
        out = run(proj, "park", "--concept", "B-tree indexes", "--note", "shipping season")
        check("park: nextReview nulled", out["concepts"]["B-tree indexes"] is None, out)
        sr = read_sr(proj)
        c = [x for x in sr["concepts"] if x["name"] == "B-tree indexes"][0]
        check("park: flag set, box/bloom/history stand",
              c["parked"] is True and c["box"] == 3
              and len(c["reviewHistory"]) == 2, c)
        last = sr["sessionHistory"][-1]
        check("park: learner-park session entry",
              last["type"] == "learner-park"
              and last["conceptsParked"] == ["B-tree indexes"]
              and last["notes"] == "shipping season", last)

        # Out of every scheduling surface, but never silently.
        out = run(proj, "due")
        check("park: excluded from due with a count",
              all(d["name"] != "B-tree indexes" for d in out["concepts"])
              and out["parkedCount"] == 1, out)
        out = run(proj, "mastery")
        check("park: out of the retention rollup, named in parked",
              "B-tree indexes" not in sum(out["retentionConcepts"].values(), [])
              and out["parked"] == ["B-tree indexes"], out)
        check("park: module tally still counts it",
              out["modules"]["Module A"]["concepts"] == 2, out)
        out = run(proj, "snapshot")
        check("park: snapshot review surface agrees",
              out["review"]["parked"] == 1
              and out["review"]["unparseableDates"] == 0
              and "B-tree indexes" not in out["review"]["dueTodayConcepts"], out)
        out = run(proj, "verify")
        check("park: verify clean on a parked concept", out["ok"] is True, out)

        # Double-park and resume-of-unparked are errors, not silent no-ops.
        run(proj, "park", "--concept", "B-tree indexes", expect_fail=True)
        run(proj, "park", "--resume", "--concept", "Query planning", expect_fail=True)

        out = run(proj, "park", "--resume", "--concept", "B-tree indexes")
        check("park: resume schedules tomorrow",
              out["concepts"]["B-tree indexes"]
              == (TODAY + datetime.timedelta(days=1)).isoformat(), out)
        sr = read_sr(proj)
        c = [x for x in sr["concepts"] if x["name"] == "B-tree indexes"][0]
        check("park: resume preserves the box", c["box"] == 3 and c["parked"] is False, c)
        check("park: resume session entry",
              sr["sessionHistory"][-1]["conceptsResumed"] == ["B-tree indexes"],
              sr["sessionHistory"][-1])


def t_profile_project_lifecycle():
    """1.16.0: the profile-* subcommands close the last hand-edit hole.

    The script constructs schema-complete entries (every PROFILE_ACTIVE_FIELDS
    key present), refreshes in place preserving unknown fields, and owns the
    active -> completed transition — the exact mutations /learn and /evaluate
    used to hand-edit.
    """
    with tempfile.TemporaryDirectory() as root:
        proj = make_project(root, spaced_review=json.loads(json.dumps(V2_SR)))
        run(proj, "migrate-spaced-review")
        # No parent profile at all -> clean error, not a stack trace.
        run(proj, "profile-add-project", "--name", "proj", "--topic", "t",
            expect_fail=True)
        with open(os.path.join(root, ".bodhi-profile.json"), "w") as f:
            json.dump({"version": 2}, f)

        # Add: creates the projects file, entry is schema-complete.
        out = run(proj, "profile-add-project", "--name", "proj",
                  "--topic", "testing", "--track-purpose", "depth")
        entry = out["entry"]
        required = {"name", "topic", "startedAt", "currentPhase",
                    "currentModule", "bloomLevel", "pace", "status",
                    "trackPurpose"}
        check("profile-add: entry schema-complete",
              required <= set(entry), out)
        check("profile-add: startedAt is today",
              entry["startedAt"] == TODAY.isoformat(), out)
        check("profile-add: defaults filled",
              entry["status"] == "active" and entry["pace"] == "steady"
              and entry["bloomLevel"] == 0, out)
        lp = os.path.join(root, ".bodhi-profile.projects.json")
        with open(lp) as f:
            data = json.load(f)
        check("profile-add: file created at version 2", data["version"] == 2)
        run(proj, "profile-add-project", "--name", "proj", "--topic", "dup",
            expect_fail=True)

        # Update: only passed fields change; unknown fields survive.
        data["activeProjects"][0]["futureField"] = "keep"
        data["customTop"] = "keep"
        with open(lp, "w") as f:
            json.dump(data, f)
        out = run(proj, "profile-update-project", "--name", "proj",
                  "--phase", "2", "--module", "Module B", "--bloom", "3")
        check("profile-update: fields refreshed",
              out["entry"]["currentPhase"] == "2"
              and out["entry"]["currentModule"] == "Module B"
              and out["entry"]["bloomLevel"] == 3, out)
        check("profile-update: unknown entry field preserved",
              out["entry"]["futureField"] == "keep", out)
        with open(lp) as f:
            check("profile-update: unknown top-level field preserved",
                  json.load(f)["customTop"] == "keep")
        run(proj, "profile-update-project", "--name", "proj", expect_fail=True)
        run(proj, "profile-update-project", "--name", "ghost", "--phase", "2",
            expect_fail=True)

        # verify accepts the script-built shape.
        out = run(proj, "verify")
        check("profile lifecycle: verify clean on script-built entries",
              out["ok"] is True, out)

        # Complete: moves the entry, finalBloomLevel defaults to bloomLevel.
        out = run(proj, "profile-complete-project", "--name", "proj")
        done = out["entry"]
        check("profile-complete: moved with today's date",
              done["completedAt"] == TODAY.isoformat()
              and out["activeProjects"] == 0
              and out["completedProjects"] == 1, out)
        check("profile-complete: finalBloomLevel from the entry",
              done["finalBloomLevel"] == 3, out)
        check("profile-complete: trackPurpose carried",
              done["trackPurpose"] == "depth", out)
        run(proj, "profile-complete-project", "--name", "proj",
            expect_fail=True)
        # A completed name cannot be re-added silently.
        run(proj, "profile-add-project", "--name", "proj", "--topic", "again",
            expect_fail=True)

        # Replace-archive variant (/learn Phase 1.5c): --status + --final-bloom.
        run(proj, "profile-add-project", "--name", "proj2", "--topic", "t2")
        out = run(proj, "profile-complete-project", "--name", "proj2",
                  "--final-bloom", "2", "--status", "archived: replaced by x")
        check("profile-complete: archive status + explicit final bloom",
              out["entry"]["finalBloomLevel"] == 2
              and out["entry"]["status"].startswith("archived"), out)
        out = run(proj, "verify")
        check("profile lifecycle: verify clean after completion",
              out["ok"] is True, out)


def t_profile_patterns():
    """profile-update-patterns: the 3+-assessments tally is pure counting —
    the script owns it (state-schema KB), the model never counts in prose."""
    with tempfile.TemporaryDirectory() as root:
        proj = make_project(root, spaced_review=json.loads(json.dumps(V2_SR)))
        run(proj, "migrate-spaced-review")
        with open(os.path.join(root, ".bodhi-profile.json"), "w") as f:
            json.dump({"version": 2, "custom": "keep"}, f)

        out = run(proj, "profile-update-patterns")
        check("patterns: no history is a clean no-op",
              out["addedChallenges"] == [] and out["addedStrengths"] == []
              and "note" in out, out)

        entry = json.dumps({"topic": "SQL", "subTopics": [
            {"name": "Query planning", "bloomLevel": 2},
            {"name": "Indexes", "bloomLevel": 4}]})
        for _ in range(2):
            run(proj, "record-assessment", "--trigger", "assess",
                "--data", entry)
        out = run(proj, "profile-update-patterns")
        check("patterns: below threshold adds nothing",
              out["addedChallenges"] == [] and out["addedStrengths"] == [], out)

        run(proj, "record-assessment", "--trigger", "evaluate",
            "--data", entry)
        out = run(proj, "profile-update-patterns")
        check("patterns: 3+ low entries -> persistent challenge",
              out["addedChallenges"] == ["Query planning"], out)
        check("patterns: 3+ high entries -> consistent strength",
              out["addedStrengths"] == ["Indexes"], out)
        with open(os.path.join(root, ".bodhi-profile.json")) as f:
            profile = json.load(f)
        check("patterns: written to the profile with fields preserved",
              profile["patterns"]["persistentChallenges"] == ["Query planning"]
              and profile["custom"] == "keep"
              and "lastUpdated" in profile, profile)

        # Re-run is append-only + deduplicated: nothing doubles.
        out = run(proj, "profile-update-patterns")
        check("patterns: re-run adds nothing (dedup)",
              out["addedChallenges"] == [] and out["addedStrengths"] == [], out)


def t_bloom_render():
    """Every emitter that returns a bloomLevel also returns the canonical
    learner-facing label + outcome clause (blooms-taxonomy KB)."""
    with tempfile.TemporaryDirectory() as root:
        proj = make_project(root, spaced_review=json.loads(json.dumps(V2_SR)))
        run(proj, "migrate-spaced-review")
        out = run(proj, "record-review", "--concept", "B-tree indexes",
                  "--result", "correct", "--tested-bloom", "3")
        check("render: record-review carries label", out["bloomLabel"] == "Apply", out)
        check("render: record-review carries outcome clause",
              out["bloomOutcome"].startswith("you can apply it"), out)
        check("render: first classification is a crossing",
              out["crossedLevel"] is True and out["crossedBloom3"] is True, out)
        out2 = run(proj, "record-review", "--concept", "B-tree indexes",
                   "--result", "correct", "--tested-bloom", "3")
        check("render: same rung again is not a crossing",
              out2["crossedLevel"] is False and out2["crossedBloom3"] is False, out2)
        out3 = run(proj, "record-review", "--concept", "B-tree indexes",
                   "--result", "correct", "--tested-bloom", "4")
        check("render: a rung above 3 is a crossing but not the Bloom-3 line",
              out3["crossedLevel"] is True and out3["crossedBloom3"] is False, out3)
        out = run(proj, "session-brief", "--concept", "Query planning")
        check("render: unclassified has no label (not a zero)",
              out["bloomLevel"] == 0 and out["bloomLabel"] is None
              and out["bloomOutcome"] == "nothing observed yet", out)
        out = run(proj, "gate-check", "--prior-module", "Module A")
        bt = [p for p in out["prerequisites"] if p["name"] == "B-tree indexes"][0]
        check("render: gate rows carry label", bt["bloomLabel"] == "Analyze", bt)
        out = run(proj, "snapshot")
        scale = out.get("bloomScale", [])
        check("render: snapshot ships the 6-rung legend",
              [r["label"] for r in scale]
              == ["Remember", "Understand", "Apply", "Analyze", "Evaluate", "Create"],
              scale)
        check("render: every rung has an outcome clause in second person",
              all(r["outcome"].startswith("you can") for r in scale), scale)


def t_gate_evidence():
    """A level reached by ONE review earns a reconfirm question, not a free
    pass; two level-3+ corrects (or Box >= 3) clear it. (1.17.0)"""
    with tempfile.TemporaryDirectory() as root:
        sr = {"version": 3, "concepts": [
            {"name": "Joins", "module": "Module A", "introduced": "2026-01-01",
             "box": 1, "bloomLevel": 0, "nextReview": "2026-01-02",
             "lastReviewed": None, "reviewHistory": []}],
            "sessionHistory": []}
        proj = make_project(root, spaced_review=sr)
        # one correct at Apply, today -> bloom 3, box 2, evidence 1
        run(proj, "record-review", "--concept", "Joins",
            "--result", "correct", "--tested-bloom", "3")
        out = run(proj, "gate-check", "--prior-module", "Module A")
        j = out["prerequisites"][0]
        check("gate: single level-3 review = reconfirm, not pass",
              j["status"] == "stale-reconfirm" and j["reason"] == "single-evidence"
              and j["evidenceAt3Plus"] == 1, j)
        check("gate: verdict offer on single evidence", out["verdict"] == "offer")
        # two level-3 corrects on record, box still below 3: evidence clears it
        sr1 = read_sr(proj)
        sr1["concepts"][0]["reviewHistory"] = [
            {"date": TODAY.isoformat(), "result": "correct", "bloomLevel": 3},
            {"date": TODAY.isoformat(), "result": "correct", "bloomLevel": 3}]
        sr1["concepts"][0]["box"] = 2
        with open(os.path.join(proj, ".bodhi", "spaced-review.json"), "w") as f:
            json.dump(sr1, f)
        out = run(proj, "gate-check", "--prior-module", "Module A")
        j = out["prerequisites"][0]
        check("gate: two level-3 corrects below box 3 = satisfied by evidence",
              j["status"] == "satisfied" and j["reason"] == "evidence"
              and j["box"] < 3 and j["evidenceAt3Plus"] == 2, j)
        # a correct graded at Understand does not count toward apply evidence
        sr2 = read_sr(proj)
        sr2["concepts"][0]["reviewHistory"] = [
            {"date": TODAY.isoformat(), "result": "correct", "bloomLevel": 3},
            {"date": TODAY.isoformat(), "result": "correct", "bloomLevel": 2}]
        sr2["concepts"][0]["box"] = 2
        with open(os.path.join(proj, ".bodhi", "spaced-review.json"), "w") as f:
            json.dump(sr2, f)
        out = run(proj, "gate-check", "--prior-module", "Module A")
        j = out["prerequisites"][0]
        check("gate: a level-2 correct is not apply evidence",
              j["status"] == "stale-reconfirm" and j["evidenceAt3Plus"] == 1, j)
        out = run(proj, "session-brief", "--concept", "Joins")
        check("brief: exposes evidenceAt3Plus", out["evidenceAt3Plus"] == 1, out)



def t_gate_evidence_reset():
    """Apply-rung evidence counts only since the most recent miss (1.18.0).
    Before: two old corrects kept a prerequisite `satisfied` through three
    straight misses and through an explicit /forget."""
    with tempfile.TemporaryDirectory() as root:
        def gate(proj):
            out = run(proj, "gate-check", "--prior-module", "Module A")
            return out["prerequisites"][0]

        def write_sr(proj, sr):
            with open(os.path.join(proj, ".bodhi", "spaced-review.json"), "w") as f:
                json.dump(sr, f)
        sr = {"version": 3, "concepts": [
            {"name": "Joins", "module": "Module A", "introduced": "2026-01-01",
             "box": 2, "bloomLevel": 3, "nextReview": TODAY.isoformat(),
             "lastReviewed": TODAY.isoformat(),
             "reviewHistory": [
                 {"date": "2026-01-02", "result": "correct", "bloomLevel": 3},
                 {"date": "2026-01-05", "result": "correct", "bloomLevel": 3}]}],
            "sessionHistory": []}
        proj = make_project(root, spaced_review=sr)
        j = gate(proj)
        check("reset: baseline two corrects = satisfied/evidence",
              j["status"] == "satisfied" and j["reason"] == "evidence", j)
        # (a) three straight misses after the evidence: not satisfied any more
        for _ in range(3):
            run(proj, "record-review", "--concept", "Joins",
                "--result", "incorrect", "--tested-bloom", "3")
        j = gate(proj)
        check("reset: three misses after old evidence = reconfirm, evidence 0",
              j["status"] == "stale-reconfirm" and j["reason"] == "single-evidence"
              and j["evidenceAt3Plus"] == 0 and j["box"] == 1, j)
        # (c) the other side of the bound: two fresh corrects after the misses
        run(proj, "record-review", "--concept", "Joins",
            "--result", "correct", "--tested-bloom", "3")
        j = gate(proj)
        check("reset: one fresh correct after a miss = still reconfirm",
              j["status"] == "stale-reconfirm" and j["evidenceAt3Plus"] == 1, j)
        run(proj, "record-review", "--concept", "Joins",
            "--result", "correct", "--tested-bloom", "3")
        j = gate(proj)
        check("reset: two fresh corrects after a miss = satisfied again",
              j["status"] == "satisfied" and j["evidenceAt3Plus"] == 2, j)
        # (b) an explicit /forget resets the count too
        run(proj, "forget", "--concept", "Joins")
        j = gate(proj)
        check("reset: /forget after evidence = reconfirm, not satisfied",
              j["status"] == "stale-reconfirm" and j["evidenceAt3Plus"] == 0, j)
        # (d) deferred entries are scheduling, not observations: ignored
        sr2 = read_sr(proj)
        sr2["concepts"][0]["reviewHistory"] = [
            {"date": "2026-01-02", "result": "correct", "bloomLevel": 3},
            {"date": TODAY.isoformat(), "deferred": True, "note": "not reached"},
            {"date": TODAY.isoformat(), "result": "correct", "bloomLevel": 3}]
        sr2["concepts"][0]["box"] = 2
        sr2["concepts"][0]["lastReviewed"] = TODAY.isoformat()
        write_sr(proj, sr2)
        j = gate(proj)
        check("reset: a deferred entry neither counts nor resets",
              j["status"] == "satisfied" and j["evidenceAt3Plus"] == 2, j)
        # sub-3 fallthrough also ignores deferred entries
        sr2["concepts"][0]["bloomLevel"] = 2
        sr2["concepts"][0]["box"] = 3
        sr2["concepts"][0]["reviewHistory"].append(
            {"date": TODAY.isoformat(), "deferred": True})
        write_sr(proj, sr2)
        j = gate(proj)
        check("reset: apply-equivalent fallthrough skips deferred entries",
              j["status"] == "apply-equivalent", j)


def t_validation_on_load():
    """Drift that `verify` flags must fail every subcommand the same clean
    way — {"ok": false, "error": ...} naming the repair — never a traceback
    from whichever command happened to compute on the bad field (1.18.0)."""
    with tempfile.TemporaryDirectory() as root:
        sr = json.loads(json.dumps(V2_SR))
        sr["version"] = 3
        for c in sr["concepts"]:
            c.update({"bloomLevel": 3, "feynmanPassed": False,
                      "consecutiveCorrectAtL4Plus": 0})
        sr["concepts"][0]["box"] = "three"
        proj = make_project(root, spaced_review=sr)
        for argv in (("due",), ("mastery",), ("snapshot",),
                     ("record-review", "--concept", "B-tree indexes",
                      "--result", "correct", "--tested-bloom", "3")):
            out = run(proj, *argv, expect_fail=True)
            check(f"load: string box fails cleanly in {argv[0]}",
                  out.get("ok") is False and "box" in out.get("error", "")
                  and "verify" in out.get("error", ""), out)
            # "three" is not a number: the advice must not name normalize,
            # which cannot repair it (1.18.x: the load-path advice claimed a
            # repair normalize did not perform)
            check(f"load: unrepairable box does not promise normalize in {argv[0]}",
                  "normalize" not in out.get("error", ""), out)
        out = run(proj, "verify", expect_fail=True)
        check("verify: string box reported, not raised",
              out.get("ok") is False and any("box" in e for e in out["errors"]), out)

        # null name: verify reports it; a subcommand dies cleanly
        sr["concepts"][0]["box"] = 2
        sr["concepts"][0]["name"] = None
        with open(os.path.join(proj, ".bodhi", "spaced-review.json"), "w") as f:
            json.dump(sr, f)
        out = run(proj, "verify", expect_fail=True)
        check("verify: null concept name reported, not raised",
              out.get("ok") is False and any("name" in e for e in out["errors"]), out)
        out = run(proj, "due", expect_fail=True)
        check("load: null name fails cleanly", out.get("ok") is False
              and "name" in out.get("error", ""), out)
        # list-typed state.json: verify reports; gate-check dies cleanly
        with open(os.path.join(proj, ".bodhi", "state.json"), "w") as f:
            json.dump(["not", "an", "object"], f)
        out = run(proj, "verify", expect_fail=True)
        check("verify: list-typed state.json reported, not raised",
              out.get("ok") is False and any("state.json" in e for e in out["errors"]), out)
        # int currentModule (a normalize-class drift) dies cleanly in gate-check
        sr["concepts"][0]["name"] = "B-tree indexes"
        with open(os.path.join(proj, ".bodhi", "spaced-review.json"), "w") as f:
            json.dump(sr, f)
        with open(os.path.join(proj, ".bodhi", "state.json"), "w") as f:
            json.dump({"version": 2, "currentModule": 7, "sessionDates": []}, f)
        out = run(proj, "gate-check", "--prior-module", "Module A", expect_fail=True)
        check("load: int currentModule fails cleanly in gate-check",
              out.get("ok") is False and "currentModule" in out.get("error", "")
              and "normalize" in out.get("error", ""), out)
        # strict dates: an int or prose lastReviewed is unparseable, not a
        # wrong daysSinceLastReview
        with open(os.path.join(proj, ".bodhi", "state.json"), "w") as f:
            json.dump({"version": 2, "currentModule": "Module A", "sessionDates": []}, f)
        sr["concepts"][0]["lastReviewed"] = 20260601
        sr["concepts"][1]["lastReviewed"] = "June 1"
        with open(os.path.join(proj, ".bodhi", "spaced-review.json"), "w") as f:
            json.dump(sr, f)
        out = run(proj, "session-brief", "--concept", "B-tree indexes")
        check("dates: int lastReviewed yields no daysSinceLastReview",
              out.get("daysSinceLastReview") is None, out)
        out = run(proj, "session-brief", "--concept", "Query planning")
        check("dates: prose lastReviewed yields no daysSinceLastReview",
              out.get("daysSinceLastReview") is None, out)
        # a date-time is still a date
        sr["concepts"][0]["lastReviewed"] = TODAY.isoformat() + "T10:00:00"
        with open(os.path.join(proj, ".bodhi", "spaced-review.json"), "w") as f:
            json.dump(sr, f)
        out = run(proj, "session-brief", "--concept", "B-tree indexes")
        check("dates: ISO date-time still parses", out.get("daysSinceLastReview") == 0, out)
        # profile projects list: a non-object entry dies cleanly
        with open(os.path.join(root, ".bodhi-profile.json"), "w") as f:
            json.dump({"version": 2, "cumulativeStats": {}}, f)
        with open(os.path.join(root, ".bodhi-profile.projects.json"), "w") as f:
            json.dump({"version": 2, "activeProjects": ["oops"], "completedProjects": []}, f)
        out = run(proj, "profile-update-project", "--name", "x", "--phase", "1", expect_fail=True)
        check("load: non-object profile entry fails cleanly",
              out.get("ok") is False and "activeProjects[0]" in out.get("error", ""), out)


def t_write_keeps_file_mode():
    """The atomic write (mkstemp + os.replace) must not chmod the learner's
    tracking files to owner-only (1.18.x): mkstemp creates 0600 and the
    rename carried that mode over, so the first script write silently made
    a synced or shared project unreadable to everyone else."""
    import stat
    with tempfile.TemporaryDirectory() as root:
        sr = json.loads(json.dumps(V2_SR))
        proj = make_project(root, spaced_review=sr)
        srp = os.path.join(proj, ".bodhi", "spaced-review.json")
        sp = os.path.join(proj, ".bodhi", "state.json")
        os.chmod(srp, 0o664)
        os.chmod(sp, 0o644)
        run(proj, "record-review", "--concept", "B-tree indexes",
            "--result", "correct", "--tested-bloom", "3")
        run(proj, "touch-state", "--activity", "mode check")
        check("write: existing 0664 spaced-review.json keeps its mode",
              stat.S_IMODE(os.stat(srp).st_mode) == 0o664,
              oct(stat.S_IMODE(os.stat(srp).st_mode)))
        check("write: existing 0644 state.json keeps its mode",
              stat.S_IMODE(os.stat(sp).st_mode) == 0o644,
              oct(stat.S_IMODE(os.stat(sp).st_mode)))
        # a file the script creates gets the umask default, not mkstemp's 0600
        old = os.umask(0o022)
        try:
            os.remove(srp)
            run(proj, "add-concept", "--concept", "Fresh", "--module", "Module A")
            check("write: a created file is not owner-only",
                  stat.S_IMODE(os.stat(srp).st_mode) == 0o644,
                  oct(stat.S_IMODE(os.stat(srp).st_mode)))
        finally:
            os.umask(old)


def t_date_travel():
    """BODHI_TODAY pins the script's clock, which makes the Leitner schedule
    testable past same-day for the first time: a promotion sets nextReview
    at the box's interval, `due` stays quiet until that day and lists the
    concept from it, and the streak counts consecutive pinned days."""
    with tempfile.TemporaryDirectory() as root:
        sr = json.loads(json.dumps(V2_SR))
        proj = make_project(root, spaced_review=sr)
        # Box 3 -> 4 on 2026-01-01: next review in 14 days (BOX_INTERVALS[4])
        out = run(proj, "record-review", "--concept", "B-tree indexes",
                  "--result", "correct", "--tested-bloom", "4", on="2026-01-01")
        check("travel: promotion recorded on the pinned day",
              out.get("box") == "3 -> 4", out)
        c = next(x for x in read_sr(proj)["concepts"] if x["name"] == "B-tree indexes")
        check("travel: nextReview is the box-4 interval from the pinned day",
              c["nextReview"] == "2026-01-15" and c["lastReviewed"] == "2026-01-01", c)
        check("travel: history entry carries the pinned date",
              c["reviewHistory"][-1]["date"] == "2026-01-01", c["reviewHistory"][-1])
        names = lambda o: [d["name"] for d in o.get("concepts", [])]
        check("travel: not due the day before the interval ends",
              "B-tree indexes" not in names(run(proj, "due", on="2026-01-14")))
        check("travel: due on the interval day",
              "B-tree indexes" in names(run(proj, "due", on="2026-01-15")))
        check("travel: overdue after it",
              "B-tree indexes" in names(run(proj, "due", on="2026-02-01")))
        # a miss on the due day demotes and reschedules at the box-1 interval
        out = run(proj, "record-review", "--concept", "B-tree indexes",
                  "--result", "incorrect", "--tested-bloom", "3", on="2026-01-15")
        c = next(x for x in read_sr(proj)["concepts"] if x["name"] == "B-tree indexes")
        check("travel: a miss lands at box 1, review the next day",
              c["box"] == 1 and c["nextReview"] == "2026-01-16", c)
        # streak: consecutive pinned days count, a gap resets
        for day in ("2026-03-01", "2026-03-02", "2026-03-03"):
            run(proj, "touch-state", "--activity", "x", on=day)
        check("travel: three consecutive days -> streak 3",
              read_state(proj)["currentStreak"] == 3, read_state(proj))
        run(proj, "touch-state", "--activity", "x", on="2026-03-10")
        check("travel: a gap resets the streak to 1",
              read_state(proj)["currentStreak"] == 1, read_state(proj))
        # a malformed pin fails loudly, never shifts dates silently
        out = run(proj, "due", on="yesterday", expect_fail=True)
        check("travel: malformed BODHI_TODAY fails cleanly",
              out.get("ok") is False and "BODHI_TODAY" in out.get("error", ""), out)


def t_shape_rules_agree():
    """One shape table behind load-time validation and `verify` (1.18.x):
    a value must not pass the Stop hook's `verify` and then kill every other
    subcommand — or the reverse. Booleans are not ints on either path;
    numeric strings and string booleans are the lossless repairs `normalize`
    performs, and the load-path advice names normalize exactly when it can."""
    def v3_sr():
        sr = json.loads(json.dumps(V2_SR))
        sr["version"] = 3
        for c in sr["concepts"]:
            c.update({"bloomLevel": 3, "feynmanPassed": False,
                      "consecutiveCorrectAtL4Plus": 0})
        return sr

    def write_sr(proj, sr):
        with open(os.path.join(proj, ".bodhi", "spaced-review.json"), "w") as f:
            json.dump(sr, f)

    with tempfile.TemporaryDirectory() as root:
        proj = make_project(root, spaced_review=v3_sr())
        # bool box / bloomLevel / counter: both paths reject, neither offers normalize
        for field, value in (("box", True), ("bloomLevel", False),
                             ("consecutiveCorrectAtL4Plus", True)):
            sr = v3_sr()
            sr["concepts"][0][field] = value
            write_sr(proj, sr)
            v = run(proj, "verify", expect_fail=True)
            check(f"verify: bool {field} is not an int",
                  v.get("ok") is False and any(field in e for e in v["errors"]), v)
            check(f"verify: bool {field} does not promise normalize",
                  not any(field in e and "normalize" in e for e in v["errors"]), v)
            d = run(proj, "due", expect_fail=True)
            check(f"load: bool {field} fails cleanly",
                  d.get("ok") is False and field in d.get("error", "")
                  and "normalize" not in d.get("error", ""), d)
        # feynmanPassed as a string: rejected on both paths
        sr = v3_sr()
        sr["concepts"][0]["feynmanPassed"] = "yes"
        write_sr(proj, sr)
        v = run(proj, "verify", expect_fail=True)
        check("verify: string feynmanPassed rejected",
              v.get("ok") is False and any("feynmanPassed" in e for e in v["errors"]), v)
        d = run(proj, "due", expect_fail=True)
        check("load: string feynmanPassed fails cleanly",
              d.get("ok") is False and "feynmanPassed" in d.get("error", ""), d)
        # numeric strings and string booleans: verify names normalize, load
        # names normalize, normalize repairs, verify passes, values are typed
        sr = v3_sr()
        sr["concepts"][0]["box"] = "3"
        sr["concepts"][0]["bloomLevel"] = " 4 "
        sr["concepts"][0]["feynmanPassed"] = "true"
        sr["concepts"][1]["consecutiveCorrectAtL4Plus"] = "2"
        write_sr(proj, sr)
        v = run(proj, "verify", expect_fail=True)
        check("verify: numeric-string box names normalize",
              any("box" in e and "normalize" in e for e in v["errors"]), v)
        d = run(proj, "due", expect_fail=True)
        check("load: numeric-string box names normalize",
              d.get("ok") is False and "normalize" in d.get("error", ""), d)
        n = run(proj, "normalize")
        check("normalize: repairs typed fields",
              n.get("action") == "normalized"
              and sum(1 for ch in n["changes"] if "->" in ch) >= 4, n)
        after = read_sr(proj)
        c0, c1 = after["concepts"][0], after["concepts"][1]
        check("normalize: box/bloomLevel/feynmanPassed/counter are typed",
              c0["box"] == 3 and c0["bloomLevel"] == 4 and c0["feynmanPassed"] is True
              and c1["consecutiveCorrectAtL4Plus"] == 2, after)
        check("normalize: repaired file verifies clean", run(proj, "verify").get("ok") is True)
        check("normalize: second run is a noop", run(proj, "normalize").get("action") == "noop")
        check("normalize: non-canonical fields survive",
              c0.get("precisionGap") == "confuses clustered vs non-clustered", after)


def t_write_on_v2_backs_up():
    """A mutating write on a v1/v2 file must make the pre-v3 backup migrate
    promises before stamping version 3 (1.18.0). Before: the first
    record-session upgraded the file silently and migrate then said noop."""
    with tempfile.TemporaryDirectory() as root:
        proj = make_project(root, spaced_review=json.loads(json.dumps(V2_SR)))
        backup = os.path.join(proj, ".bodhi", ".pre-1.10-backup", "spaced-review.json")
        out = run(proj, "record-session", "--type", "quiz",
                  "--data", '{"questionsAsked": 1}')
        check("v2 write: backup created before the first v3 write",
              os.path.exists(backup), out)
        check("v2 write: output reports migratedFromVersion 2",
              out.get("migratedFromVersion") == 2 and out.get("backup") == backup, out)
        with open(backup) as f:
            saved = json.load(f)
        check("v2 write: backup is the untouched v2 file",
              saved["version"] == 2 and "bloomLevel" not in saved["concepts"][0], saved)
        check("v2 write: live file is now v3", read_sr(proj)["version"] == 3)
        # a second write neither re-reports nor overwrites the backup
        out = run(proj, "record-review", "--concept", "B-tree indexes",
                  "--result", "correct", "--tested-bloom", "3")
        check("v2 write: second write does not report a migration",
              "migratedFromVersion" not in out, out)
        with open(backup) as f:
            check("v2 write: backup untouched by later writes",
                  json.load(f) == saved)
        out = run(proj, "migrate-spaced-review")
        check("v2 write: migrate afterwards is an honest noop",
              out["action"] == "noop" and os.path.exists(backup), out)
        # One upgrade, two entry points (1.18.x): the write path must leave
        # the same file migrate would have — marker included — so "noop"
        # from migrate afterwards is true, not a half-upgraded file it
        # cannot see.
        marker = os.path.join(proj, ".bodhi", ".migration-1.10.md")
        check("v2 write: migration marker written by the write path",
              os.path.exists(marker))
        with open(marker) as f:
            check("v2 write: marker names the write path and the version",
                  "write" in f.read() and "v2 -> v3" in open(marker).read())
        write_path_keys = [sorted(c) for c in read_sr(proj)["concepts"]]
    with tempfile.TemporaryDirectory() as root:
        proj = make_project(root, spaced_review=json.loads(json.dumps(V2_SR)))
        run(proj, "migrate-spaced-review")
        migrate_keys = [sorted(c) for c in read_sr(proj)["concepts"]]
        check("v2 write: write-path upgrade has the same key set as migrate",
              write_path_keys == migrate_keys, (write_path_keys, migrate_keys))
        check("v2 write: both paths add question/lastResult",
              all("question" in c and "lastResult" in c for c in read_sr(proj)["concepts"]))


def t_script_hygiene():
    """1.18.0 small contracts: read-only subcommands never create the lock
    file; defer rejects a non-positive --days; a review that auto-creates a
    concept under a module nothing has seen flags it."""
    with tempfile.TemporaryDirectory() as root:
        proj = make_project(root, spaced_review=json.loads(json.dumps(V2_SR)))
        run(proj, "migrate-spaced-review")
        lock = os.path.join(proj, ".bodhi", ".bodhi-state.lock")
        if os.path.exists(lock):
            os.unlink(lock)
        for argv in (("due",), ("mastery",), ("snapshot",), ("verify",),
                     ("session-brief", "--concept", "B-tree indexes"),
                     ("gate-check", "--prior-module", "Module A")):
            run(proj, *argv)
        check("hygiene: read-only subcommands leave no lock file behind",
              not os.path.exists(lock))
        run(proj, "record-session", "--type", "quiz", "--data", "{}")
        check("hygiene: a writer creates the lock file", os.path.exists(lock))
        out = run(proj, "defer", "--concept", "B-tree indexes", "--days", "-5",
                  expect_fail=True)
        check("hygiene: defer --days -5 is an error, not +1",
              out.get("ok") is False and "--days" in out.get("error", ""), out)
        out = run(proj, "defer", "--concept", "B-tree indexes", "--days", "0",
                  expect_fail=True)
        check("hygiene: defer --days 0 is an error", out.get("ok") is False, out)
        out = run(proj, "record-review", "--concept", "Window functions",
                  "--result", "correct", "--tested-bloom", "2",
                  "--module", "Module A")
        check("hygiene: auto-create under a known module is not flagged",
              out["created"] is True and out["newModule"] is False, out)
        out = run(proj, "record-review", "--concept", "CTEs",
                  "--result", "correct", "--tested-bloom", "2",
                  "--module", "Modul A")
        check("hygiene: auto-create under an unseen module is flagged",
              out["created"] is True and out["newModule"] is True, out)
        out = run(proj, "record-review", "--concept", "CTEs",
                  "--result", "correct", "--tested-bloom", "2")
        check("hygiene: an existing concept carries no newModule flag",
              "newModule" not in out, out)
        out = run(proj, "forget", "--concept", "CTEs")
        la = read_state(proj)["lastActivity"]
        check("hygiene: forget lastActivity within LAST_ACTIVITY_MAX", len(la) <= 120, la)


def t_mastery_snapshot_agree():
    """`mastery` and `snapshot.mastery/review` are one computation
    (review_rollup); they must agree on every shared key (1.18.0)."""
    with tempfile.TemporaryDirectory() as root:
        sr = json.loads(json.dumps(V2_SR))
        proj = make_project(root, spaced_review=sr)
        run(proj, "migrate-spaced-review")
        run(proj, "add-concept", "--concept", "Window functions", "--module", "Module B")
        for _ in range(3):
            run(proj, "record-review", "--concept", "Window functions",
                "--result", "correct", "--tested-bloom", "4")
        run(proj, "park", "--concept", "Query planning")
        m = run(proj, "mastery")
        snap = run(proj, "snapshot")
        check("agree: modules", m["modules"] == snap["mastery"]["modules"])
        check("agree: retentionRollup", m["retentionRollup"] == snap["review"]["retentionRollup"])
        check("agree: retentionConcepts", m["retentionConcepts"] == snap["review"]["retentionConcepts"])
        check("agree: dueToday", m["dueToday"] == snap["review"]["dueTodayConcepts"])
        check("agree: dueThisWeek", m["dueThisWeek"] == snap["review"]["dueThisWeekConcepts"])
        check("agree: blockedOnFeynman", m["blockedOnFeynman"] == snap["mastery"]["blockedOnFeynman"])
        check("agree: parked", len(m.get("parked", [])) == snap["review"]["parked"] == 1, (m.get("parked"), snap["review"]["parked"]))
        check("agree: boxDistribution excludes parked",
              sum(snap["review"]["boxDistribution"].values()) == 2, snap["review"]["boxDistribution"])


def t_revision_brief():
    """revision-brief: today's studied concepts, the sheet to write, and
    whether one exists (1.18.0). Seeding and assessing write no review, so
    those days need no sheet."""
    with tempfile.TemporaryDirectory() as root:
        proj = make_project(root, spaced_review=json.loads(json.dumps(V2_SR)))
        run(proj, "migrate-spaced-review")
        out = run(proj, "revision-brief")
        check("brief: nothing studied today -> sessionToday false",
              out["sessionToday"] is False and out["concepts"] == [], out)
        run(proj, "add-concept", "--concept", "Window functions", "--module", "Module B")
        out = run(proj, "revision-brief")
        check("brief: a concept introduced today counts as studied",
              out["sessionToday"] is True
              and [c["name"] for c in out["concepts"]] == ["Window functions"], out)
        run(proj, "record-review", "--concept", "B-tree indexes",
            "--result", "partial", "--tested-bloom", "3", "--source", "quiz")
        run(proj, "record-review", "--concept", "Query planning",
            "--result", "correct", "--tested-bloom", "3", "--source", "teach")
        run(proj, "defer", "--concept", "Window functions", "--days", "2")
        out = run(proj, "revision-brief")
        names = [c["name"] for c in out["concepts"]]
        check("brief: taught concept sorts first and names the file",
              names[0] == "Query planning"
              and out["suggestedFile"] == f"revision/{TODAY.isoformat()}-query-planning.md", out)
        qp = out["concepts"][0]
        check("brief: rows carry results, source, outcome clause, next review",
              qp["resultsToday"] == ["correct"] and qp["sourcesToday"] == ["teach"]
              and qp["bloomOutcome"].startswith("you can") and qp["nextReview"], qp)
        check("brief: a deferral is not a study event",
              "Window functions" in names and
              next(c for c in out["concepts"] if c["name"] == "Window functions")["resultsToday"] == [],
              out)
        check("brief: no sheet yet", out["existing"] == [], out)
        os.makedirs(os.path.join(proj, "revision"))
        with open(os.path.join(proj, "revision", f"{TODAY.isoformat()}-query-planning.md"), "w") as f:
            f.write("# Revision\n")
        out = run(proj, "revision-brief")
        check("brief: today's sheet is reported for appending",
              out["existing"] == [f"revision/{TODAY.isoformat()}-query-planning.md"], out)
        check("brief: slugify", run(proj, "revision-brief")["suggestedFile"].endswith("-query-planning.md"))
        lock = os.path.join(proj, ".bodhi", ".bodhi-state.lock")
        if os.path.exists(lock):
            os.unlink(lock)
        run(proj, "revision-brief")
        check("brief: read-only (no lock file created)", not os.path.exists(lock))


def t_due_shape():
    """`due` is the surface skills narrate from: it carries dueSince /
    overdueDays / bloomOutcome / priority and never a box or Bloom number
    (1.18.0 — a Fable run read box: 1 straight into learner-facing text)."""
    with tempfile.TemporaryDirectory() as root:
        sr = json.loads(json.dumps(V2_SR))
        proj = make_project(root, spaced_review=sr)
        run(proj, "migrate-spaced-review")
        out = run(proj, "due")
        rows = out["concepts"]
        check("due: rows carry no box/bloomLevel numbers",
              rows and all("box" not in r and "bloomLevel" not in r and "_sort" not in r for r in rows), rows)
        check("due: priority is the rank in review order",
              [r["priority"] for r in rows] == list(range(1, len(rows) + 1)), rows)
        check("due: box-1 miss ranks before the box-3 concept",
              rows[0]["name"] == "Query planning", rows)
        check("due: dueSince + overdueDays + bloomOutcome present",
              all(r["dueSince"] and isinstance(r["overdueDays"], int)
                  and r["bloomOutcome"] for r in rows), rows)

def main():
    for t in (t_migrate, t_record_review, t_sessions_and_forget,
              t_touch_state_and_profile, t_gate_check,
              t_mastery_due_calibration, t_verify,
              t_retry_and_relearning, t_partial_breaks_streak,
              t_touch_state_profile_bump,
              t_data_reserved_keys, t_migrate_stale_backup,
              t_forget_comma_names, t_robustness, t_concurrency,
              t_history_cap, t_mastery_blocked_on_feynman,
              t_box_before, t_retention, t_export_anonymized,
              t_defer, t_verify_flags_drift, t_normalize, t_last_activity_threshold,
              t_profile_project_list_shape,
              t_session_brief, t_crossed_bloom3, t_snapshot,
              t_due_never_taught, t_concept_tiers,
              t_profile_project_lifecycle, t_profile_patterns, t_park,
              t_bloom_render, t_gate_evidence,
              t_gate_evidence_reset, t_validation_on_load, t_shape_rules_agree,
              t_write_keeps_file_mode, t_date_travel,
              t_write_on_v2_backs_up, t_script_hygiene,
              t_mastery_snapshot_agree, t_revision_brief,
              t_due_shape):
        print(f"-- {t.__name__}")
        try:
            t()
        except Exception as e:  # one crashed test must not hide the summary
            global FAIL
            FAIL += 1
            print(f"FAIL  {t.__name__} crashed: {type(e).__name__}: "
                  f"{str(e).strip().splitlines()[0] if str(e).strip() else ''}")
    print(f"\n{PASS} passed, {FAIL} failed")
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
