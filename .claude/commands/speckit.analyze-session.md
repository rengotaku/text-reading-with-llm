---
description: Analyze session and generate agent improvement insights
---

## User Input

```text
$ARGUMENTS
```

## Overview

Two-stage session analysis workflow with **automatic file output**:

```
┌─────────────────────────────────────────────────────────────┐
│ Stage 1: analyze-session.sh --auto --type TYPE              │
│   └→ {timestamp}-{type}.json (raw data + metrics)           │
│   └→ {timestamp}-{type}.md (statistics summary)             │
├─────────────────────────────────────────────────────────────┤
│ Stage 2: Claude reads JSON → generates insights             │
│   └→ {timestamp}-{type}-insights.md (improvement proposals) │
└─────────────────────────────────────────────────────────────┘
```

## Instructions

### 1. Detect Session Type

Infer from conversation context:
- After `speckit.implement` → `implement`
- After `speckit.plan` → `plan`
- After `speckit.tasks` → `tasks`
- Default → `session`

### 2. Run Stage 1: Data Collection

Run the script with `--auto` flag (auto-detects FEATURE_DIR from git branch):

```bash
.specify/scripts/bash/analyze-session.sh --auto --type implement
```

If local script not found, use global:
```bash
~/.claude/scripts/analyze-session.sh --auto --type implement
```

This generates in `specs/{branch}/analyzed-action/`:
- `{timestamp}-{type}.json` - Raw data for insights
- `{timestamp}-{type}.md` - Human-readable summary

### 3. Display Terminal Summary

Run without `--auto` to show immediate feedback:

```bash
.specify/scripts/bash/analyze-session.sh --type implement
```

### 4. Run Stage 2: Generate Insights (Subagent)

**Launch `insights-generator` subagent** with Sonnet model:

```
Task tool:
  subagent_type: general-purpose
  model: sonnet
  prompt: |
    You are an insights-generator agent.
    Read: .claude/agents/insights-generator.md for instructions.

    Input: {json_file_path}
    Output: {output_dir}/{timestamp}-{type}-insights.md

    Generate improvement insights based on the JSON data.
```

The subagent analyzes:

| Category | What to Check |
|----------|---------------|
| **Efficiency** | Duplicate reads, parallelization opportunities |
| **Delegation** | Model selection, subagent utilization |
| **Error Prevention** | Preflight-preventable errors, retry patterns |
| **Workflow** | TDD compliance, commit granularity |
| **Cost** | Token usage, cache hit rate |

### 5. Report Completion

```
✅ Session analysis complete

📁 Output files:
   - specs/{branch}/analyzed-action/20260225-implement.json
   - specs/{branch}/analyzed-action/20260225-implement.md
   - specs/{branch}/analyzed-action/20260225-implement-insights.md

📊 Key findings:
   - {finding 1}
   - {finding 2}
```

## Insights Template

Use this structure for `-insights.md`:

```markdown
# Session Insights: {type}

**Generated**: {timestamp}
**Session**: {session_id}

## Executive Summary
{2-3 sentence summary}

## 🔴 HIGH Priority
{Critical issues}

## 🟡 MEDIUM Priority
{Important optimizations}

## 🟢 LOW Priority
{Nice-to-have}

## Actionable Next Steps
1. ...
2. ...
```
