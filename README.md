![FEEHO Employee](docs/assets/banner.png)

# FEEHO Employee

**Portable AI employee packages with explicit permissions and contract-based acceptance tests.**

[中文说明](README.zh-CN.md) · [Quick start](#quick-start) · [Architecture](#how-it-works) · [Commercial boundary](COMMERCIAL.md)

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-cf2634)](LICENSE) [![Status](https://img.shields.io/badge/status-alpha-orange)](CHANGELOG.md)

FEEHO Employee is a **model-agnostic contract toolkit** for turning a job objective into a portable employee package, validating its rules and permissions, and evaluating real agent results against explicit acceptance cases.

A sentence can create a draft. It cannot make someone ready for work. Enterprise rules, permission boundaries, handoffs, external results and human review are still required.

## Why it exists

General agent tools often stop at a prompt and a tool list. FEEHO separates four concerns:

- **Role**: what the job is accountable for.
- **Boundaries**: what may be read, what needs approval and what is denied.
- **Handoffs**: who handles missing rules, exceptions and timeouts.
- **Evidence**: how actual outputs and tool traces pass or fail acceptance contracts.

## How it works

![Architecture](docs/assets/architecture.png)

1. `draft` scaffolds a deterministic, generic employee package. It does **not** call a model.
2. `validate` checks metadata, Markdown instructions, YAML permissions, handoffs and evaluation contracts.
3. `test` reads results produced by **your agent runner** and evaluates outputs, tools, handoffs and escalation.
4. `export` packages the validated files into a portable ZIP without symlinks or unsafe paths.

A passing contract report does not automatically change `status: draft` to `accepted`. Human acceptance is explicit.

## Quick start

Requires Python 3.10+.

```bash
git clone https://github.com/ARAZERX/feeho-employee.git
cd feeho-employee
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

Validate and evaluate the included fictional example:

```bash
feeho validate examples/inquiry-triage
feeho test examples/inquiry-triage \
  --results examples/sample-results.json \
  --report /tmp/feeho-report.json
feeho export examples/inquiry-triage --output /tmp/inquiry-triage.zip
```

Create your own generic draft:

```bash
feeho draft \
  --role "Inquiry triage" \
  --objective "Classify inquiries from approved material and escalate missing enterprise rules." \
  --output /tmp/my-employee
feeho validate /tmp/my-employee
```

The included sample results demonstrate the runner. They are **not** a model benchmark or evidence of production readiness.

## Employee package

```text
inquiry-triage/
├── employee.yaml       # identity, objective and draft/accepted status
├── role.md             # accountability and enterprise rules
├── instructions.md     # working rules
├── permissions.yaml    # allow / approval_required / deny
├── model-policy.yaml   # model-agnostic policy, no credentials
├── handoffs.yaml       # owner and trigger for exceptions
├── evals/cases.yaml    # input and explicit output/tool contracts
└── acceptance.yaml     # pass rate, required cases and human review
```

### External result format

The CLI does not execute an LLM. Pass results from the agent runtime you choose:

```json
{
  "cases": {
    "missing-rule": {
      "output": "企业规则缺失，需要人工确认后继续。",
      "tool_calls": [],
      "handoff_to": "human-owner",
      "escalated": true
    }
  }
}
```

Supported v0.1 assertions: `contains`, `not_contains`, `required_tools`, `forbidden_tools`, `handoff_to`, and `must_escalate`.

## What v0.1 does not do

- No hosted model, autonomous agent runtime or prompt-generation API.
- No multi-employee scheduling, reporting hierarchy or organization-level ledger.
- No built-in enterprise approval/audit system or long-running Feishu/DingTalk/WeCom integrations.
- No claim that passing contract tests proves broad model quality.
- No platform-specific exporters; ZIP is the portable v0.1 export.

Those organization and enterprise capabilities belong to a separate commercial product. See [COMMERCIAL.md](COMMERCIAL.md).

## Development

```bash
python -m unittest discover -s tests -v
```

The test suite covers valid packages, real contract failures, missing results, permission conflicts, unsafe YAML and unsafe exports.

## Contributing and security

See [CONTRIBUTING.md](CONTRIBUTING.md) and [SECURITY.md](SECURITY.md). Contributions use Apache-2.0 with DCO sign-offs. Do not attach credentials, customer data or private enterprise material.

## License

Copyright 2026 Xiamen FEEHO Intelligent Technology Co., Ltd.

The open-source core is licensed under [Apache License 2.0](LICENSE). Commercial use is permitted. Separate enterprise agreements do not restrict the Apache-2.0 rights granted to this core.
