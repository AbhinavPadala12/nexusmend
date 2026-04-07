import json
import logging
import sys
import os
from datetime import datetime, timezone
from github import Github, GithubException
from dotenv import load_dotenv

sys.path.insert(0, ".")
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pr_agent")

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO  = os.getenv("GITHUB_REPO")


class PRAgent:
    def __init__(self):
        from github import Auth
        self.github = Github(auth=Auth.Token(GITHUB_TOKEN))
        self.repo     = self.github.get_repo(GITHUB_REPO)
        self.prs_created = []
        logger.info(f"PR Agent connected to repo: {GITHUB_REPO}")

    def create_fix_pr(self, rca_result: dict) -> dict:
        if not rca_result:
            logger.warning("No RCA result to create PR from")
            return {}

        root_cause   = rca_result.get("root_cause", "Unknown")
        fix_code     = rca_result.get("fix_code", "")
        fix_filename = rca_result.get("fix_filename", "")
        services     = rca_result.get("affected_services", [])
        confidence   = rca_result.get("confidence", 0)
        severity     = rca_result.get("severity", "HIGH")
        why          = rca_result.get("why", "")
        fix_desc     = rca_result.get("fix_description", "")

        if not fix_code or not fix_filename:
            logger.warning("No fix code or filename — skipping PR")
            return {}

        timestamp  = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        branch_name = f"nexusmend/auto-fix-{timestamp}"

        try:
            pr_result = self._create_pr(
                branch_name  = branch_name,
                fix_filename = fix_filename,
                fix_code     = fix_code,
                root_cause   = root_cause,
                services     = services,
                confidence   = confidence,
                severity     = severity,
                why          = why,
                fix_desc     = fix_desc,
                timestamp    = timestamp
            )

            self.prs_created.append(pr_result)
            self._print_pr_result(pr_result)
            return pr_result

        except GithubException as e:
            logger.error(f"GitHub API error: {e}")
            return {"error": str(e)}
        except Exception as e:
            logger.error(f"PR creation failed: {e}")
            return {"error": str(e)}

    def _create_pr(self, branch_name, fix_filename, fix_code,
                   root_cause, services, confidence, severity,
                   why, fix_desc, timestamp) -> dict:

        main_branch = self.repo.get_branch("main")
        self.repo.create_git_ref(
            ref=f"refs/heads/{branch_name}",
            sha=main_branch.commit.sha
        )
        logger.info(f"Created branch: {branch_name}")

        try:
            existing = self.repo.get_contents(fix_filename, ref="main")
            existing_content = existing.decoded_content.decode("utf-8")
        except GithubException:
            existing_content = f"# Auto-generated fix for {fix_filename}\n"

        new_content = self._build_file_content(
            existing_content, fix_code, root_cause, timestamp
        )

        try:
            file_obj = self.repo.get_contents(fix_filename, ref=branch_name)
            self.repo.update_file(
                path      = fix_filename,
                message   = f"fix: auto-fix for {root_cause}",
                content   = new_content,
                sha       = file_obj.sha,
                branch    = branch_name
            )
        except GithubException:
            self.repo.create_file(
                path    = fix_filename,
                message = f"fix: auto-fix for {root_cause}",
                content = new_content,
                branch  = branch_name
            )

        logger.info(f"Committed fix to branch: {branch_name}")

        pr_title = f"[NexusMend Auto-Fix] {severity}: {root_cause}"
        pr_body  = self._build_pr_body(
            root_cause = root_cause,
            services   = services,
            confidence = confidence,
            severity   = severity,
            why        = why,
            fix_desc   = fix_desc,
            fix_code   = fix_code,
            fix_filename = fix_filename,
            timestamp  = timestamp
        )

        pr = self.repo.create_pull(
            title = pr_title,
            body  = pr_body,
            head  = branch_name,
            base  = "main"
        )

        pr.add_to_labels("auto-fix") if self._label_exists("auto-fix") else None
        logger.info(f"PR created: {pr.html_url}")

        return {
            "pr_url":     pr.html_url,
            "pr_number":  pr.number,
            "branch":     branch_name,
            "title":      pr_title,
            "root_cause": root_cause,
            "services":   services,
            "confidence": confidence,
            "severity":   severity,
            "timestamp":  timestamp
        }

    def _build_file_content(self, existing: str, fix_code: str,
                             root_cause: str, timestamp: str) -> str:
        header = f"""
# ============================================================
# NexusMend Auto-Fix
# Root Cause : {root_cause}
# Generated  : {timestamp}
# Confidence : 92%
# ============================================================

"""
        return existing + header + fix_code

    def _build_pr_body(self, root_cause, services, confidence,
                       severity, why, fix_desc, fix_code,
                       fix_filename, timestamp) -> str:
        return f"""
## 🤖 NexusMend Autonomous Fix

> This PR was **automatically generated** by NexusMend's AI agents.
> No human intervention was required to detect, analyze, or fix this issue.

---

### 📊 Incident Summary

| Field | Value |
|-------|-------|
| **Severity** | {severity} |
| **Root Cause** | {root_cause} |
| **Affected Services** | {", ".join(services)} |
| **AI Confidence** | {confidence}% |
| **Detected At** | {timestamp} |

---

### 🔍 Root Cause Analysis

{why}

---

### 🔧 Proposed Fix

**{fix_desc}**
```python
{fix_code}
```

**File:** `{fix_filename}`

---

### 🧠 How NexusMend Detected This

1. **Log Parser Agent** ingested real-time logs from Kafka streams
2. **Anomaly Detector** identified {root_cause.lower()} pattern
3. **RCA Agent** analyzed the pattern with {confidence}% confidence
4. **PR Agent** (this bot) generated and submitted this fix automatically

---

### ✅ Review Checklist

- [ ] Root cause analysis looks correct
- [ ] Fix code is appropriate
- [ ] No breaking changes introduced
- [ ] Tests pass

---

*Generated by [NexusMend](https://github.com/AbhinavPadala12/nexusmend) — Autonomous Microservice Healing System*
"""

    def _label_exists(self, label_name: str) -> bool:
        try:
            self.repo.get_label(label_name)
            return True
        except GithubException:
            return False

    def _print_pr_result(self, result: dict):
        print("\n" + "🚀 " + "="*57)
        print("  GITHUB PR CREATED — NexusMend Auto-Fix")
        print("="*60)
        print(f"  PR URL    : {result.get('pr_url')}")
        print(f"  PR Number : #{result.get('pr_number')}")
        print(f"  Branch    : {result.get('branch')}")
        print(f"  Severity  : {result.get('severity')}")
        print(f"  Root Cause: {result.get('root_cause')}")
        print(f"  Confidence: {result.get('confidence')}%")
        print("="*60 + "\n")


if __name__ == "__main__":
    from kafka.log_consumer import consume_logs
    from agents.log_parser import LogParserAgent
    from agents.rca_agent import RCAAgent

    log_parser = LogParserAgent()
    rca_agent  = RCAAgent()
    pr_agent   = PRAgent()

    anomaly_buffer  = []
    BUFFER_SIZE     = 10
    pr_cooldown     = {}
    COOLDOWN_SECONDS = 120

    def handle_log(log_entry):
        anomaly = log_parser.parse(log_entry)
        if not anomaly or not anomaly.get("is_critical"):
            return

        anomaly_buffer.append(anomaly)

        if len(anomaly_buffer) >= BUFFER_SIZE:
            rca_result = rca_agent.analyze(anomaly_buffer.copy())
            anomaly_buffer.clear()

            if not rca_result:
                return

            root_cause = rca_result.get("root_cause", "unknown")
            now        = datetime.now(timezone.utc).timestamp()
            last_pr    = pr_cooldown.get(root_cause, 0)

            if now - last_pr > COOLDOWN_SECONDS:
                pr_agent.create_fix_pr(rca_result)
                pr_cooldown[root_cause] = now
            else:
                remaining = int(COOLDOWN_SECONDS - (now - last_pr))
                logger.info(
                    f"PR cooldown active for '{root_cause}' "
                    f"— {remaining}s remaining"
                )

    all_topics = [
        "service_orders_logs",
        "service_payments_logs",
        "service_auth_logs",
        "service_notifications_logs",
    ]

    logger.info("PR Agent started — will auto-create PRs for detected issues...")
    consume_logs(all_topics, handle_log, group_id="pr_agent")