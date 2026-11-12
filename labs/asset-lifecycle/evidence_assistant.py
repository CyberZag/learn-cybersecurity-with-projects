"""Retrieve evidence from the bundled, fictional patch review. Python 3.10+."""
import argparse
import json
import math
import re
from collections import Counter
from pathlib import Path

from patch_coverage import reconcile

HERE = Path(__file__).resolve().parent
STOP = set("a an the are is how many of to in have which what do devices device we for".split())
TOPICS = {
    "installed": "confirmed installed patched verified successful",
    "pending": "pending waiting queued",
    "failed": "failed failure unsuccessful",
    "no target evidence": "missing absent no target evidence offline coverage gap",
    "stale evidence": "stale outdated old evidence freshness",
    "conflicting reports": "conflict conflicting contradictory inconsistent reports",
}


def tokens(text):
    return [word for word in re.findall(r"[a-z0-9]+", text.lower()) if word not in STOP]


def review(question, report):
    """Rank topics by TF-IDF cosine similarity, then quote the matching evidence."""
    if not tokens(question):
        return {"status": "insufficient evidence"}
    docs = {key: Counter(tokens(words)) for key, words in TOPICS.items()}
    query = Counter(tokens(question))
    vocabulary = set(query).union(*docs.values())
    weights = {w: 1 + math.log((len(docs) + 1) /
               (1 + sum(w in doc for doc in docs.values()))) for w in vocabulary}

    def norm(vector):
        return math.sqrt(sum((count * weights[w]) ** 2 for w, count in vector.items()))

    scores = {key: sum(query[w] * count * weights[w] ** 2 for w, count in doc.items())
              / (norm(query) * norm(doc)) for key, doc in docs.items()}
    first, second = sorted(scores, key=scores.get, reverse=True)[:2]
    if scores[first] < 0.20 or scores[first] - scores[second] < 0.08:
        return {"status": "insufficient evidence"}
    rows = [row for row in report["devices"] if row["result"] == first]
    return {"status": "candidate evidence for human review", "matched_topic": first,
            "target_update": report["target_update"], "as_of": report["as_of"],
            "matched_count": len(rows), "active_devices": report["active_devices"],
            "source": "patch_coverage.reconcile / devices", "evidence": rows}


def sample_report():
    def read(name):
        return json.loads((HERE / name).read_text(encoding="utf-8"))
    return reconcile(read("sample_data.json"), read("patch_snapshot.json"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("question", help="Describe one patch evidence category")
    parser.add_argument("--prompt", action="store_true", help="Export a grounded analyst prompt")
    args = parser.parse_args()
    result = review(args.question, sample_report())
    if args.prompt and "evidence" in result:
        result = {"instruction": "Summarize this fictional category. Cite asset IDs from evidence. "
                  "State the cutoff and scope. Treat missing evidence as unknown. "
                  "Leave remediation decisions to the reviewer.", "context": result}
    print(json.dumps(result, indent=2))
