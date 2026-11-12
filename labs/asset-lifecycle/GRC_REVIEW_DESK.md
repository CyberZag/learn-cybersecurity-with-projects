# AI-assisted GRC review desk

A security questionnaire asks who reviews access. The only available review covers two of eight fictional accounts. This project helps an analyst find that review, see exactly what is missing, and prepare a follow-up.

## Two workflows

1. **Evidence register.** Run the existing synthetic workpaper checks and list the control, NIST CSF 2.0 reference, evidence scope, owner, gaps and next action. Each case also has an illustrative SOC 2 discussion theme. This exercise makes no formal mapping or attestation claim.
2. **Local AI questionnaire routing.** Give the assistant one fictional question. An optional local language model proposes one ID from the three supplied objectives or UNKNOWN. Python then supplies the evidence from the workpaper. Extra fields and unknown IDs are rejected. A recognized but irrelevant choice can still pass validation, so review each match and its scope before using it.

## Run

From `labs/asset-lifecycle`, use Python 3.10+ and the standard library:

```sh
python grc_assistant.py
python grc_assistant.py --as-of 2027-01-10
python -m unittest test_grc_assistant -v
```

For the model-assisted workflow, use an already running Ollama server on the local computer and an installed chat model. Substitute its name below. The program sends only the question and synthetic objectives to the fixed loopback endpoint. It never installs models, edits accounts or sends questionnaire responses.

```sh
python grc_assistant.py --ask "Who reviews permissions for the eight fictional accounts?" --model YOUR_LOCAL_MODEL
```

## Example and reviewer exercise

In the assistant's local model test, the example question selected LAB-ACCESS, linked to PR.AA-05. The evidence record had three gaps: missing owner, unrecorded review and scope mismatch. The tool requested evidence covering all eight accounts. The default register produced two evidence requests and one case ready for manual testing. Neither outcome establishes operating effectiveness.

Try a question combining access and recovery. Compare the suggested objective with both workpapers and document when you would route the question manually. Then advance the review date to see how stale evidence changes the queue. Track your own observations separately.

The assistant wrote and tested the code and generated the example using fictional records. The project builds on [the control workpapers](CONTROL_WORKPAPERS.md). Model choice and inference settings can affect routing. Framework references: [NIST CSF 2.0](https://doi.org/10.6028/NIST.CSWP.29) and [AICPA Trust Services Criteria](https://www.aicpa-cima.com/resources/download/2017-trust-services-criteria-with-revised-points-of-focus-2022).
