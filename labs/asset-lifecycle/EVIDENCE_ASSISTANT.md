# Patch evidence assistant

An analyst asks “Which devices have stale evidence?” This offline retrieval assistant selects a patch-status category and returns the fictional asset IDs and timestamps behind the count. It uses TF-IDF cosine similarity over six curated topic descriptions. The counts come directly from the existing [patch reconciliation lab](PATCH_COVERAGE.md).

## Run the exercise

From `labs/asset-lifecycle` with Python 3.10 or later:

```sh
python evidence_assistant.py "Which devices have stale evidence?"
python evidence_assistant.py "Which devices are patched?" --prompt
python evidence_assistant.py "rotate database passwords"
python -m unittest test_evidence_assistant -v
```

The second command creates a structured prompt with instructions, the reporting cutoff, scope and matching evidence. A reviewer can compare any resulting summary against those rows. All processing in this tool is local. It makes no model calls and takes no action on devices.

## Interpret the output

With the bundled snapshot, “Which devices are patched?” retrieves three confirmed installations among 18 active devices. It does not establish the status of devices outside the inventory. The unrelated password question returns `insufficient evidence`.

The ranker retrieves one topic at a time. Its scores measure word overlap, not probability or understanding. Negation and complex questions can retrieve the wrong category: check `matched_topic` and rephrase before using the evidence. Thresholds are illustrative and have not been validated on production data.

**Practice:** Try a paraphrase, an out-of-scope question and a question covering two statuses. Record the expected category before running each query. If you change a synonym or threshold, rerun the tests and record which results changed.

**Attribution:** The assistant authored and tested this educational tool using synthetic data. Personal learner results can be recorded separately.
