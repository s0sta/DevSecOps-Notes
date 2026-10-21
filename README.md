<a href="https://s0sta.com"><img src=".github/assets/banner.png" alt="s0sta DevSecOps notes: commands and checklists you can copy and run" width="100%"></a>

# DevSecOps notes

Practical DevSecOps notes from my LinkedIn posts: Docker, Kubernetes, Terraform, CI/CD, cloud, observability, application and supply-chain security, incident response and vulnerability management. Every note has a **quick reference** you can copy, the **full explanation**, and the **script** when there is one.

| Notes | Topics | Scripts |
|:--|:--|:--|
| **623** | **28** | **181** (156 Python + 25 Bash), no extra packages |

Linux, Windows, networks, storage and databases are in **[IT-Notes](https://github.com/s0sta/IT-Notes)**. The 194 notes that fit both are in both repos.

## How to use it

1. Open a topic below and pick a note.
2. Copy a command from a code box. GitHub shows a copy button on every box.
3. Need a script? It is at the end of the note and in [`scripts/`](scripts).

Looking for one command? Use the search box at the top of GitHub, for example `kubectl logs` or `terraform plan`.

## Notes by topic

<details>
<summary><b>Python scripts</b> · 158 notes</summary>

- [A disk-space alert in 15 lines of Python](notes/p172-a-disk-space-alert-in-15-lines-of-python.md) <sub>P172 · script</sub>
- [Find risky file permissions with Python](notes/p177-find-risky-file-permissions-with-python.md) <sub>P177 · script</sub>
- [A TLS certificate expiry checker in Python](notes/p182-a-tls-certificate-expiry-checker-in-python.md) <sub>P182 · script</sub>
- [A website uptime and latency checker in Python](notes/p187-a-website-uptime-and-latency-checker-in-python.md) <sub>P187 · script</sub>
- [A self-cleaning backup script in Python](notes/p192-a-self-cleaning-backup-script-in-python.md) <sub>P192 · script</sub>
- [A secret scanner in Python for your CI](notes/p197-a-secret-scanner-in-python-for-your-ci.md) <sub>P197 · script</sub>
- [A Kubernetes pod health summary in Python](notes/p202-a-kubernetes-pod-health-summary-in-python.md) <sub>P202 · script</sub>
- [A systemd service watchdog in Python](notes/p207-a-systemd-service-watchdog-in-python.md) <sub>P207 · script</sub>
- [Find SSH brute-force attempts with Python](notes/p212-find-ssh-brute-force-attempts-with-python.md) <sub>P212 · script</sub>
- [Check a site's security headers with Python](notes/p217-check-a-sites-security-headers-with-python.md) <sub>P217 · script</sub>
- [A GitOps drift detector in Python](notes/p224-a-gitops-drift-detector-in-python.md) <sub>P224 · script</sub>
- [An Argo CD sync report in Python](notes/p229-an-argo-cd-sync-report-in-python.md) <sub>P229 · script</sub>
- [nginx latency percentiles in Python](notes/p234-nginx-latency-percentiles-in-python.md) <sub>P234 · script</sub>
- [A Prometheus health check in Python](notes/p239-a-prometheus-health-check-in-python.md) <sub>P239 · script</sub>
- [A Terraform plan gate in Python](notes/p244-a-terraform-plan-gate-in-python.md) <sub>P244 · script</sub>
- [A repository standards checker in Python](notes/p249-a-repository-standards-checker-in-python.md) <sub>P249 · script</sub>
- [An IAM wildcard scanner in Python](notes/p254-an-iam-wildcard-scanner-in-python.md) <sub>P254 · script</sub>
- [A Trivy gate in Python](notes/p259-a-trivy-gate-in-python.md) <sub>P259 · script</sub>
- [An LLM gateway log audit in Python](notes/p264-an-llm-gateway-log-audit-in-python.md) <sub>P264 · script</sub>
- [A GPU workload audit in Python](notes/p269-a-gpu-workload-audit-in-python.md) <sub>P269 · script</sub>
- [A VPC subnet planner in Python](notes/p275-a-vpc-subnet-planner-in-python.md) <sub>P275 · script</sub>
- [An HTTP redirect chain checker in Python](notes/p280-an-http-redirect-chain-checker-in-python.md) <sub>P280 · script</sub>
- [An S3 public access checker in Python](notes/p285-an-s3-public-access-checker-in-python.md) <sub>P285 · script</sub>
- [A Terraform tag auditor in Python](notes/p290-a-terraform-tag-auditor-in-python.md) <sub>P290 · script</sub>
- [A Dockerfile linter in Python](notes/p295-a-dockerfile-linter-in-python.md) <sub>P295 · script</sub>
- [A git repository health report in Python](notes/p300-a-git-repository-health-report-in-python.md) <sub>P300 · script</sub>
- [An SSH configuration auditor in Python](notes/p305-an-ssh-configuration-auditor-in-python.md) <sub>P305 · script</sub>
- [A git history secret scanner in Python](notes/p310-a-git-history-secret-scanner-in-python.md) <sub>P310 · script</sub>
- [A token budget estimator in Python](notes/p315-a-token-budget-estimator-in-python.md) <sub>P315 · script</sub>
- [A GPU utilisation report in Python](notes/p320-a-gpu-utilisation-report-in-python.md) <sub>P320 · script</sub>
- [A consumer lag report in Python](notes/p355-a-consumer-lag-report-in-python.md) <sub>P355 · script</sub>
- [A data freshness checker in Python](notes/p360-a-data-freshness-checker-in-python.md) <sub>P360 · script</sub>
- [A PII column scanner in Python](notes/p365-a-pii-column-scanner-in-python.md) <sub>P365 · script</sub>
- [A data quality checker in Python](notes/p370-a-data-quality-checker-in-python.md) <sub>P370 · script</sub>
- [A risk register scorer in Python](notes/p377-a-risk-register-scorer-in-python.md) <sub>P377 · script</sub>
- [A lockfile audit in Python](notes/p387-a-lockfile-audit-in-python.md) <sub>P387 · script</sub>
- [A GitHub Actions audit in Python](notes/p396-a-github-actions-audit-in-python.md) <sub>P396 · script</sub>
- [A Terraform security audit in Python](notes/p397-a-terraform-security-audit-in-python.md) <sub>P397 · script</sub>
- [A JWT checker in Python](notes/p406-a-jwt-checker-in-python.md) <sub>P406 · script</sub>
- [A CloudTrail detection script in Python](notes/p415-a-cloudtrail-detection-script-in-python.md) <sub>P415 · script</sub>
- [A vulnerability SLA tracker in Python](notes/p416-a-vulnerability-sla-tracker-in-python.md) <sub>P416 · script</sub>
- [A changelog generator in Python](notes/p425-a-changelog-generator-in-python.md) <sub>P425 · script</sub>
- [A semantic version bumper in Python](notes/p426-a-semantic-version-bumper-in-python.md) <sub>P426 · script</sub>
- [A build time report in Python](notes/p435-a-build-time-report-in-python.md) <sub>P435 · script</sub>
- [A flaky test detector in Python](notes/p436-a-flaky-test-detector-in-python.md) <sub>P436 · script</sub>
- [An environment diff in Python](notes/p445-an-environment-diff-in-python.md) <sub>P445 · script</sub>
- [A config linter in Python](notes/p446-a-config-linter-in-python.md) <sub>P446 · script</sub>
- [An on-call load report in Python](notes/p455-an-on-call-load-report-in-python.md) <sub>P455 · script</sub>
- [An incident metrics report in Python](notes/p456-an-incident-metrics-report-in-python.md) <sub>P456 · script</sub>
- [A review latency report in Python](notes/p465-a-review-latency-report-in-python.md) <sub>P465 · script</sub>
- [A CI cost report in Python](notes/p466-a-ci-cost-report-in-python.md) <sub>P466 · script</sub>
- [HTTP timing phases in Python](notes/p474-http-timing-phases-in-python.md) <sub>P474 · script</sub>
- [A TLS inspector in Python](notes/p475-a-tls-inspector-in-python.md) <sub>P475 · script</sub>
- [A DNS check in Python](notes/p485-a-dns-check-in-python.md) <sub>P485 · script</sub>
- [A TCP port check in Python](notes/p486-a-tcp-port-check-in-python.md) <sub>P486 · script</sub>
- [A route table check in Python](notes/p495-a-route-table-check-in-python.md) <sub>P495 · script</sub>
- [A VPC flow log report in Python](notes/p496-a-vpc-flow-log-report-in-python.md) <sub>P496 · script</sub>
- [A connection state report in Python](notes/p505-a-connection-state-report-in-python.md) <sub>P505 · script</sub>
- [A latency matrix in Python](notes/p506-a-latency-matrix-in-python.md) <sub>P506 · script</sub>
- [An MTU calculator in Python](notes/p515-an-mtu-calculator-in-python.md) <sub>P515 · script</sub>
- [A bandwidth-delay product in Python](notes/p516-a-bandwidth-delay-product-in-python.md) <sub>P516 · script</sub>
- [The Python stdlib for DevSecOps](notes/p523-the-python-stdlib-for-devsecops.md) <sub>P523</sub>
- [An sshd_config audit in Python](notes/p525-an-sshd-config-audit-in-python.md) <sub>P525 · script</sub>
- [A sudoers audit in Python](notes/p526-a-sudoers-audit-in-python.md) <sub>P526 · script</sub>
- [9 commands to debug a Python automation script](notes/p528-9-commands-to-debug-a-python-automation-script.md) <sub>P528</sub>
- [A systemd hardening score in Python](notes/p529-a-systemd-hardening-score-in-python.md) <sub>P529 · script</sub>
- [A cron audit in Python](notes/p530-a-cron-audit-in-python.md) <sub>P530 · script</sub>
- [An SBOM diff in Python](notes/p535-an-sbom-diff-in-python.md) <sub>P535 · script</sub>
- [A licence audit in Python](notes/p536-a-licence-audit-in-python.md) <sub>P536 · script</sub>
- [A Terraform module pin check in Python](notes/p539-a-terraform-module-pin-check-in-python.md) <sub>P539 · script</sub>
- [A Terraform state secret scanner in Python](notes/p540-a-terraform-state-secret-scanner-in-python.md) <sub>P540 · script</sub>
- [An IAM policy diff in Python](notes/p545-an-iam-policy-diff-in-python.md) <sub>P545 · script</sub>
- [An S3 bucket config audit in Python](notes/p546-an-s3-bucket-config-audit-in-python.md) <sub>P546 · script</sub>
- [A pod security context audit in Python](notes/p549-a-pod-security-context-audit-in-python.md) <sub>P549 · script</sub>
- [A NetworkPolicy coverage report in Python](notes/p550-a-networkpolicy-coverage-report-in-python.md) <sub>P550 · script</sub>
- [A CSP audit in Python](notes/p555-a-csp-audit-in-python.md) <sub>P555 · script</sub>
- [A CORS audit in Python](notes/p556-a-cors-audit-in-python.md) <sub>P556 · script</sub>
- [A cookie flag audit in Python](notes/p558-a-cookie-flag-audit-in-python.md) <sub>P558 · script</sub>
- [An OpenAPI auth check in Python](notes/p559-an-openapi-auth-check-in-python.md) <sub>P559 · script</sub>
- [A log redactor in Python](notes/p565-a-log-redactor-in-python.md) <sub>P565 · script</sub>
- [An API key age report in Python](notes/p566-an-api-key-age-report-in-python.md) <sub>P566 · script</sub>
- [A Docker CIS check in Python](notes/p569-a-docker-cis-check-in-python.md) <sub>P569 · script</sub>
- [An image pin report in Python](notes/p570-an-image-pin-report-in-python.md) <sub>P570 · script</sub>
- [An inode exhaustion forecaster](notes/p572-an-inode-exhaustion-forecaster.md) <sub>P572 · script</sub>
- [An OOM kill report](notes/p573-an-oom-kill-report.md) <sub>P573 · script</sub>
- [A zombie process scan](notes/p574-a-zombie-process-scan.md) <sub>P574 · script</sub>
- [A log flood detector](notes/p575-a-log-flood-detector.md) <sub>P575 · script</sub>
- [A file descriptor leak finder](notes/p576-a-file-descriptor-leak-finder.md) <sub>P576 · script</sub>
- [A certificate bundle check in Python](notes/p582-a-certificate-bundle-check-in-python.md) <sub>P582 · script</sub>
- [A secret rotation report in Python](notes/p583-a-secret-rotation-report-in-python.md) <sub>P583 · script</sub>
- [An offboarding access audit in Python](notes/p584-an-offboarding-access-audit-in-python.md) <sub>P584 · script</sub>
- [A password age audit in Python](notes/p585-a-password-age-audit-in-python.md) <sub>P585 · script</sub>
- [A sudo drift report in Python](notes/p586-a-sudo-drift-report-in-python.md) <sub>P586 · script</sub>
- [Why is this pod Pending?](notes/p592-why-is-this-pod-pending.md) <sub>P592 · script</sub>
- [An eviction report](notes/p593-an-eviction-report.md) <sub>P593 · script</sub>
- [An image pull failure report](notes/p594-an-image-pull-failure-report.md) <sub>P594 · script</sub>
- [A node pressure report](notes/p595-a-node-pressure-report.md) <sub>P595 · script</sub>
- [A failed job report](notes/p596-a-failed-job-report.md) <sub>P596 · script</sub>
- [Did the deploy actually land?](notes/p602-did-the-deploy-actually-land.md) <sub>P602 · script</sub>
- [A missing artifact check](notes/p603-a-missing-artifact-check.md) <sub>P603 · script</sub>
- [Is rollback ready?](notes/p604-is-rollback-ready.md) <sub>P604 · script</sub>
- [A CI log secret leak scan](notes/p605-a-ci-log-secret-leak-scan.md) <sub>P605 · script</sub>
- [A pipeline flake report](notes/p606-a-pipeline-flake-report.md) <sub>P606 · script</sub>
- [A restore drill in Python](notes/p612-a-restore-drill-in-python.md) <sub>P612 · script</sub>
- [A table growth report in Python](notes/p613-a-table-growth-report-in-python.md) <sub>P613 · script</sub>
- [An S3 cost hotspot report in Python](notes/p614-an-s3-cost-hotspot-report-in-python.md) <sub>P614 · script</sub>
- [A log retention audit in Python](notes/p615-a-log-retention-audit-in-python.md) <sub>P615 · script</sub>
- [An orphan resource report in Python](notes/p616-an-orphan-resource-report-in-python.md) <sub>P616 · script</sub>
- [An alert dedupe report](notes/p672-an-alert-dedupe-report.md) <sub>P672 · script</sub>
- [A merged incident timeline](notes/p673-a-merged-incident-timeline.md) <sub>P673 · script</sub>
- [A service blast radius report](notes/p674-a-service-blast-radius-report.md) <sub>P674 · script</sub>
- [A severity policy check](notes/p675-a-severity-policy-check.md) <sub>P675 · script</sub>
- [An on-call handoff brief](notes/p676-an-on-call-handoff-brief.md) <sub>P676 · script</sub>
- [A host quarantine plan that keeps the console](notes/p682-a-host-quarantine-plan-that-keeps-the-console.md) <sub>P682 · script</sub>
- [An ordered account lockout plan](notes/p683-an-ordered-account-lockout-plan.md) <sub>P683 · script</sub>
- [A token revocation list, oldest first](notes/p684-a-token-revocation-list-oldest-first.md) <sub>P684 · script</sub>
- [An edge block that checks the allow list](notes/p685-an-edge-block-that-checks-the-allow-list.md) <sub>P685 · script</sub>
- [A kill-switch audit ranked by blast radius](notes/p686-a-kill-switch-audit-ranked-by-blast-radius.md) <sub>P686 · script</sub>
- [A credential rotation planner](notes/p692-a-credential-rotation-planner.md) <sub>P692 · script</sub>
- [A config rollback planner](notes/p693-a-config-rollback-planner.md) <sub>P693 · script</sub>
- [A certificate replacement planner](notes/p694-a-certificate-replacement-planner.md) <sub>P694 · script</sub>
- [A restore point picker](notes/p695-a-restore-point-picker.md) <sub>P695 · script</sub>
- [A node drain simulator](notes/p696-a-node-drain-simulator.md) <sub>P696 · script</sub>
- [An evidence bundle](notes/p702-an-evidence-bundle.md) <sub>P702 · script</sub>
- [A status page draft](notes/p703-a-status-page-draft.md) <sub>P703 · script</sub>
- [A timeline export](notes/p704-a-timeline-export.md) <sub>P704 · script</sub>
- [An action item tracker](notes/p705-an-action-item-tracker.md) <sub>P705 · script</sub>
- [A notification log](notes/p706-a-notification-log.md) <sub>P706 · script</sub>
- [The detection that was never written](notes/p712-the-detection-that-was-never-written.md) <sub>P712 · script</sub>
- [Runbooks that rotted](notes/p713-runbooks-that-rotted.md) <sub>P713 · script</sub>
- [Alerts nobody acts on](notes/p714-alerts-nobody-acts-on.md) <sub>P714 · script</sub>
- [The incident that keeps coming back](notes/p715-the-incident-that-keeps-coming-back.md) <sub>P715 · script</sub>
- [The control you think is on](notes/p716-the-control-you-think-is-on.md) <sub>P716 · script</sub>
- [Subdomains you never registered](notes/p722-subdomains-you-never-registered.md) <sub>P722 · script</sub>
- [The DNS record that points at nothing](notes/p723-the-dns-record-that-points-at-nothing.md) <sub>P723 · script</sub>
- [Takeover before someone else does](notes/p724-takeover-before-someone-else-does.md) <sub>P724 · script</sub>
- [The asset nobody owns](notes/p725-the-asset-nobody-owns.md) <sub>P725 · script</sub>
- [Shadow IT in your own account](notes/p726-shadow-it-in-your-own-account.md) <sub>P726 · script</sub>
- [The admin panel on the internet](notes/p732-the-admin-panel-on-the-internet.md) <sub>P732 · script</sub>
- [API keys in the JavaScript](notes/p733-api-keys-in-the-javascript.md) <sub>P733 · script</sub>
- [The bucket that lists itself](notes/p734-the-bucket-that-lists-itself.md) <sub>P734 · script</sub>
- [Ports that should never face the internet](notes/p735-ports-that-should-never-face-the-internet.md) <sub>P735 · script</sub>
- [The API you forgot to authenticate](notes/p736-the-api-you-forgot-to-authenticate.md) <sub>P736 · script</sub>
- [Rank findings by exploit evidence](notes/p742-rank-findings-by-exploit-evidence.md) <sub>P742 · script</sub>
- [Match findings against the KEV catalog](notes/p743-match-findings-against-the-kev-catalog.md) <sub>P743 · script</sub>
- [Map vulnerable packages onto live import paths](notes/p744-map-vulnerable-packages-onto-live-import-paths.md) <sub>P744 · script</sub>
- [Score the asset, then rank the finding](notes/p745-score-the-asset-then-rank-the-finding.md) <sub>P745 · script</sub>
- [Merge the same finding from five scanners](notes/p746-merge-the-same-finding-from-five-scanners.md) <sub>P746 · script</sub>
- [Patch in waves, not in panic](notes/p752-patch-in-waves-not-in-panic.md) <sub>P752 · script</sub>
- [The exception that never expires](notes/p753-the-exception-that-never-expires.md) <sub>P753 · script</sub>
- [Did the fix actually fix it?](notes/p754-did-the-fix-actually-fix-it.md) <sub>P754 · script</sub>
- [Give the owner a packet, not a dashboard](notes/p755-give-the-owner-a-packet-not-a-dashboard.md) <sub>P755 · script</sub>
- [Escalate on evidence, not on mood](notes/p756-escalate-on-evidence-not-on-mood.md) <sub>P756 · script</sub>
- [One page for the board](notes/p762-one-page-for-the-board.md) <sub>P762 · script</sub>
- [Is it getting better?](notes/p763-is-it-getting-better.md) <sub>P763 · script</sub>
- [What the scanner never saw](notes/p764-what-the-scanner-never-saw.md) <sub>P764 · script</sub>
- [Map the finding to the control](notes/p765-map-the-finding-to-the-control.md) <sub>P765 · script</sub>
- [The audit packet](notes/p766-the-audit-packet.md) <sub>P766 · script</sub>

</details>

<details>
<summary><b>DevSecOps &amp; cloud security</b> · 43 notes</summary>

- [9 checks for a new cloud account](notes/p159-9-checks-for-a-new-cloud-account.md) <sub>P159</sub>
- [NSG vs Azure Firewall](notes/p188-nsg-vs-azure-firewall.md) <sub>P188</sub>
- [9 checks to secure an Azure subscription](notes/p190-9-checks-to-secure-an-azure-subscription.md) <sub>P190</sub>
- [9 commands for Kubernetes security (CKS)](notes/p213-9-commands-for-kubernetes-security-cks.md) <sub>P213</sub>
- [The secure software supply chain](notes/p215-the-secure-software-supply-chain.md) <sub>P215</sub>
- [5 Kubernetes security mistakes](notes/p216-5-kubernetes-security-mistakes.md) <sub>P216</sub>
- [Trivy vs Falco vs OPA Gatekeeper](notes/p218-trivy-vs-falco-vs-opa-gatekeeper.md) <sub>P218</sub>
- [6 Kubernetes security terms](notes/p219-6-kubernetes-security-terms.md) <sub>P219</sub>
- [The CKS exam by the numbers](notes/p220-the-cks-exam-by-the-numbers.md) <sub>P220</sub>
- [3 Kubernetes security questions](notes/p221-3-kubernetes-security-questions.md) <sub>P221</sub>
- [9 AWS IAM commands for access reviews](notes/p252-9-aws-iam-commands-for-access-reviews.md) <sub>P252</sub>
- [IRSA vs GKE Workload Identity vs Azure Workload Identity](notes/p253-irsa-vs-gke-workload-identity-vs-azure-workload-identity.md) <sub>P253</sub>
- [NetworkPolicy vs service mesh mTLS](notes/p255-networkpolicy-vs-service-mesh-mtls.md) <sub>P255</sub>
- [5 Kubernetes RBAC mistakes](notes/p256-5-kubernetes-rbac-mistakes.md) <sub>P256</sub>
- [How a pod becomes cluster admin](notes/p257-how-a-pod-becomes-cluster-admin.md) <sub>P257</sub>
- [Cloud security terms, decoded](notes/p258-cloud-security-terms-decoded.md) <sub>P258</sub>
- [Anatomy of an IAM policy statement](notes/p260-anatomy-of-an-iam-policy-statement.md) <sub>P260</sub>
- [Quiz: 3 cloud security questions](notes/p261-quiz-3-cloud-security-questions.md) <sub>P261</sub>
- [The shared responsibility model, drawn](notes/p284-the-shared-responsibility-model-drawn.md) <sub>P284</sub>
- [The software supply chain, drawn](notes/p306-the-software-supply-chain-drawn.md) <sub>P306</sub>
- [Four Kubernetes attack paths, drawn](notes/p307-four-kubernetes-attack-paths-drawn.md) <sub>P307</sub>
- [The AWS security cheat sheet](notes/p308-the-aws-security-cheat-sheet.md) <sub>P308</sub>
- [Secrets management: Vault vs cloud KMS vs SOPS](notes/p309-secrets-management-vault-vs-cloud-kms-vs-sops.md) <sub>P309</sub>
- [Quiz: 3 security questions](notes/p311-quiz-3-security-questions.md) <sub>P311</sub>
- [The secure SDLC, drawn](notes/p372-the-secure-sdlc-drawn.md) <sub>P372</sub>
- [Security posture at a glance](notes/p379-security-posture-at-a-glance.md) <sub>P379</sub>
- [DevSecOps terms, decoded](notes/p381-devsecops-terms-decoded.md) <sub>P381</sub>
- [Secret management architecture, drawn](notes/p383-secret-management-architecture-drawn.md) <sub>P383</sub>
- [Compliance posture at a glance](notes/p419-compliance-posture-at-a-glance.md) <sub>P419</sub>
- [The security automation pipeline, drawn](notes/p522-the-security-automation-pipeline-drawn.md) <sub>P522</sub>
- [Four rules for safe automation](notes/p524-four-rules-for-safe-automation.md) <sub>P524</sub>
- [9 steps to write a security script](notes/p527-9-steps-to-write-a-security-script.md) <sub>P527</sub>
- [Quiz: 3 automation questions](notes/p531-quiz-3-automation-questions.md) <sub>P531</sub>
- [Policy as code, in three tiers](notes/p542-policy-as-code-in-three-tiers.md) <sub>P542</sub>
- [Four policy checks that catch most misconfigs](notes/p544-four-policy-checks-that-catch-most-misconfigs.md) <sub>P544</sub>
- [5 scripting mistakes in cloud audits](notes/p547-5-scripting-mistakes-in-cloud-audits.md) <sub>P547</sub>
- [Quiz: 3 policy questions](notes/p551-quiz-3-policy-questions.md) <sub>P551</sub>
- [The reporting pipeline](notes/p562-the-reporting-pipeline.md) <sub>P562</sub>
- [The log redaction cheat sheet](notes/p563-the-log-redaction-cheat-sheet.md) <sub>P563</sub>
- [Four properties of a security report](notes/p564-four-properties-of-a-security-report.md) <sub>P564</sub>
- [Security automation at a glance](notes/p567-security-automation-at-a-glance.md) <sub>P567</sub>
- [Python security scripting terms](notes/p568-python-security-scripting-terms.md) <sub>P568</sub>
- [Quiz: 3 reporting questions](notes/p571-quiz-3-reporting-questions.md) <sub>P571</sub>

</details>

<details>
<summary><b>Kubernetes</b> · 34 notes</summary>

- [9 kubectl commands for troubleshooting](notes/p115-9-kubectl-commands-for-troubleshooting.md) <sub>P115</sub>
- [The cloud-native stack, layer by layer](notes/p142-the-cloud-native-stack-layer-by-layer.md) <sub>P142</sub>
- [Fix: Kubernetes ImagePullBackOff](notes/p143-fix-kubernetes-imagepullbackoff.md) <sub>P143</sub>
- [Kubernetes terms, decoded](notes/p156-kubernetes-terms-decoded.md) <sub>P156</sub>
- [What runs inside a Kubernetes node](notes/p157-what-runs-inside-a-kubernetes-node.md) <sub>P157</sub>
- [How a request reaches a pod in Kubernetes](notes/p160-how-a-request-reaches-a-pod-in-kubernetes.md) <sub>P160</sub>
- [5 Kubernetes mistakes in production](notes/p161-5-kubernetes-mistakes-in-production.md) <sub>P161</sub>
- [Quiz: 3 Kubernetes questions](notes/p162-quiz-3-kubernetes-questions.md) <sub>P162</sub>
- [Anatomy of a kubectl command](notes/p203-anatomy-of-a-kubectl-command.md) <sub>P203</sub>
- [9 imperative kubectl commands that save CKA exam time](notes/p204-9-imperative-kubectl-commands-that-save-cka-exam-time.md) <sub>P204</sub>
- [Fix: Kubernetes CrashLoopBackOff](notes/p205-fix-kubernetes-crashloopbackoff.md) <sub>P205</sub>
- [Deployment vs StatefulSet](notes/p206-deployment-vs-statefulset.md) <sub>P206</sub>
- [9 skills to have ready for the CKA exam](notes/p208-9-skills-to-have-ready-for-the-cka-exam.md) <sub>P208</sub>
- [The Kubernetes control plane, part by part](notes/p209-the-kubernetes-control-plane-part-by-part.md) <sub>P209</sub>
- [Kubernetes networking terms, decoded](notes/p210-kubernetes-networking-terms-decoded.md) <sub>P210</sub>
- [What happens when you run kubectl apply](notes/p211-what-happens-when-you-run-kubectl-apply.md) <sub>P211</sub>
- [6 Kubernetes numbers that decide capacity](notes/p248-6-kubernetes-numbers-that-decide-capacity.md) <sub>P248</sub>
- [Inside a Kubernetes cluster](notes/p278-inside-a-kubernetes-cluster.md) <sub>P278</sub>
- [The kubectl command cheat sheet](notes/p292-the-kubectl-command-cheat-sheet.md) <sub>P292</sub>
- [The four Kubernetes objects you actually use, drawn](notes/p298-the-four-kubernetes-objects-you-actually-use-drawn.md) <sub>P298</sub>
- [Pod-to-pod networking, drawn](notes/p502-pod-to-pod-networking-drawn.md) <sub>P502</sub>
- [The Kubernetes network debugging cheat sheet](notes/p503-the-kubernetes-network-debugging-cheat-sheet.md) <sub>P503</sub>
- [The four service types](notes/p504-the-four-service-types.md) <sub>P504</sub>
- [Ingress vs Gateway API](notes/p507-ingress-vs-gateway-api.md) <sub>P507</sub>
- [From kubectl apply to a routable service](notes/p508-from-kubectl-apply-to-a-routable-service.md) <sub>P508</sub>
- [The layers a pod packet crosses](notes/p509-the-layers-a-pod-packet-crosses.md) <sub>P509</sub>
- [Quiz: 3 Kubernetes network questions](notes/p510-quiz-3-kubernetes-network-questions.md) <sub>P510</sub>
- [Kubernetes networking terms](notes/p511-kubernetes-networking-terms.md) <sub>P511</sub>
- [OPA vs Kyverno vs a Python script](notes/p548-opa-vs-kyverno-vs-a-python-script.md) <sub>P548</sub>
- [The pod failure path, drawn](notes/p597-the-pod-failure-path-drawn.md) <sub>P597</sub>
- [The kubectl triage cheat sheet](notes/p598-the-kubectl-triage-cheat-sheet.md) <sub>P598</sub>
- [Four pod failure reasons](notes/p599-four-pod-failure-reasons.md) <sub>P599</sub>
- [9 commands to triage a failing pod](notes/p600-9-commands-to-triage-a-failing-pod.md) <sub>P600</sub>
- [Quiz: 3 Kubernetes failure questions](notes/p601-quiz-3-kubernetes-failure-questions.md) <sub>P601</sub>

</details>

<details>
<summary><b>Incident response &amp; detection</b> · 32 notes</summary>

- [The detection pipeline, drawn](notes/p412-the-detection-pipeline-drawn.md) <sub>P412</sub>
- [The detection engineering cheat sheet](notes/p413-the-detection-engineering-cheat-sheet.md) <sub>P413</sub>
- [Four SIEM detection patterns](notes/p414-four-siem-detection-patterns.md) <sub>P414</sub>
- [Anatomy of an audit event](notes/p417-anatomy-of-an-audit-event.md) <sub>P417</sub>
- [Security operations at a glance](notes/p418-security-operations-at-a-glance.md) <sub>P418</sub>
- [From alert to containment](notes/p420-from-alert-to-containment.md) <sub>P420</sub>
- [Detection and response terms, decoded](notes/p421-detection-and-response-terms-decoded.md) <sub>P421</sub>
- [The incident triage pipeline](notes/p677-the-incident-triage-pipeline.md) <sub>P677</sub>
- [Triage commands for the first ten minutes](notes/p678-triage-commands-for-the-first-ten-minutes.md) <sub>P678</sub>
- [Four triage mistakes](notes/p679-four-triage-mistakes.md) <sub>P679</sub>
- [9 steps from alert to incident](notes/p680-9-steps-from-alert-to-incident.md) <sub>P680</sub>
- [Quiz: 3 triage questions](notes/p681-quiz-3-triage-questions.md) <sub>P681</sub>
- [The containment tree](notes/p687-the-containment-tree.md) <sub>P687</sub>
- [Containment commands](notes/p688-containment-commands.md) <sub>P688</sub>
- [Four containment failures](notes/p689-four-containment-failures.md) <sub>P689</sub>
- [9 commands to contain a host](notes/p690-9-commands-to-contain-a-host.md) <sub>P690</sub>
- [Quiz: 3 containment questions](notes/p691-quiz-3-containment-questions.md) <sub>P691</sub>
- [The recovery path, drawn](notes/p697-the-recovery-path-drawn.md) <sub>P697</sub>
- [Recovery command cheat sheet](notes/p698-recovery-command-cheat-sheet.md) <sub>P698</sub>
- [Four recovery failures, explained](notes/p699-four-recovery-failures-explained.md) <sub>P699</sub>
- [9 checks before you call it recovered](notes/p700-9-checks-before-you-call-it-recovered.md) <sub>P700</sub>
- [Quiz: 3 recovery questions](notes/p701-quiz-3-recovery-questions.md) <sub>P701</sub>
- [The evidence path](notes/p707-the-evidence-path.md) <sub>P707</sub>
- [The evidence command sheet](notes/p708-the-evidence-command-sheet.md) <sub>P708</sub>
- [Four evidence failures](notes/p709-four-evidence-failures.md) <sub>P709</sub>
- [Status update by phase](notes/p710-status-update-by-phase.md) <sub>P710</sub>
- [Quiz: 3 evidence questions](notes/p711-quiz-3-evidence-questions.md) <sub>P711</sub>
- [The learning loop](notes/p717-the-learning-loop.md) <sub>P717</sub>
- [Post-incident commands](notes/p718-post-incident-commands.md) <sub>P718</sub>
- [Four learning failures](notes/p719-four-learning-failures.md) <sub>P719</sub>
- [5 postmortem mistakes](notes/p720-5-postmortem-mistakes-2.md) <sub>P720</sub>
- [Quiz: 3 learning questions](notes/p721-quiz-3-learning-questions.md) <sub>P721</sub>

</details>

<details>
<summary><b>Git &amp; CI/CD</b> · 31 notes</summary>

- [Quiz: 3 Git questions every developer should know](notes/p132-quiz-3-git-questions-every-developer-should-know.md) <sub>P132</sub>
- [9 git commands to undo mistakes](notes/p134-9-git-commands-to-undo-mistakes.md) <sub>P134</sub>
- [How a git push becomes a running deploy](notes/p145-how-a-git-push-becomes-a-running-deploy.md) <sub>P145</sub>
- [A zero-downtime deployment, minute by minute](notes/p153-a-zero-downtime-deployment-minute-by-minute.md) <sub>P153</sub>
- [Jenkins vs GitHub Actions vs GitLab CI](notes/p154-jenkins-vs-github-actions-vs-gitlab-ci.md) <sub>P154</sub>
- [9 git commands for reading history](notes/p155-9-git-commands-for-reading-history.md) <sub>P155</sub>
- [Fix: a failing GitHub Actions job](notes/p195-fix-a-failing-github-actions-job.md) <sub>P195</sub>
- [How a GitHub Actions workflow is structured](notes/p198-how-a-github-actions-workflow-is-structured.md) <sub>P198</sub>
- [Monorepo vs polyrepo](notes/p243-monorepo-vs-polyrepo.md) <sub>P243</sub>
- [How a commit reaches production, drawn](notes/p293-how-a-commit-reaches-production-drawn.md) <sub>P293</sub>
- [Git merge vs rebase, drawn](notes/p294-git-merge-vs-rebase-drawn.md) <sub>P294</sub>
- [5 CI/CD mistakes and the fix for each](notes/p299-5-ci-cd-mistakes-and-the-fix-for-each.md) <sub>P299</sub>
- [Hardening the CI/CD pipeline, drawn](notes/p392-hardening-the-ci-cd-pipeline-drawn.md) <sub>P392</sub>
- [The CI/CD security cheat sheet](notes/p393-the-ci-cd-security-cheat-sheet.md) <sub>P393</sub>
- [Four ways a CI pipeline leaks](notes/p395-four-ways-a-ci-pipeline-leaks.md) <sub>P395</sub>
- [Pipeline security at a glance](notes/p399-pipeline-security-at-a-glance.md) <sub>P399</sub>
- [A pipeline attack, minute by minute](notes/p400-a-pipeline-attack-minute-by-minute.md) <sub>P400</sub>
- [CI/CD security terms, decoded](notes/p401-ci-cd-security-terms-decoded.md) <sub>P401</sub>
- [The developer workflow cheat sheet](notes/p463-the-developer-workflow-cheat-sheet.md) <sub>P463</sub>
- [Anatomy of a commit message](notes/p467-anatomy-of-a-commit-message.md) <sub>P467</sub>
- [GitHub vs GitLab vs Bitbucket](notes/p469-github-vs-gitlab-vs-bitbucket.md) <sub>P469</sub>
- [Deploy verification, drawn](notes/p607-deploy-verification-drawn.md) <sub>P607</sub>
- [Deployment verification commands](notes/p608-deployment-verification-commands.md) <sub>P608</sub>
- [Four deploy failure modes](notes/p609-four-deploy-failure-modes.md) <sub>P609</sub>
- [Verify after deploy vs trust the pipeline](notes/p610-verify-after-deploy-vs-trust-the-pipeline.md) <sub>P610</sub>
- [Quiz: 3 deployment questions](notes/p611-quiz-3-deployment-questions.md) <sub>P611</sub>
- [The deploy gate, in three tiers](notes/p647-the-deploy-gate-in-three-tiers.md) <sub>P647</sub>
- [Deployment shell commands](notes/p648-deployment-shell-commands.md) <sub>P648</sub>
- [Four deploy failures](notes/p649-four-deploy-failures.md) <sub>P649</sub>
- [9 checks before a deploy](notes/p650-9-checks-before-a-deploy.md) <sub>P650</sub>
- [Quiz: 3 deploy questions](notes/p651-quiz-3-deploy-questions.md) <sub>P651</sub>

</details>

<details>
<summary><b>Vulnerability management &amp; attack surface</b> · 28 notes</summary>

- [Anatomy of a CVSS vector](notes/p378-anatomy-of-a-cvss-vector.md) <sub>P378</sub>
- [From vulnerability report to fix](notes/p380-from-vulnerability-report-to-fix.md) <sub>P380</sub>
- [From CVE publish to patch deployed](notes/p390-from-cve-publish-to-patch-deployed.md) <sub>P390</sub>
- [The surface map](notes/p727-the-surface-map.md) <sub>P727</sub>
- [Surface discovery commands](notes/p728-surface-discovery-commands.md) <sub>P728</sub>
- [Four surface blind spots](notes/p729-four-surface-blind-spots.md) <sub>P729</sub>
- [9 steps to map your attack surface](notes/p730-9-steps-to-map-your-attack-surface.md) <sub>P730</sub>
- [Quiz: 3 surface questions](notes/p731-quiz-3-surface-questions.md) <sub>P731</sub>
- [The exposure pipeline](notes/p737-the-exposure-pipeline.md) <sub>P737</sub>
- [Exposure hunting commands](notes/p738-exposure-hunting-commands.md) <sub>P738</sub>
- [Four exposures that persist](notes/p739-four-exposures-that-persist.md) <sub>P739</sub>
- [9 commands to check your exposure](notes/p740-9-commands-to-check-your-exposure.md) <sub>P740</sub>
- [Quiz: 3 exposure questions](notes/p741-quiz-3-exposure-questions.md) <sub>P741</sub>
- [The prioritisation ladder: signal, context, decision](notes/p747-the-prioritisation-ladder-signal-context-decision.md) <sub>P747</sub>
- [Prioritisation commands: EPSS, KEV, reachability, dedupe](notes/p748-prioritisation-commands-epss-kev-reachability-dedupe.md) <sub>P748</sub>
- [Four false priorities in vulnerability management](notes/p749-four-false-priorities-in-vulnerability-management.md) <sub>P749</sub>
- [9 checks before you call a finding critical](notes/p750-9-checks-before-you-call-a-finding-critical.md) <sub>P750</sub>
- [Quiz: 3 prioritisation questions](notes/p751-quiz-3-prioritisation-questions.md) <sub>P751</sub>
- [The remediation loop](notes/p757-the-remediation-loop.md) <sub>P757</sub>
- [Remediation commands](notes/p758-remediation-commands.md) <sub>P758</sub>
- [Four fixes that fail](notes/p759-four-fixes-that-fail.md) <sub>P759</sub>
- [Fix now vs fix later](notes/p760-fix-now-vs-fix-later.md) <sub>P760</sub>
- [Quiz: 3 remediation questions](notes/p761-quiz-3-remediation-questions.md) <sub>P761</sub>
- [The proof chain](notes/p767-the-proof-chain.md) <sub>P767</sub>
- [Reporting commands](notes/p768-reporting-commands.md) <sub>P768</sub>
- [Four reports that lie](notes/p769-four-reports-that-lie.md) <sub>P769</sub>
- [5 vulnerability programme mistakes](notes/p770-5-vulnerability-programme-mistakes.md) <sub>P770</sub>
- [Quiz: 3 proof questions](notes/p771-quiz-3-proof-questions.md) <sub>P771</sub>

</details>

<details>
<summary><b>Cloud: AWS &amp; Azure</b> · 27 notes</summary>

- [9 AWS CLI commands every admin should know](notes/p126-9-aws-cli-commands-every-admin-should-know.md) <sub>P126</sub>
- [AWS vs Azure vs GCP: core services](notes/p139-aws-vs-azure-vs-gcp-core-services.md) <sub>P139</sub>
- [Cloud acronyms, decoded](notes/p171-cloud-acronyms-decoded.md) <sub>P171</sub>
- [9 Azure CLI commands for AZ-104](notes/p183-9-azure-cli-commands-for-az-104.md) <sub>P183</sub>
- [Azure Blob storage tiers: Hot vs Cool vs Archive](notes/p184-azure-blob-storage-tiers-hot-vs-cool-vs-archive.md) <sub>P184</sub>
- [Anatomy of an Azure resource ID](notes/p185-anatomy-of-an-azure-resource-id.md) <sub>P185</sub>
- [6 Azure numbers worth knowing](notes/p186-6-azure-numbers-worth-knowing.md) <sub>P186</sub>
- [How a request reaches a VM in Azure](notes/p189-how-a-request-reaches-a-vm-in-azure.md) <sub>P189</sub>
- [Azure cost at a glance](notes/p191-azure-cost-at-a-glance.md) <sub>P191</sub>
- [The 3-tier architecture on AWS, drawn](notes/p272-the-3-tier-architecture-on-aws-drawn.md) <sub>P272</sub>
- [A serverless web app on AWS, drawn](notes/p282-a-serverless-web-app-on-aws-drawn.md) <sub>P282</sub>
- [The AWS CLI cheat sheet](notes/p283-the-aws-cli-cheat-sheet.md) <sub>P283</sub>
- [Multi-region active-active, drawn](notes/p286-multi-region-active-active-drawn.md) <sub>P286</sub>
- [VPC anatomy, drawn](notes/p287-vpc-anatomy-drawn.md) <sub>P287</sub>
- [The Azure CLI cheat sheet](notes/p288-the-azure-cli-cheat-sheet.md) <sub>P288</sub>
- [5 cloud architecture mistakes](notes/p289-5-cloud-architecture-mistakes.md) <sub>P289</sub>
- [Quiz: 3 cloud architecture questions](notes/p291-quiz-3-cloud-architecture-questions.md) <sub>P291</sub>
- [VPC routing, drawn](notes/p492-vpc-routing-drawn.md) <sub>P492</sub>
- [The VPC troubleshooting cheat sheet](notes/p493-the-vpc-troubleshooting-cheat-sheet.md) <sub>P493</sub>
- [Four reasons a packet is dropped](notes/p494-four-reasons-a-packet-is-dropped.md) <sub>P494</sub>
- [Peering vs Transit Gateway vs PrivateLink](notes/p497-peering-vs-transit-gateway-vs-privatelink.md) <sub>P497</sub>
- [Anatomy of a route table entry](notes/p498-anatomy-of-a-route-table-entry.md) <sub>P498</sub>
- [The life of a NAT connection](notes/p499-the-life-of-a-nat-connection.md) <sub>P499</sub>
- [Quiz: 3 cloud network questions](notes/p500-quiz-3-cloud-network-questions.md) <sub>P500</sub>
- [5 VPC mistakes](notes/p501-5-vpc-mistakes.md) <sub>P501</sub>
- [Querying cloud JSON without an SDK](notes/p543-querying-cloud-json-without-an-sdk.md) <sub>P543</sub>
- [Four data and cost leaks](notes/p619-four-data-and-cost-leaks.md) <sub>P619</sub>

</details>

<details>
<summary><b>Shell scripts</b> · 25 notes</summary>

- [Logs that never rotate](notes/p622-logs-that-never-rotate.md) <sub>P622 · script</sub>
- [Accounts hiding in plain sight](notes/p623-accounts-hiding-in-plain-sight.md) <sub>P623 · script</sub>
- [Ports nobody remembers opening](notes/p624-ports-nobody-remembers-opening.md) <sub>P624 · script</sub>
- [Services that died quietly](notes/p625-services-that-died-quietly.md) <sub>P625 · script</sub>
- [Packages that changed without a deploy](notes/p626-packages-that-changed-without-a-deploy.md) <sub>P626 · script</sub>
- [Config that drifted overnight](notes/p632-config-that-drifted-overnight.md) <sub>P632 · script</sub>
- [SSH keys you forgot about](notes/p633-ssh-keys-you-forgot-about.md) <sub>P633 · script</sub>
- [TLS that is still offering 1.0](notes/p634-tls-that-is-still-offering-1-0.md) <sub>P634 · script</sub>
- [Files that changed under you](notes/p635-files-that-changed-under-you.md) <sub>P635 · script</sub>
- [Certificates before they expire](notes/p636-certificates-before-they-expire.md) <sub>P636 · script</sub>
- [A deploy gate that says no](notes/p642-a-deploy-gate-that-says-no.md) <sub>P642 · script</sub>
- [The rollback nobody tested](notes/p643-the-rollback-nobody-tested.md) <sub>P643 · script</sub>
- [Artifacts that did not arrive](notes/p644-artifacts-that-did-not-arrive.md) <sub>P644 · script</sub>
- [A smoke test with teeth](notes/p645-a-smoke-test-with-teeth.md) <sub>P645 · script</sub>
- [CI caches that ate the disk](notes/p646-ci-caches-that-ate-the-disk.md) <sub>P646 · script</sub>
- [SUID binaries that appeared overnight](notes/p652-suid-binaries-that-appeared-overnight.md) <sub>P652 · script</sub>
- [Secrets in crontabs and env files](notes/p653-secrets-in-crontabs-and-env-files.md) <sub>P653 · script</sub>
- [An image gate for the registry](notes/p654-an-image-gate-for-the-registry.md) <sub>P654 · script</sub>
- [Logins that do not look right](notes/p655-logins-that-do-not-look-right.md) <sub>P655 · script</sub>
- [ACLs that override your permissions](notes/p656-acls-that-override-your-permissions.md) <sub>P656 · script</sub>
- [Retention that never ran](notes/p662-retention-that-never-ran.md) <sub>P662 · script</sub>
- [A backup that copied nothing](notes/p663-a-backup-that-copied-nothing.md) <sub>P663 · script</sub>
- [The cron job that overlapped](notes/p664-the-cron-job-that-overlapped.md) <sub>P664 · script</sub>
- [Renewed certificate, old process](notes/p665-renewed-certificate-old-process.md) <sub>P665 · script</sub>
- [The disk nobody will clean](notes/p666-the-disk-nobody-will-clean.md) <sub>P666 · script</sub>

</details>

<details>
<summary><b>Networking &amp; DNS</b> · 24 notes</summary>

- [Subnet sizes cheat sheet](notes/p127-subnet-sizes-cheat-sheet.md) <sub>P127</sub>
- [The TCP handshake in four panels](notes/p472-the-tcp-handshake-in-four-panels.md) <sub>P472</sub>
- [The network debugging cheat sheet](notes/p473-the-network-debugging-cheat-sheet.md) <sub>P473</sub>
- [The edge path](notes/p477-the-edge-path.md) <sub>P477</sub>
- [Anatomy of a connection tuple](notes/p478-anatomy-of-a-connection-tuple.md) <sub>P478</sub>
- [The life of a TCP connection](notes/p479-the-life-of-a-tcp-connection.md) <sub>P479</sub>
- [Quiz: 3 packet questions](notes/p480-quiz-3-packet-questions.md) <sub>P480</sub>
- [5 network mistakes](notes/p481-5-network-mistakes.md) <sub>P481</sub>
- [How DNS resolves a name](notes/p482-how-dns-resolves-a-name.md) <sub>P482</sub>
- [The DNS records cheat sheet](notes/p483-the-dns-records-cheat-sheet.md) <sub>P483</sub>
- [DNS TTL and failover](notes/p484-dns-ttl-and-failover.md) <sub>P484</sub>
- [IPv4 vs IPv6](notes/p487-ipv4-vs-ipv6.md) <sub>P487</sub>
- [Anatomy of a DNS record](notes/p488-anatomy-of-a-dns-record.md) <sub>P488</sub>
- [DNS health at a glance](notes/p489-dns-health-at-a-glance.md) <sub>P489</sub>
- [Quiz: 3 DNS questions](notes/p490-quiz-3-dns-questions.md) <sub>P490</sub>
- [DNS terms, decoded](notes/p491-dns-terms-decoded.md) <sub>P491</sub>
- [The network observability path, drawn](notes/p512-the-network-observability-path-drawn.md) <sub>P512</sub>
- [The packet capture cheat sheet](notes/p513-the-packet-capture-cheat-sheet.md) <sub>P513</sub>
- [Latency, bandwidth and throughput, drawn](notes/p514-latency-bandwidth-and-throughput-drawn.md) <sub>P514</sub>
- [6 network numbers](notes/p517-6-network-numbers.md) <sub>P517</sub>
- [Network health at a glance](notes/p518-network-health-at-a-glance.md) <sub>P518</sub>
- [Anatomy of a network incident](notes/p519-anatomy-of-a-network-incident.md) <sub>P519</sub>
- [Quiz: 3 network operations questions](notes/p520-quiz-3-network-operations-questions.md) <sub>P520</sub>
- [Network terms, decoded](notes/p521-network-terms-decoded.md) <sub>P521</sub>

</details>

<details>
<summary><b>Security &amp; hardening</b> · 24 notes</summary>

- [9 firewall checks with ufw](notes/p081-9-firewall-checks-with-ufw.md) <sub>P81</sub>
- [Defense in depth: 6 layers of security](notes/p098-defense-in-depth-6-layers-of-security.md) <sub>P98</sub>
- [Hashing vs Encryption](notes/p117-hashing-vs-encryption.md) <sub>P117</sub>
- [9 nmap commands to check your own network](notes/p119-9-nmap-commands-to-check-your-own-network.md) <sub>P119</sub>
- [5 password and access mistakes](notes/p124-5-password-and-access-mistakes.md) <sub>P124</sub>
- [9 checks to harden a fresh RHEL server](notes/p178-9-checks-to-harden-a-fresh-rhel-server.md) <sub>P178</sub>
- [firewalld vs iptables](notes/p179-firewalld-vs-iptables.md) <sub>P179</sub>
- [Zero-trust architecture, drawn](notes/p302-zero-trust-architecture-drawn.md) <sub>P302</sub>
- [The security command cheat sheet](notes/p304-the-security-command-cheat-sheet.md) <sub>P304</sub>
- [The certificate lifecycle](notes/p587-the-certificate-lifecycle.md) <sub>P587</sub>
- [The certificate and key cheat sheet](notes/p588-the-certificate-and-key-cheat-sheet.md) <sub>P588</sub>
- [Four identity failures](notes/p589-four-identity-failures.md) <sub>P589</sub>
- [9 checks before an access review](notes/p590-9-checks-before-an-access-review.md) <sub>P590</sub>
- [Quiz: 3 access questions](notes/p591-quiz-3-access-questions.md) <sub>P591</sub>
- [The config and crypto sweep](notes/p637-the-config-and-crypto-sweep.md) <sub>P637</sub>
- [The openssl shell cheat sheet](notes/p638-the-openssl-shell-cheat-sheet.md) <sub>P638</sub>
- [Four config and crypto failures](notes/p639-four-config-and-crypto-failures.md) <sub>P639</sub>
- [9 steps of a config audit](notes/p640-9-steps-of-a-config-audit.md) <sub>P640</sub>
- [Quiz: 3 config questions](notes/p641-quiz-3-config-questions.md) <sub>P641</sub>
- [The security sweep](notes/p657-the-security-sweep.md) <sub>P657</sub>
- [Security shell commands](notes/p658-security-shell-commands.md) <sub>P658</sub>
- [Four security regressions](notes/p659-four-security-regressions.md) <sub>P659</sub>
- [Bash script vs security tool](notes/p660-bash-script-vs-security-tool.md) <sub>P660</sub>
- [Quiz: 3 security questions](notes/p661-quiz-3-security-questions-2.md) <sub>P661</sub>

</details>

<details>
<summary><b>Application &amp; API security</b> · 21 notes</summary>

- [The security review path, drawn](notes/p373-the-security-review-path-drawn.md) <sub>P373</sub>
- [The threat modelling cheat sheet](notes/p374-the-threat-modelling-cheat-sheet.md) <sub>P374</sub>
- [The secure code review cheat sheet](notes/p375-the-secure-code-review-cheat-sheet.md) <sub>P375</sub>
- [The four questions of threat modelling](notes/p376-the-four-questions-of-threat-modelling.md) <sub>P376</sub>
- [The SAST, DAST and SCA cheat sheet](notes/p384-the-sast-dast-and-sca-cheat-sheet.md) <sub>P384</sub>
- [SAST vs DAST vs SCA, drawn](notes/p385-sast-vs-dast-vs-sca-drawn.md) <sub>P385</sub>
- [The request security path, drawn](notes/p402-the-request-security-path-drawn.md) <sub>P402</sub>
- [The API security testing cheat sheet](notes/p403-the-api-security-testing-cheat-sheet.md) <sub>P403</sub>
- [XSS in four panels, drawn](notes/p404-xss-in-four-panels-drawn.md) <sub>P404</sub>
- [SQL injection to a parameterised query, drawn](notes/p405-sql-injection-to-a-parameterised-query-drawn.md) <sub>P405</sub>
- [Anatomy of an SSRF target](notes/p407-anatomy-of-an-ssrf-target.md) <sub>P407</sub>
- [Anatomy of a Set-Cookie header](notes/p408-anatomy-of-a-set-cookie-header.md) <sub>P408</sub>
- [Application security at a glance](notes/p409-application-security-at-a-glance.md) <sub>P409</sub>
- [Anatomy of an API attack](notes/p410-anatomy-of-an-api-attack.md) <sub>P410</sub>
- [AppSec terms, decoded](notes/p411-appsec-terms-decoded.md) <sub>P411</sub>
- [The API security check, in three tiers](notes/p552-the-api-security-check-in-three-tiers.md) <sub>P552</sub>
- [The HTTP security header cheat sheet](notes/p553-the-http-security-header-cheat-sheet.md) <sub>P553</sub>
- [Four header defences and what each stops](notes/p554-four-header-defences-and-what-each-stops.md) <sub>P554</sub>
- [6 status codes in API security](notes/p557-6-status-codes-in-api-security.md) <sub>P557</sub>
- [The layers of web request defence](notes/p560-the-layers-of-web-request-defence.md) <sub>P560</sub>
- [Quiz: 3 web security questions](notes/p561-quiz-3-web-security-questions.md) <sub>P561</sub>

</details>

<details>
<summary><b>Observability &amp; SRE</b> · 21 notes</summary>

- [Uptime math: what each nine really allows](notes/p116-uptime-math-what-each-nine-really-allows.md) <sub>P116</sub>
- [The four golden signals of monitoring](notes/p150-the-four-golden-signals-of-monitoring.md) <sub>P150</sub>
- [An SLO and error budget at a glance](notes/p165-an-slo-and-error-budget-at-a-glance.md) <sub>P165</sub>
- [6 timeouts every DevOps should set](notes/p166-6-timeouts-every-devops-should-set.md) <sub>P166</sub>
- [9 PromQL queries for real incidents](notes/p232-9-promql-queries-for-real-incidents.md) <sub>P232</sub>
- [The observability stack, layer by layer](notes/p233-the-observability-stack-layer-by-layer.md) <sub>P233</sub>
- [6 numbers that set your monitoring](notes/p235-6-numbers-that-set-your-monitoring.md) <sub>P235</sub>
- [Logs vs metrics vs traces](notes/p236-logs-vs-metrics-vs-traces.md) <sub>P236</sub>
- [How a metric becomes an alert](notes/p237-how-a-metric-becomes-an-alert.md) <sub>P237</sub>
- [5 observability mistakes](notes/p238-5-observability-mistakes.md) <sub>P238</sub>
- [Anatomy of an alert rule](notes/p240-anatomy-of-an-alert-rule.md) <sub>P240</sub>
- [Quiz: 3 observability questions](notes/p241-quiz-3-observability-questions.md) <sub>P241</sub>
- [The observability pipeline, drawn](notes/p297-the-observability-pipeline-drawn.md) <sub>P297</sub>
- [The on-call system, drawn](notes/p452-the-on-call-system-drawn.md) <sub>P452</sub>
- [The incident command cheat sheet](notes/p453-the-incident-command-cheat-sheet.md) <sub>P453</sub>
- [Four levels of incident severity](notes/p454-four-levels-of-incident-severity.md) <sub>P454</sub>
- [9 checks before you go on call](notes/p457-9-checks-before-you-go-on-call.md) <sub>P457</sub>
- [The layers of incident response](notes/p458-the-layers-of-incident-response.md) <sub>P458</sub>
- [5 postmortem mistakes](notes/p459-5-postmortem-mistakes.md) <sub>P459</sub>
- [Quiz: 3 operations questions](notes/p460-quiz-3-operations-questions.md) <sub>P460</sub>
- [On-call terms, decoded](notes/p461-on-call-terms-decoded.md) <sub>P461</sub>

</details>

<details>
<summary><b>Linux</b> · 20 notes</summary>

- [5 Bash script mistakes that bite in production](notes/p079-5-bash-script-mistakes-that-bite-in-production.md) <sub>P79</sub>
- [The life of a log line](notes/p090-the-life-of-a-log-line.md) <sub>P90</sub>
- [What a healthy Linux server looks like](notes/p135-what-a-healthy-linux-server-looks-like.md) <sub>P135</sub>
- [9 jq commands for working with JSON](notes/p140-9-jq-commands-for-working-with-json.md) <sub>P140</sub>
- [9 SELinux commands that fix Permission denied](notes/p173-9-selinux-commands-that-fix-permission-denied.md) <sub>P173</sub>
- [Fix: the app works with SELinux off, fails with it on](notes/p176-fix-the-app-works-with-selinux-off-fails-with-it-on.md) <sub>P176</sub>
- [The layers that decide who can touch a file on RHEL](notes/p180-the-layers-that-decide-who-can-touch-a-file-on-rhel.md) <sub>P180</sub>
- [Quiz: 3 RHCSA questions](notes/p181-quiz-3-rhcsa-questions.md) <sub>P181</sub>
- [The Linux command cheat sheet](notes/p274-the-linux-command-cheat-sheet.md) <sub>P274</sub>
- [First-response commands for a host incident](notes/p578-first-response-commands-for-a-host-incident.md) <sub>P578</sub>
- [Four host failure modes](notes/p579-four-host-failure-modes.md) <sub>P579</sub>
- [Quiz: 3 host incident questions](notes/p581-quiz-3-host-incident-questions.md) <sub>P581</sub>
- [The host triage flow](notes/p627-the-host-triage-flow.md) <sub>P627</sub>
- [Bash one-liners for host triage](notes/p628-bash-one-liners-for-host-triage.md) <sub>P628</sub>
- [Four host signals](notes/p629-four-host-signals.md) <sub>P629</sub>
- [9 shell commands for a host checkup](notes/p630-9-shell-commands-for-a-host-checkup.md) <sub>P630</sub>
- [Quiz: 3 host questions](notes/p631-quiz-3-host-questions.md) <sub>P631</sub>
- [Cron and systemd automation commands](notes/p668-cron-and-systemd-automation-commands.md) <sub>P668</sub>
- [5 shell scripting mistakes](notes/p670-5-shell-scripting-mistakes.md) <sub>P670</sub>
- [Quiz: 3 automation questions](notes/p671-quiz-3-automation-questions-2.md) <sub>P671</sub>

</details>

<details>
<summary><b>AI infrastructure &amp; LLM security</b> · 16 notes</summary>

- [The LLM application stack, layer by layer](notes/p262-the-llm-application-stack-layer-by-layer.md) <sub>P262</sub>
- [RAG vs fine-tuning](notes/p263-rag-vs-fine-tuning.md) <sub>P263</sub>
- [5 LLM app security mistakes](notes/p265-5-llm-app-security-mistakes.md) <sub>P265</sub>
- [A prompt's journey through a gateway](notes/p266-a-prompts-journey-through-a-gateway.md) <sub>P266</sub>
- [9 checks before you expose an LLM app](notes/p267-9-checks-before-you-expose-an-llm-app.md) <sub>P267</sub>
- [6 GPU numbers for platform teams](notes/p268-6-gpu-numbers-for-platform-teams.md) <sub>P268</sub>
- [LLM security terms, decoded](notes/p270-llm-security-terms-decoded.md) <sub>P270</sub>
- [Quiz: 3 LLM security questions](notes/p271-quiz-3-llm-security-questions.md) <sub>P271</sub>
- [RAG architecture, drawn](notes/p312-rag-architecture-drawn.md) <sub>P312</sub>
- [Anatomy of an agent, drawn](notes/p313-anatomy-of-an-agent-drawn.md) <sub>P313</sub>
- [The LLM API cheat sheet](notes/p314-the-llm-api-cheat-sheet.md) <sub>P314</sub>
- [A GPU training cluster, drawn](notes/p316-a-gpu-training-cluster-drawn.md) <sub>P316</sub>
- [The GPU and Kubernetes cheat sheet](notes/p317-the-gpu-and-kubernetes-cheat-sheet.md) <sub>P317</sub>
- [Tokens, context and cost, drawn](notes/p318-tokens-context-and-cost-drawn.md) <sub>P318</sub>
- [AI infrastructure terms, decoded](notes/p319-ai-infrastructure-terms-decoded.md) <sub>P319</sub>
- [Quiz: 3 AI infrastructure questions](notes/p321-quiz-3-ai-infrastructure-questions.md) <sub>P321</sub>

</details>

<details>
<summary><b>Data engineering</b> · 16 notes</summary>

- [Kafka architecture, drawn](notes/p352-kafka-architecture-drawn.md) <sub>P352</sub>
- [Kafka delivery semantics, drawn](notes/p353-kafka-delivery-semantics-drawn.md) <sub>P353</sub>
- [The Kafka CLI cheat sheet](notes/p354-the-kafka-cli-cheat-sheet.md) <sub>P354</sub>
- [ETL and ELT, drawn](notes/p356-etl-and-elt-drawn.md) <sub>P356</sub>
- [The lakehouse layers, drawn](notes/p357-the-lakehouse-layers-drawn.md) <sub>P357</sub>
- [The window functions cheat sheet](notes/p358-the-window-functions-cheat-sheet.md) <sub>P358</sub>
- [5 data pipeline mistakes and the fix for each](notes/p359-5-data-pipeline-mistakes-and-the-fix-for-each.md) <sub>P359</sub>
- [Quiz: 3 pipeline questions](notes/p361-quiz-3-pipeline-questions.md) <sub>P361</sub>
- [The feature store, drawn](notes/p362-the-feature-store-drawn.md) <sub>P362</sub>
- [Vector search in four steps](notes/p363-vector-search-in-four-steps.md) <sub>P363</sub>
- [The pgvector cheat sheet](notes/p364-the-pgvector-cheat-sheet.md) <sub>P364</sub>
- [Lakehouse governance, drawn](notes/p366-lakehouse-governance-drawn.md) <sub>P366</sub>
- [Data quality, four checks](notes/p367-data-quality-four-checks.md) <sub>P367</sub>
- [The dbt cheat sheet](notes/p368-the-dbt-cheat-sheet.md) <sub>P368</sub>
- [Data terms, decoded](notes/p369-data-terms-decoded.md) <sub>P369</sub>
- [Quiz: 3 data questions](notes/p371-quiz-3-data-questions.md) <sub>P371</sub>

</details>

<details>
<summary><b>Release &amp; build engineering</b> · 16 notes</summary>

- [The release path, drawn](notes/p422-the-release-path-drawn.md) <sub>P422</sub>
- [The git release cheat sheet](notes/p423-the-git-release-cheat-sheet.md) <sub>P423</sub>
- [Canary, blue-green and rolling, drawn](notes/p424-canary-blue-green-and-rolling-drawn.md) <sub>P424</sub>
- [9 steps to a repeatable release](notes/p427-9-steps-to-a-repeatable-release.md) <sub>P427</sub>
- [Trunk-based vs GitFlow](notes/p428-trunk-based-vs-gitflow.md) <sub>P428</sub>
- [A feature flag's life](notes/p429-a-feature-flags-life.md) <sub>P429</sub>
- [Quiz: 3 release questions](notes/p430-quiz-3-release-questions.md) <sub>P430</sub>
- [Anatomy of a semantic version](notes/p431-anatomy-of-a-semantic-version.md) <sub>P431</sub>
- [The build cache, drawn](notes/p432-the-build-cache-drawn.md) <sub>P432</sub>
- [The Docker build cheat sheet](notes/p433-the-docker-build-cheat-sheet.md) <sub>P433</sub>
- [Why builds are slow](notes/p434-why-builds-are-slow.md) <sub>P434</sub>
- [9 checks for a reproducible build](notes/p437-9-checks-for-a-reproducible-build.md) <sub>P437</sub>
- [9 commands to debug a slow build](notes/p438-9-commands-to-debug-a-slow-build.md) <sub>P438</sub>
- [Make vs Bazel vs Nx](notes/p439-make-vs-bazel-vs-nx.md) <sub>P439</sub>
- [Quiz: 3 build questions](notes/p440-quiz-3-build-questions.md) <sub>P440</sub>
- [6 numbers in a build pipeline](notes/p441-6-numbers-in-a-build-pipeline.md) <sub>P441</sub>

</details>

<details>
<summary><b>DevOps basics</b> · 14 notes</summary>

- [Latency numbers every engineer should know](notes/p136-latency-numbers-every-engineer-should-know.md) <sub>P136</sub>
- [DevOps jargon, decoded](notes/p141-devops-jargon-decoded.md) <sub>P141</sub>
- [9 checks before a service is production-ready](notes/p144-9-checks-before-a-service-is-production-ready.md) <sub>P144</sub>
- [Horizontal vs Vertical scaling](notes/p167-horizontal-vs-vertical-scaling.md) <sub>P167</sub>
- [The DORA metrics: 4 numbers that measure delivery](notes/p200-the-dora-metrics-4-numbers-that-measure-delivery.md) <sub>P200</sub>
- [Quiz: 3 toolchain questions](notes/p301-quiz-3-toolchain-questions.md) <sub>P301</sub>
- [Environment topology, drawn](notes/p442-environment-topology-drawn.md) <sub>P442</sub>
- [The environment debugging cheat sheet](notes/p443-the-environment-debugging-cheat-sheet.md) <sub>P443</sub>
- [Four sources of environment drift](notes/p444-four-sources-of-environment-drift.md) <sub>P444</sub>
- [9 steps to a preview environment](notes/p447-9-steps-to-a-preview-environment.md) <sub>P447</sub>
- [Environment variables vs a config service](notes/p448-environment-variables-vs-a-config-service.md) <sub>P448</sub>
- [Environment health at a glance](notes/p449-environment-health-at-a-glance.md) <sub>P449</sub>
- [Quiz: 3 environment questions](notes/p450-quiz-3-environment-questions.md) <sub>P450</sub>
- [5 environment mistakes](notes/p451-5-environment-mistakes.md) <sub>P451</sub>

</details>

<details>
<summary><b>Docker &amp; containers</b> · 12 notes</summary>

- [9 docker commands for when a container fails](notes/p108-9-docker-commands-for-when-a-container-fails.md) <sub>P108</sub>
- [What is inside a Docker image](notes/p109-what-is-inside-a-docker-image.md) <sub>P109</sub>
- [5 Docker mistakes in production](notes/p113-5-docker-mistakes-in-production.md) <sub>P113</sub>
- [Anatomy of a docker run command](notes/p133-anatomy-of-a-docker-run-command.md) <sub>P133</sub>
- [Quiz: 3 container questions](notes/p147-quiz-3-container-questions.md) <sub>P147</sub>
- [Docker Compose vs Kubernetes](notes/p152-docker-compose-vs-kubernetes.md) <sub>P152</sub>
- [Anatomy of a container image reference](notes/p163-anatomy-of-a-container-image-reference.md) <sub>P163</sub>
- [9 docker compose commands for daily work](notes/p164-9-docker-compose-commands-for-daily-work.md) <sub>P164</sub>
- [9 docker commands for building and shipping images](notes/p194-9-docker-commands-for-building-and-shipping-images.md) <sub>P194</sub>
- [Alpine vs Debian base images](notes/p196-alpine-vs-debian-base-images.md) <sub>P196</sub>
- [5 Dockerfile mistakes to avoid](notes/p199-5-dockerfile-mistakes-to-avoid.md) <sub>P199</sub>
- [The Docker command cheat sheet](notes/p277-the-docker-command-cheat-sheet.md) <sub>P277</sub>

</details>

<details>
<summary><b>Supply chain &amp; SBOM</b> · 12 notes</summary>

- [The dependency supply chain, drawn](notes/p382-the-dependency-supply-chain-drawn.md) <sub>P382</sub>
- [Dependency confusion and typosquatting, drawn](notes/p386-dependency-confusion-and-typosquatting-drawn.md) <sub>P386</sub>
- [Anatomy of a dependency path](notes/p388-anatomy-of-a-dependency-path.md) <sub>P388</sub>
- [Dependency risk at a glance](notes/p389-dependency-risk-at-a-glance.md) <sub>P389</sub>
- [Supply chain terms, decoded](notes/p391-supply-chain-terms-decoded.md) <sub>P391</sub>
- [Anatomy of a signed image reference](notes/p398-anatomy-of-a-signed-image-reference.md) <sub>P398</sub>
- [The SBOM pipeline, drawn](notes/p532-the-sbom-pipeline-drawn.md) <sub>P532</sub>
- [The SBOM and licence cheat sheet](notes/p533-the-sbom-and-licence-cheat-sheet.md) <sub>P533</sub>
- [What to check in a dependency](notes/p534-what-to-check-in-a-dependency.md) <sub>P534</sub>
- [SBOM vs lockfile](notes/p537-sbom-vs-lockfile.md) <sub>P537</sub>
- [9 checks before trusting a dependency](notes/p538-9-checks-before-trusting-a-dependency.md) <sub>P538</sub>
- [Quiz: 3 supply-chain questions](notes/p541-quiz-3-supply-chain-questions.md) <sub>P541</sub>

</details>

<details>
<summary><b>Terraform, Ansible &amp; IaC</b> · 11 notes</summary>

- [Terraform vs Ansible](notes/p137-terraform-vs-ansible.md) <sub>P137</sub>
- [5 Terraform mistakes to avoid](notes/p146-5-terraform-mistakes-to-avoid.md) <sub>P146</sub>
- [9 terraform commands every engineer should know](notes/p149-9-terraform-commands-every-engineer-should-know.md) <sub>P149</sub>
- [Fix: Terraform state lock](notes/p158-fix-terraform-state-lock.md) <sub>P158</sub>
- [Terraform vs CloudFormation vs Pulumi](notes/p169-terraform-vs-cloudformation-vs-pulumi.md) <sub>P169</sub>
- [9 ansible commands to start with](notes/p170-9-ansible-commands-to-start-with.md) <sub>P170</sub>
- [Anatomy of a Terraform resource block](notes/p193-anatomy-of-a-terraform-resource-block.md) <sub>P193</sub>
- [Quiz: 3 Terraform questions](notes/p201-quiz-3-terraform-questions.md) <sub>P201</sub>
- [Terraform vs Crossplane vs Pulumi](notes/p246-terraform-vs-crossplane-vs-pulumi.md) <sub>P246</sub>
- [The Terraform command cheat sheet](notes/p296-the-terraform-command-cheat-sheet.md) <sub>P296</sub>
- [The IaC scanning cheat sheet](notes/p394-the-iac-scanning-cheat-sheet.md) <sub>P394</sub>

</details>

<details>
<summary><b>Platform engineering</b> · 10 notes</summary>

- [Platform engineering terms, decoded](notes/p242-platform-engineering-terms-decoded.md) <sub>P242</sub>
- [9 checks for a golden-path template](notes/p245-9-checks-for-a-golden-path-template.md) <sub>P245</sub>
- [A developer's first deploy, hour by hour](notes/p247-a-developers-first-deploy-hour-by-hour.md) <sub>P247</sub>
- [Anatomy of a Backstage catalog-info.yaml](notes/p250-anatomy-of-a-backstage-catalog-info-yaml.md) <sub>P250</sub>
- [Quiz: 3 platform engineering questions](notes/p251-quiz-3-platform-engineering-questions.md) <sub>P251</sub>
- [The developer workflow, drawn](notes/p462-the-developer-workflow-drawn.md) <sub>P462</sub>
- [Where developer time goes](notes/p464-where-developer-time-goes.md) <sub>P464</sub>
- [Developer experience at a glance](notes/p468-developer-experience-at-a-glance.md) <sub>P468</sub>
- [Quiz: 3 developer experience questions](notes/p470-quiz-3-developer-experience-questions.md) <sub>P470</sub>
- [DevEx terms, decoded](notes/p471-devex-terms-decoded.md) <sub>P471</sub>

</details>

<details>
<summary><b>GitOps &amp; Helm</b> · 9 notes</summary>

- [Argo CD vs Flux (GitOps)](notes/p214-argo-cd-vs-flux-gitops.md) <sub>P214</sub>
- [9 Argo CD commands for daily GitOps work](notes/p222-9-argo-cd-commands-for-daily-gitops-work.md) <sub>P222</sub>
- [Anatomy of a helm upgrade](notes/p223-anatomy-of-a-helm-upgrade.md) <sub>P223</sub>
- [Helm vs Kustomize](notes/p225-helm-vs-kustomize.md) <sub>P225</sub>
- [9 checks before you enable auto-sync](notes/p226-9-checks-before-you-enable-auto-sync.md) <sub>P226</sub>
- [How a commit reaches the cluster](notes/p227-how-a-commit-reaches-the-cluster.md) <sub>P227</sub>
- [5 GitOps mistakes and the fix for each](notes/p228-5-gitops-mistakes-and-the-fix-for-each.md) <sub>P228</sub>
- [GitOps terms, decoded](notes/p230-gitops-terms-decoded.md) <sub>P230</sub>
- [Quiz: 3 GitOps questions](notes/p231-quiz-3-gitops-questions.md) <sub>P231</sub>

</details>

<details>
<summary><b>IT operations &amp; incidents</b> · 6 notes</summary>

- [9 checks before a server goes live](notes/p089-9-checks-before-a-server-goes-live.md) <sub>P89</sub>
- [The first 30 minutes of an outage](notes/p138-the-first-30-minutes-of-an-outage.md) <sub>P138</sub>
- [The incident triage path](notes/p577-the-incident-triage-path.md) <sub>P577</sub>
- [9 steps of a host incident](notes/p580-9-steps-of-a-host-incident.md) <sub>P580</sub>
- [The automation pipeline](notes/p667-the-automation-pipeline.md) <sub>P667</sub>
- [Four automation failures](notes/p669-four-automation-failures.md) <sub>P669</sub>

</details>

<details>
<summary><b>Backup &amp; recovery</b> · 4 notes</summary>

- [Backup and cost control](notes/p617-backup-and-cost-control.md) <sub>P617</sub>
- [The backup verification cheat sheet](notes/p618-the-backup-verification-cheat-sheet.md) <sub>P618</sub>
- [5 backup mistakes](notes/p620-5-backup-mistakes.md) <sub>P620</sub>
- [Quiz: 3 data questions](notes/p621-quiz-3-data-questions-2.md) <sub>P621</sub>

</details>

<details>
<summary><b>Web servers, TLS &amp; HTTP</b> · 4 notes</summary>

- [9 openssl commands for SSL certificate problems](notes/p084-9-openssl-commands-for-ssl-certificate-problems.md) <sub>P84</sub>
- [How a Let's Encrypt certificate is issued and renewed](notes/p123-how-a-lets-encrypt-certificate-is-issued-and-renewed.md) <sub>P123</sub>
- [The TLS handshake, drawn](notes/p303-the-tls-handshake-drawn.md) <sub>P303</sub>
- [HTTP/1.1 vs HTTP/2 vs HTTP/3](notes/p476-http-1-1-vs-http-2-vs-http-3.md) <sub>P476</sub>

</details>

<details>
<summary><b>Storage &amp; infrastructure</b> · 3 notes</summary>

- [Block vs File vs Object storage](notes/p129-block-vs-file-vs-object-storage.md) <sub>P129</sub>
- [Anatomy of an /etc/fstab line](notes/p174-anatomy-of-an-etc-fstab-line.md) <sub>P174</sub>
- [9 LVM commands every RHCSA needs](notes/p175-9-lvm-commands-every-rhcsa-needs.md) <sub>P175</sub>

</details>

<details>
<summary><b>Databases &amp; SQL</b> · 1 notes</summary>

- [A zero-downtime database migration](notes/p168-a-zero-downtime-database-migration.md) <sub>P168</sub>

</details>

<details>
<summary><b>Windows &amp; Active Directory</b> · 1 notes</summary>

- [Active Directory vs Entra ID](notes/p128-active-directory-vs-entra-id.md) <sub>P128</sub>

</details>


## What is in a note

Each file in [`notes/`](notes) is Markdown with a short header:

```yaml
---
id: p72
title: "9 curl commands for debugging websites"
sections: [it]              # it, devsecops, or [it, devsecops]
topic: "Web servers, TLS & HTTP"
tags: [Linux, curl, SysAdmin]
source: "LinkedIn post P72 · Linux series"
---
```

Then the parts: **Quick reference** (commands, checklists, tables), **Explained** (the full post), **In one line** (the short version) and, for script posts, **Script**.

## Folders

```text
notes/     623 notes, one Markdown file each (p072-....md)
scripts/   181 scripts from the posts (156 Python + 25 Bash)
tools/     the converter that turns my LinkedIn post folders into notes for both repos
```

---

Made by **Hosam Hani** ([s0sta](https://github.com/s0sta)) · [s0sta.com](https://s0sta.com) · [LinkedIn](https://www.linkedin.com/in/hosam-hani-abdelati) · Contact: [s0sta.com/#contact](https://s0sta.com/#contact)
