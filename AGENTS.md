# AGENTS.md

# Laya Decision Labs — Agent Instructions

## 1. Purpose

This file defines how AI agents, coding assistants, and automated development tools must work within the `laya-decision-labs` repository.

The repository is an educational project evolving toward an enterprise security decision and GRC control plane.

Agents must preserve the architecture, security boundaries, and design principles defined in `SPECS.md`.

---

# 2. Source of Truth

Before modifying the project, agents should read:

```text
README.md
AGENTS.md
SPECS.md
```

For a specific component, agents should also inspect the relevant source code and tests.

Priority:

```text
SPECS.md
    ↓
AGENTS.md
    ↓
Existing implementation
    ↓
Lab requirements
```

If an implementation conflicts with the specification, do not silently change the architecture.

Explain the conflict and propose the smallest appropriate change.

---

# 3. General Development Rules

Agents must:

* make small, understandable changes
* preserve working functionality
* avoid unnecessary refactoring
* add tests for new behavior
* keep modules focused
* document security-sensitive behavior
* maintain backward compatibility where practical
* prefer explicit code over clever abstractions

Agents should not introduce large frameworks merely to solve small problems.

---

# 4. Phase Awareness

The repository is organized into phases.

Current architecture:

```text
Phase 1
Laya Decision Labs

Phase 2
Security Decision Engine

Phase 3
GRC Control Plane

Phase 4
Cloud Security Plane

Phase 5
Agentic Security Control Plane
```

Agents must not prematurely implement Phase 3–5 functionality when working on Phase 2 unless explicitly requested.

---

# 5. Decision Architecture

The authoritative flow is:

```text
REQUEST
   ↓
CLASSIFICATION
   ↓
RISK
   ↓
POLICY
   ↓
APPROVAL
   ↓
EXECUTION
   ↓
EVIDENCE
   ↓
AUDIT
```

Agents must preserve this separation.

---

# 6. Model Boundary

Laya, LLMs, and other AI models are advisory components.

They may:

* classify
* summarize
* reason
* recommend
* extract information

They must not independently authorize high-impact actions.

Do not implement:

```text
LLM → execute tool
```

Prefer:

```text
LLM
 ↓
Recommendation
 ↓
Policy Engine
 ↓
Approval
 ↓
Tool
```

---

# 7. Policy Authority

The policy engine is authoritative.

Agents must not allow model-generated text to override:

* policy rules
* approval requirements
* security boundaries
* production restrictions
* explicit deny rules

If a model says:

```text
"ALLOW"
```

that is not sufficient evidence that an operation is authorized.

---

# 8. High-Risk Operations

Treat the following as potentially high-risk:

```text
terraform destroy
delete
terminate
remove
disable MFA
disable encryption
disable logging
change IAM
grant administrator
modify production security controls
expose sensitive data
```

High-risk operations must pass through policy evaluation.

---

# 9. Production Protection

Agents must assume production requires stronger controls than development.

Agents must not:

* modify production infrastructure automatically
* delete production resources
* disable production security controls
* grant privileged production permissions

unless the project explicitly introduces an approved workflow for that behavior.

---

# 10. Credentials and Secrets

Agents must never:

* request users to paste credentials into source files
* commit credentials
* print access tokens
* print passwords
* print private keys
* expose cloud credentials in logs
* create fake credentials that look real

Use environment variables, secret managers, or the appropriate cloud authentication mechanism.

Never hard-code:

```text
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
AWS_SESSION_TOKEN
AZURE_CLIENT_SECRET
GCP_SERVICE_ACCOUNT_KEYS
API keys
tokens
passwords
```

---

# 11. Logging

Logs must not contain secrets.

Before logging user or tool input, consider whether it contains:

* credentials
* tokens
* personal information
* customer data
* secrets
* confidential configuration

Sensitive values should be redacted.

---

# 12. Decision Results

New decision-producing components should use a consistent result contract.

Conceptually:

```python
{
    "decision_id": "...",
    "source": "...",
    "classification": "...",
    "confidence": 0.0,
    "risk": {
        "score": 0.0,
        "level": "...",
        "factors": []
    },
    "policy": {
        "action": "...",
        "reason": "..."
    },
    "approval": {
        "required": False,
        "status": "NOT_REQUIRED"
    },
    "evidence": [],
    "metadata": {}
}
```

Do not introduce incompatible result structures without a clear reason.

---

# 13. Classification

Classification answers:

> "What type of operation is this?"

Examples:

```text
READ_ONLY
MODIFY
SECURITY_SENSITIVE
DESTRUCTIVE
DATA_ACCESS
PRIVILEGED
UNKNOWN
```

Classification does not answer:

> "Should this operation be executed?"

That is the responsibility of policy.

---

# 14. Risk

Risk answers:

> "How much potential impact does this request represent?"

Risk must consider context.

Examples:

```text
environment
operation type
privilege
data sensitivity
destructive potential
security impact
reversibility
```

Risk scoring must remain separate from classification.

---

# 15. Policy

Policy answers:

> "What should the system require before this operation can proceed?"

Possible results:

```text
ALLOW
REQUIRES_REVIEW
REQUIRES_SECURITY_REVIEW
REQUIRES_HUMAN_APPROVAL
BLOCK
```

Policy must be deterministic and testable.

---

# 16. Evidence

Agents should distinguish between:

```text
Observed evidence
```

and:

```text
Model-generated reasoning
```

Example:

```text
Observed:
terraform destroy matched deterministic rule.

Observed:
environment = production.

Policy:
production destructive operations require approval.
```

Do not represent model speculation as verified evidence.

---

# 17. Audit

Security-relevant decisions should create structured audit information.

At minimum:

```text
decision_id
timestamp
request
classification
risk
policy
approval
evidence
```

Audit information should support future integration with enterprise logging systems.

---

# 18. Tests

Every new security-sensitive component should have tests.

At minimum test:

```text
expected behavior
unexpected behavior
unknown input
boundary conditions
high-risk conditions
policy enforcement
```

When modifying existing functionality:

```text
1. Run existing tests.
2. Make the change.
3. Add/update tests.
4. Run the complete test suite.
```

Never intentionally remove tests simply to make a change pass.

---

# 19. Lab Development

Labs should be educational and progressively more advanced.

Each lab should:

1. explain one architectural concept
2. use reusable project code
3. demonstrate the concept
4. print or expose meaningful results
5. have tests where appropriate

Do not duplicate large amounts of logic inside individual labs.

Prefer:

```text
Lab
 ↓
Reusable module
```

instead of:

```text
Lab
 ↓
Copied implementation
```

---

# 20. Phase 1 Preservation

Do not unnecessarily modify:

```text
labs/01_noul
labs/02_choice
labs/03_score
labs/04_structured_decisions
labs/05_llm_vs_laya
labs/06_dynamic_routing
labs/07_prompt_guardrail
labs/08_tool_guardrail
labs/09_middleware
labs/10_enterprise_agent
```

These labs establish the project's historical progression.

If a Phase 2 refactor requires a change, preserve the original behavior unless explicitly instructed otherwise.

---

# 21. Dependencies

Before adding a dependency, ask:

```text
Can this be implemented using the standard library?
```

If not:

```text
Is the dependency necessary?
Is it maintained?
Does it introduce unnecessary complexity?
Does it affect installation?
Does it create security concerns?
```

Cloud-specific dependencies should remain isolated from the core engine.

---

# 22. Configuration

Security policies should progressively move from hard-coded Python logic into configuration files.

Preferred formats:

```text
YAML
JSON
TOML
```

Configuration should be:

* version controlled
* validated
* testable
* documented

Do not allow arbitrary configuration to bypass security controls.

---

# 23. Cloud Integrations

Future cloud integrations may include:

```text
AWS
Azure
GCP
```

Cloud discovery must be read-only unless an explicitly approved operation is being performed.

Discovery should never expose credentials.

Preferred architecture:

```text
Cloud Adapter
      ↓
Normalized Resource Model
      ↓
Policy Engine
      ↓
Decision
```

Do not place AWS-specific logic throughout the core decision engine.

---

# 24. Terraform Integration

Terraform operations should be classified before execution.

Examples:

```text
terraform plan
    ↓
READ / ANALYSIS

terraform apply
    ↓
MODIFY

terraform destroy
    ↓
DESTRUCTIVE
```

Production Terraform operations should require stronger policy controls.

---

# 25. Kubernetes Integration

Future Kubernetes operations should distinguish:

```text
read
create
update
delete
privileged
security-sensitive
```

Examples of potentially sensitive operations include:

```text
cluster-admin
privileged containers
security context changes
network policy changes
secret access
RBAC changes
```

---

# 26. MCP and Agent Tools

Future MCP tools must be treated as untrusted execution boundaries until evaluated.

Every tool should have metadata describing:

```text
tool name
description
risk category
required privileges
read/write behavior
environment scope
approval requirement
```

A tool must pass through the policy engine before high-impact execution.

---

# 27. Human Approval

Human approval must be explicit.

The system should not interpret:

```text
"I think this is okay"
```

from an AI model as human approval.

Approval should contain:

```text
approver
decision_id
timestamp
status
reason
```

---

# 28. Error Handling

Security-sensitive failures should fail safely.

For example:

```text
Policy engine unavailable
        ↓
Do not automatically ALLOW
```

Prefer:

```text
BLOCK
```

or:

```text
REQUIRES_REVIEW
```

depending on the operation.

---

# 29. Unknown States

Unknown should remain a valid state.

Do not force uncertain input into:

```text
ALLOW
```

just because the classifier needs an answer.

Use:

```text
UNKNOWN
```

and allow policy to determine the appropriate action.

---

# 30. Agent Change Workflow

When making a change:

```text
1. Read README.md
2. Read AGENTS.md
3. Read SPECS.md
4. Identify affected components
5. Inspect existing implementation
6. Make the smallest change
7. Add/update tests
8. Run tests
9. Run the relevant lab
10. Review security implications
11. Summarize changes
```

---

# 31. Do Not

Agents must not:

* silently rewrite architecture
* remove security checks
* bypass policy
* expose secrets
* automatically approve high-risk actions
* execute destructive production operations
* treat LLM output as authoritative
* hide failed tests
* delete tests without justification
* add unnecessary dependencies
* duplicate core decision logic across labs

---

# 32. Preferred Implementation Style

Prefer code that is:

```text
explicit
typed
small
testable
documented
deterministic
composable
```

Avoid excessive abstraction.

A beginner should be able to understand the core security flow.

---

# 33. Enterprise Evolution

The repository will eventually support:

```text
Decision Engine
       ↓
Policy Engine
       ↓
GRC Controls
       ↓
Evidence
       ↓
Findings
       ↓
Cloud Security
       ↓
Agentic Automation
```

Agents should therefore favor stable interfaces and reusable models.

---

# 34. Final Agent Rule

The most important rule is:

> **AI may recommend. Policy decides. Humans approve high-impact actions. Tools execute only after authorization. Evidence records what happened.**

---

# 35. Lab Execution and Scope

Run tests with `python -m pytest` and run a lab from the repository root, for example `python labs/12_policy_configuration/main.py`. Labs 21-30 must remain read-only against real cloud providers; use fixtures by default and document any live provider prerequisites. Lab 21 may create a disposable instance only in the explicitly selected local Floci emulator mode, never in an AWS account. Lab 31 is an interactive, non-executing capstone. Lab 32 evaluates Laya against labeled fixtures; inference may download model checkpoints, must not use cloud credentials, and must not mutate infrastructure. Do not add provider SDKs to core dependencies. Treat `SPECS.md` as the architecture source of truth and update it when an approved architecture change is made.

This principle must remain intact as the project grows.
