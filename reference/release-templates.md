# Release/DevOps templates

Read by the Release/DevOps agent in process establishment, release preparation, and pipeline review modes. Sprint close-out doesn't need these. Fill every placeholder with the project's real commands and values; if the tooling isn't established yet, leave clearly marked placeholders.

## Release process document
```
# Release Process: [project name]
**Version:** [version]
**Last updated:** [date]

## Environment structure
| Environment | Purpose | URL / Access | Promotion trigger |
|---|---|---|---|
| Local | Development | localhost | Manual |
| Staging | Pre-release verification | [URL] | Merge to main |
| Production | Live | [URL] | Manual release |

## Branching and release trigger
[Description of branching strategy and what constitutes a releasable state]

## Pre-release requirements
What must be true before any release begins:
- [ ] All QA sign-offs complete for included changes
- [ ] Security review complete for included changes
- [ ] All acceptance criteria verified
- [ ] Staging deployment verified
- [ ] Rollback plan confirmed
- [ ] [Project-specific requirements]

## Deployment sequence
[Ordered steps — see runbook format for detail]

## Post-deploy verification
[What to check after deployment to confirm success]

## Rollback plan
[See rollback plan format]

## Access and credentials required
[What is needed, where to obtain it — do not store credentials here]

## Communication
[Who is notified, when, and how]

## Process change log
| Date | Change | Reason |
|---|---|---|
```


## Pre-release checklist
```
# Pre-Release Checklist: [release name / version]
**Release date:** [date]
**Executor:** [who is running this release]
**Release scope:** [brief description of what is being released]


## Human inputs required before execution
Collect these before starting. Do not begin execution without them.

- [ ] [Credential or value needed]: [where to obtain it]
- [ ] [Decision required]: [context and options]
- [ ] [Approval needed from]: [who and how to confirm]


## Codebase state
- [ ] All changes for this release are merged to [branch]
- [ ] No uncommitted changes on [branch]
- [ ] Version / tag created: [tag name]
- [ ] Changelog updated and accurate

## Test and review sign-offs
- [ ] QA sign-off received: [reference]
- [ ] Security review complete: [reference or N/A]
- [ ] Accessibility review complete: [reference or N/A]
- [ ] UX review complete: [reference or N/A]

## Environment readiness
- [ ] Staging deployment verified within [timeframe]
- [ ] Production environment healthy — [how to verify]
- [ ] No active incidents in production
- [ ] Database migrations tested on staging: [N/A if none]
- [ ] Feature flags configured correctly: [N/A if none]
- [ ] Environment variables verified for production: [list]

## Rollback readiness
- [ ] Rollback plan reviewed and understood
- [ ] Rollback tested on staging: [N/A if not applicable]
- [ ] Previous known-good version identified: [version / commit]


**Checklist complete:** [ ] Yes — proceed to runbook
**Blockers identified:** [list any items that could not be checked and why]
```


## Deployment runbook
```
# Deployment Runbook: [release name / version]
**Release date:** [date]
**Executor:** [who is running this release]
**Estimated duration:** [time]
**Rollback plan:** [reference to rollback plan]


## Before you begin
- Pre-release checklist complete: [ ] confirmed
- Human inputs collected: [ ] confirmed
- Rollback plan reviewed: [ ] confirmed


## Deployment steps

### Step [n]: [step name]
**Action:**
[Exact command, UI action, or procedure. No ambiguity.]

**Expected outcome:**
[What success looks like — output, status code, UI state, log message]

**Verification:**
[How to confirm this step succeeded before proceeding]

**If this step fails:**
[Immediate action — stop and assess / execute rollback / contact X]


[Repeat for each step]


## Post-deploy verification

### Verify [n]: [what is being verified]
**Check:**
[Exact command or procedure]

**Expected result:**
[What success looks like]

**If verification fails:**
[Immediate action]


## Release complete
- [ ] All deployment steps completed
- [ ] All post-deploy verifications passed
- [ ] Release noted in changelog / status docs
- [ ] PM notified of successful deployment

**Deployment completed at:** [time]
**Deployed by:** [executor]
**Any deviations from runbook:** [describe or N/A]
```


## Rollback plan
```
# Rollback Plan: [release name / version]
**Trigger condition:** Use this plan if post-deploy verification fails or a critical issue is detected after deployment.
**Decision authority:** [who decides to execute rollback — default: executor, escalate to PM if uncertain]
**Estimated rollback duration:** [time]


## Rollback trigger criteria
Execute rollback immediately if any of the following are true:
- [ ] [Specific failure condition]
- [ ] [Specific failure condition]
- [ ] Post-deploy verification step [n] fails

Do not wait to assess if these conditions are met. Execute rollback.

Assess before deciding if:
- [ ] [Ambiguous condition — describe what to assess and who to involve]


## Rollback steps

### Step [n]: [step name]
**Action:**
[Exact command or procedure]

**Expected outcome:**
[What success looks like]

**Verification:**
[How to confirm this step succeeded]


## Post-rollback verification
[What to check to confirm the system is back to the prior known-good state]

## After rollback
- [ ] PM notified of rollback
- [ ] Incident documented: [what happened, when, what was rolled back]
- [ ] Root cause investigation initiated
- [ ] Re-release blocked until root cause is identified and resolved
```


## Pipeline review report
```
## CI/CD Pipeline Review: [pipeline name]
**Date:** [date]
**Mode:** [New design / Change review]
**Pipeline reviewed:** [file or service reference]

### Overall assessment
One paragraph. Is this pipeline correctly structured, reliable, and secure for its purpose?

### Stage analysis

| Stage | Purpose | Trigger | Pass condition | Assessment |
|---|---|---|---|---|
| [stage] | [purpose] | [trigger] | [condition] | Pass / Fail / Concern |

### Findings

#### [Finding title] — [Severity: Critical / Major / Minor / Note]
- **Issue:** What the problem is
- **Risk:** What goes wrong if not addressed
- **Recommendation:** What the correct approach is

### Security assessment
- Secrets exposure risk: [assessment]
- Unauthorized trigger risk: [assessment]
- Artifact integrity: [assessment]

### Recommended PM / Architect actions
- [Finding]: Resolve before first use / Address before next change / Track as improvement

### Clear areas
Pipeline aspects reviewed with no current concerns.
```
