/* s0sta notes: find the tech things in a note (ports, protocols, cloud services, standards, Kubernetes objects,
 * DNS record types, HTTP status codes, Windows event IDs, MITRE ATT&CK IDs, CVE IDs, file paths).
 * Used by the notes search: port:443  proto:tls  svc:s3  std:owasp  k8s:networkpolicy  dns:cname  http:503
 * event:4625  mitre:t1059  cve:2021-44228  path:/etc/ssh  and tech: for any of them.
 * Plain browser JavaScript (ES5), no libraries. Also runs in Node for the tests (module.exports).
 */
var NOTES_TECH = (function () {
  "use strict";

  /* ---------------------------------------------------------------- the kinds, in the order the filter panel shows them */
  var KINDS = [
    ["port", "Ports"], ["proto", "Protocols"], ["svc", "Cloud services"], ["k8s", "Kubernetes"], ["std", "Standards"],
    ["dns", "DNS records"], ["http", "HTTP status"], ["event", "Windows events"], ["mitre", "MITRE ATT&CK"], ["cve", "CVE"], ["path", "Paths"]
  ];

  /* ---------------------------------------------------------------- well-known ports (number -> name) */
  var PORTS = {
    20: "FTP data", 21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS", 67: "DHCP", 68: "DHCP", 69: "TFTP", 80: "HTTP", 88: "Kerberos",
    110: "POP3", 111: "RPC", 123: "NTP", 135: "MS RPC", 137: "NetBIOS", 138: "NetBIOS", 139: "NetBIOS", 143: "IMAP", 161: "SNMP", 162: "SNMP trap",
    179: "BGP", 389: "LDAP", 443: "HTTPS", 445: "SMB", 465: "SMTPS", 500: "IKE", 514: "Syslog", 587: "SMTP submit", 636: "LDAPS",
    853: "DNS over TLS", 873: "rsync", 989: "FTPS", 990: "FTPS", 993: "IMAPS", 995: "POP3S", 1080: "SOCKS", 1194: "OpenVPN", 1433: "SQL Server",
    1521: "Oracle", 1812: "RADIUS", 2049: "NFS", 2375: "Docker API", 2376: "Docker TLS", 2379: "etcd", 2380: "etcd peer", 3000: "Grafana / dev",
    3128: "Squid", 3268: "Global Catalog", 3306: "MySQL", 3389: "RDP", 4317: "OTLP gRPC", 4318: "OTLP HTTP", 4369: "Erlang", 4789: "VXLAN",
    5000: "app / registry", 5044: "Beats", 5432: "PostgreSQL", 5601: "Kibana", 5672: "AMQP", 5900: "VNC", 5985: "WinRM", 5986: "WinRM TLS",
    6379: "Redis", 6443: "Kubernetes API", 6514: "Syslog TLS", 7946: "Swarm", 8000: "HTTP alt", 8080: "HTTP alt", 8200: "Vault",
    8443: "HTTPS alt", 8500: "Consul", 8883: "MQTT TLS", 9000: "app", 9090: "Prometheus", 9092: "Kafka", 9093: "Alertmanager", 9100: "Node exporter",
    9200: "Elasticsearch", 9300: "Elasticsearch", 9418: "Git", 10250: "Kubelet", 10255: "Kubelet read-only", 11211: "Memcached",
    15672: "RabbitMQ UI", 27017: "MongoDB", 51820: "WireGuard"
  };
  var PORT_SVC = {};   // service word -> its usual port (for "SSH on 22" and for tech:ssh)
  "ssh:22 telnet:23 smtp:25 dns:53 http:80 https:443 kerberos:88 ntp:123 snmp:161 bgp:179 ldap:389 smb:445 ldaps:636 rdp:3389 mysql:3306 postgres:5432 postgresql:5432 redis:6379 mongodb:27017 rabbitmq:5672 kafka:9092 prometheus:9090 grafana:3000 vault:8200 etcd:2379 kubelet:10250 winrm:5985 vnc:5900 nfs:2049 imap:143 imaps:993 pop3:110 ftp:21 tftp:69 syslog:514 radius:1812 openvpn:1194 wireguard:51820 elasticsearch:9200 kibana:5601 memcached:11211".split(" ").forEach(function (x) {
    var p = x.split(":"); PORT_SVC[p[0]] = +p[1];
  });

  /* ---------------------------------------------------------------- word lists: [value, label, pattern] */
  function W(list, flags) {
    return list.map(function (x) { return { v: x[0], d: x[1], re: new RegExp(x[2], flags === undefined ? "" : flags) }; });
  }
  var B = "(?:^|[^A-Za-z0-9_-])", E = "(?![A-Za-z0-9_])";
  var PROTOS = W([
    ["tcp", "TCP", B + "TCP" + E], ["udp", "UDP", B + "UDP" + E], ["ip", "IP", B + "IP(?: address| packet| header| layer)"], ["ipv4", "IPv4", B + "IPv4" + E], ["ipv6", "IPv6", B + "IPv6" + E],
    ["icmp", "ICMP", B + "ICMP(?:v6)?" + E], ["arp", "ARP", B + "ARP" + E], ["dhcp", "DHCP", B + "DHCP" + E], ["dns", "DNS", B + "DNS" + E], ["dnssec", "DNSSEC", B + "DNSSEC" + E],
    ["http", "HTTP", B + "HTTP(?!S|/[23])" + E], ["http2", "HTTP/2", B + "HTTP/2" + E], ["http3", "HTTP/3", B + "HTTP/3" + E], ["https", "HTTPS", B + "HTTPS" + E],
    ["tls", "TLS", B + "(?:TLS|SSL)(?: ?v?1\\.[0-3])?" + E], ["mtls", "mTLS", B + "mTLS" + E], ["quic", "QUIC", B + "QUIC" + E], ["websocket", "WebSocket", B + "WebSockets?" + E],
    ["grpc", "gRPC", B + "gRPC" + E], ["ssh", "SSH", B + "SSH" + E], ["sftp", "SFTP", B + "SFTP" + E], ["ftp", "FTP", B + "FTPS?" + E], ["smtp", "SMTP", B + "SMTPS?" + E],
    ["imap", "IMAP", B + "IMAPS?" + E], ["ntp", "NTP", B + "NTP" + E], ["snmp", "SNMP", B + "SNMP" + E], ["ldap", "LDAP", B + "LDAPS?" + E], ["kerberos", "Kerberos", B + "Kerberos" + E],
    ["ntlm", "NTLM", B + "NTLM(?:v2)?" + E], ["rdp", "RDP", B + "RDP" + E], ["smb", "SMB", B + "(?:SMB|CIFS)(?:v[123])?" + E], ["nfs", "NFS", B + "NFS(?:v[34])?" + E],
    ["bgp", "BGP", B + "BGP" + E], ["ospf", "OSPF", B + "OSPF" + E], ["vxlan", "VXLAN", B + "VXLAN" + E], ["vlan", "VLAN", B + "VLANs?" + E], ["nat", "NAT", B + "NAT" + E],
    ["ipsec", "IPsec", B + "IPsec" + E], ["wireguard", "WireGuard", B + "WireGuard" + E], ["vpn", "VPN", B + "VPNs?" + E], ["radius", "RADIUS", B + "RADIUS" + E],
    ["syslog", "Syslog", B + "[Ss]yslog" + E], ["mqtt", "MQTT", B + "MQTT" + E], ["amqp", "AMQP", B + "AMQP" + E], ["iscsi", "iSCSI", B + "iSCSI" + E],
    ["oauth", "OAuth", B + "OAuth ?2?(?:\\.0)?" + E], ["oidc", "OIDC", B + "(?:OIDC|OpenID Connect)" + E], ["saml", "SAML", B + "SAML" + E], ["jwt", "JWT", B + "JWTs?" + E],
    ["cors", "CORS", B + "CORS" + E], ["csp", "CSP", B + "(?:CSP|Content-Security-Policy)" + E], ["hsts", "HSTS", B + "(?:HSTS|Strict-Transport-Security)" + E],
    ["802.1x", "802.1X", B + "802\\.1X" + E], ["stp", "STP", B + "STP" + E], ["lacp", "LACP", B + "LACP" + E], ["ocsp", "OCSP", B + "OCSP" + E], ["acme", "ACME", B + "ACME" + E]
  ]);
  var SVCS = W([
    ["s3", "S3 · AWS", B + "S3" + E], ["ec2", "EC2 · AWS", B + "EC2" + E], ["iam", "IAM", B + "IAM" + E], ["vpc", "VPC", B + "VPCs?" + E], ["cloudtrail", "CloudTrail · AWS", B + "CloudTrail" + E],
    ["cloudwatch", "CloudWatch · AWS", B + "CloudWatch" + E], ["kms", "KMS", B + "KMS" + E], ["lambda", "Lambda · AWS", B + "Lambda" + E], ["eks", "EKS · AWS", B + "EKS" + E],
    ["ecs", "ECS · AWS", B + "ECS" + E], ["ecr", "ECR · AWS", B + "ECR" + E], ["rds", "RDS · AWS", B + "RDS" + E], ["route53", "Route 53 · AWS", B + "Route ?53" + E],
    ["guardduty", "GuardDuty · AWS", B + "GuardDuty" + E], ["securityhub", "Security Hub · AWS", B + "Security Hub" + E], ["aws-config", "AWS Config", B + "AWS Config" + E],
    ["waf", "WAF", B + "WAF" + E], ["cloudfront", "CloudFront · AWS", B + "CloudFront" + E], ["elb", "Load balancer (ELB/ALB/NLB)", B + "(?:ELB|ALB|NLB)" + E],
    ["nat-gateway", "NAT Gateway", B + "NAT [Gg]ateway" + E], ["transit-gateway", "Transit Gateway · AWS", B + "Transit Gateway" + E], ["privatelink", "PrivateLink · AWS", B + "PrivateLink" + E],
    ["secrets-manager", "Secrets Manager · AWS", B + "Secrets Manager" + E], ["ssm", "Systems Manager (SSM) · AWS", B + "(?:SSM|Systems Manager|Parameter Store)" + E],
    ["sts", "STS · AWS", B + "STS" + E], ["organizations", "Organizations / SCP · AWS", B + "(?:AWS Organizations|SCPs?|service control polic)"], ["dynamodb", "DynamoDB · AWS", B + "DynamoDB" + E],
    ["sqs", "SQS · AWS", B + "SQS" + E], ["sns", "SNS · AWS", B + "SNS" + E], ["inspector", "Inspector · AWS", B + "(?:Amazon |AWS )Inspector" + E], ["macie", "Macie · AWS", B + "Macie" + E],
    ["athena", "Athena · AWS", B + "Athena" + E], ["ebs", "EBS · AWS", B + "EBS" + E], ["efs", "EFS · AWS", B + "EFS" + E], ["flow-logs", "VPC Flow Logs", B + "[Ff]low [Ll]ogs?" + E],
    ["security-group", "Security groups", B + "[Ss]ecurity [Gg]roups?" + E], ["nacl", "Network ACL", B + "(?:NACLs?|[Nn]etwork ACLs?)" + E],
    ["entra", "Entra ID / Azure AD", B + "(?:Entra(?: ID)?|Azure AD|Azure Active Directory)" + E], ["key-vault", "Key Vault · Azure", B + "Key Vault" + E], ["aks", "AKS · Azure", B + "AKS" + E],
    ["nsg", "NSG · Azure", B + "NSGs?" + E], ["azure-policy", "Azure Policy", B + "Azure Policy" + E], ["defender", "Defender for Cloud · Azure", B + "Defender for (?:Cloud|Endpoint)" + E],
    ["sentinel", "Sentinel · Azure", B + "(?:Microsoft |Azure )Sentinel" + E], ["azure-monitor", "Azure Monitor / Log Analytics", B + "(?:Azure Monitor|Log Analytics)" + E],
    ["gke", "GKE · Google Cloud", B + "GKE" + E], ["cloud-run", "Cloud Run · Google Cloud", B + "Cloud Run" + E], ["bigquery", "BigQuery · Google Cloud", B + "BigQuery" + E],
    ["gcs", "Cloud Storage · Google Cloud", B + "(?:GCS|Google Cloud Storage)" + E], ["cloudflare", "Cloudflare", B + "Cloudflare" + E]
  ]);
  var STDS = W([
    ["owasp", "OWASP (Top 10, ASVS)", B + "OWASP" + E], ["cis", "CIS Benchmarks / Controls", B + "CIS" + E], ["nist", "NIST (CSF, 800-53, SSDF)", B + "NIST" + E],
    ["mitre-attack", "MITRE ATT&CK", B + "(?:MITRE|ATT&CK)" + E], ["slsa", "SLSA", B + "SLSA" + E], ["sbom", "SBOM", B + "SBOMs?" + E], ["cyclonedx", "CycloneDX", B + "CycloneDX" + E],
    ["spdx", "SPDX", B + "SPDX" + E], ["cvss", "CVSS", B + "CVSS(?:v?[234](?:\\.\\d)?)?" + E], ["epss", "EPSS", B + "EPSS" + E], ["kev", "CISA KEV", B + "KEV" + E],
    ["cwe", "CWE", B + "CWE" + E], ["iso27001", "ISO 27001", B + "ISO ?27001" + E], ["soc2", "SOC 2", B + "SOC ?2" + E], ["pci-dss", "PCI DSS", B + "PCI(?:[ -]DSS)?" + E],
    ["gdpr", "GDPR", B + "GDPR" + E], ["hipaa", "HIPAA", B + "HIPAA" + E], ["stride", "STRIDE", B + "STRIDE" + E], ["fips", "FIPS", B + "FIPS" + E],
    ["openssf", "OpenSSF Scorecard", B + "(?:OpenSSF|Scorecard)" + E], ["in-toto", "in-toto", B + "in-toto" + E], ["semver", "SemVer", B + "(?:SemVer|semantic version)"],
    ["conventional-commits", "Conventional Commits", B + "Conventional Commits?" + E], ["dora", "DORA metrics", B + "DORA" + E], ["sla-slo", "SLO / SLA / SLI", B + "(?:SLOs?|SLAs?|SLIs?)" + E],
    ["rfc", "RFC", B + "RFC ?\\d{3,4}" + E], ["openapi", "OpenAPI", B + "(?:OpenAPI|Swagger)" + E], ["opentelemetry", "OpenTelemetry", B + "(?:OpenTelemetry|OTel|OTLP)" + E]
  ]);
  var K8S = W([
    ["pod", "Pod", B + "[Pp]ods?" + E], ["deployment", "Deployment", B + "[Dd]eployments?" + E], ["statefulset", "StatefulSet", B + "[Ss]tateful[Ss]ets?" + E],
    ["daemonset", "DaemonSet", B + "[Dd]aemon[Ss]ets?" + E], ["replicaset", "ReplicaSet", B + "[Rr]eplica[Ss]ets?" + E], ["job", "Job / CronJob", B + "(?:kind: ?Job|CronJobs?|[Cc]ron[Jj]ob)" + E],
    ["service", "Service (ClusterIP, NodePort, LoadBalancer)", B + "(?:kind: ?Service|ClusterIP|NodePort|LoadBalancer|ExternalName|[Hh]eadless service)" + E],
    ["ingress", "Ingress", B + "[Ii]ngress(?:es)?" + E], ["gateway-api", "Gateway API / HTTPRoute", B + "(?:Gateway API|HTTPRoute|GatewayClass)" + E],
    ["networkpolicy", "NetworkPolicy", B + "(?:NetworkPolic(?:y|ies)|[Nn]etwork [Pp]olic(?:y|ies))" + E], ["configmap", "ConfigMap", B + "[Cc]onfig[Mm]aps?" + E],
    ["secret", "Secret", B + "(?:kind: ?Secret|Kubernetes [Ss]ecrets?|[Ss]ecret/)" ], ["pvc", "PersistentVolume / PVC", B + "(?:PersistentVolume(?:Claim)?s?|PVCs?|PVs?)" + E],
    ["storageclass", "StorageClass", B + "[Ss]torage[Cc]lass(?:es)?" + E], ["serviceaccount", "ServiceAccount", B + "[Ss]ervice[Aa]ccounts?" + E],
    ["rbac", "RBAC (Role, ClusterRole, RoleBinding)", B + "(?:RBAC|ClusterRole(?:Binding)?s?|RoleBindings?|kind: ?Role)" + E], ["hpa", "HPA (autoscaling)", B + "(?:HPA|HorizontalPodAutoscaler)" + E],
    ["pdb", "PodDisruptionBudget", B + "(?:PDB|PodDisruptionBudget)s?" + E], ["namespace", "Namespace", B + "[Nn]amespaces?" + E], ["node", "Node", B + "(?:[Nn]odes?|kubelet)" + E],
    ["crd", "CRD", B + "(?:CRDs?|CustomResourceDefinition)" + E], ["probe", "Probes (liveness, readiness)", B + "(?:liveness|readiness|startup)(?:Probe| probe)" + E],
    ["securitycontext", "securityContext / Pod Security", B + "(?:securityContext|Pod Security(?: Admission| Standards)?|runAsNonRoot|privileged: ?true)" + E],
    ["cni", "CNI", B + "CNI" + E], ["coredns", "CoreDNS", B + "CoreDNS" + E], ["etcd", "etcd", B + "etcd" + E], ["kube-proxy", "kube-proxy", B + "kube-proxy" + E]
  ]);
  var DNSTYPES = ["A", "AAAA", "CNAME", "MX", "TXT", "NS", "SOA", "PTR", "SRV", "CAA", "DNSKEY", "DS", "NAPTR"];
  var HTTPCODES = { 100: "Continue", 101: "Switching Protocols", 200: "OK", 201: "Created", 202: "Accepted", 204: "No Content", 206: "Partial Content",
    301: "Moved Permanently", 302: "Found", 303: "See Other", 304: "Not Modified", 307: "Temporary Redirect", 308: "Permanent Redirect",
    400: "Bad Request", 401: "Unauthorized", 403: "Forbidden", 404: "Not Found", 405: "Method Not Allowed", 408: "Request Timeout", 409: "Conflict",
    410: "Gone", 413: "Payload Too Large", 415: "Unsupported Media Type", 418: "I'm a teapot", 421: "Misdirected Request", 422: "Unprocessable", 425: "Too Early",
    426: "Upgrade Required", 429: "Too Many Requests", 431: "Headers Too Large", 451: "Unavailable For Legal Reasons", 499: "Client Closed (nginx)",
    500: "Internal Server Error", 501: "Not Implemented", 502: "Bad Gateway", 503: "Service Unavailable", 504: "Gateway Timeout", 505: "HTTP Version Not Supported" };
  var EVENTS = { 1102: "Audit log cleared", 4104: "PowerShell script block", 4624: "Logon", 4625: "Failed logon", 4634: "Logoff", 4647: "User logoff",
    4648: "Logon with explicit credentials", 4657: "Registry value changed", 4663: "Object access", 4672: "Admin logon (special privileges)",
    4688: "Process created", 4697: "Service installed", 4698: "Scheduled task created", 4719: "Audit policy changed", 4720: "User created",
    4722: "User enabled", 4723: "Password change", 4724: "Password reset", 4725: "User disabled", 4726: "User deleted", 4728: "Added to global group",
    4732: "Added to local group", 4738: "User changed", 4740: "Account locked out", 4756: "Added to universal group", 4767: "Account unlocked",
    4768: "Kerberos TGT", 4769: "Kerberos service ticket", 4771: "Kerberos pre-auth failed", 4776: "NTLM credential check", 5140: "Share accessed",
    5145: "Share object checked", 5156: "Connection allowed (WFP)", 7036: "Service state changed", 7040: "Service start type changed", 7045: "Service installed" };

  /* ---------------------------------------------------------------- helpers */
  function okPort(p) { p = +p; return p >= 1 && p <= 65535; }
  function each(re, s, fn) { re.lastIndex = 0; var m; while ((m = re.exec(s))) { fn(m); if (!m[0]) re.lastIndex++; } }

  var RE = {
    portWord: /\bports?\s+(?:number\s+)?(?:below\s+|above\s+|like\s+)?(\d{1,5})((?:\s*(?:,|and|or|\/|to|like)\s*\d{1,5})*)/gi,
    l4: /\b(?:TCP|UDP|tcp|udp)\s+(?:port\s+)?(\d{1,5})\b/g,
    onKnown: /\b(?:on|to|open|opens|block|blocks|allow|allows|reach|reaches)\s+(?:port\s+)?(\d{2,5})(?![\d.%:\w])/g,
    unit: /^\s*(?:%|percent|bytes?|bits?|ms|s\b|sec|seconds?|minutes?|mins?|hours?|days?|weeks?|times|x\b|GB|MB|KB|Gbps|Mbps|lines?|items?|errors?|requests?|users?|hosts?|nodes?|pods?|files?|rows?|jobs?|alerts?|findings?|percent)/i,
    forSvc: /\b(\d{2,5}) (?:for|is|=) (?:HTTPS?|DNS|SSH|SMTP|RDP|LDAPS?|NTP|SNMP|Kerberos|SMB|MySQL|PostgreSQL|Redis)\b/g,
    bareHost: /(?:^|[^\w.\/-])([a-z][\w-]{1,30}):(\d{2,5})(?![\d.:\w])/g,
    slashProto: /(?:^|[^\w.:/-])(\d{1,5})\/(tcp|udp|sctp)\b/gi,
    flagPort: /(?:--?(?:d|s)?port|--to-ports?|--listen|--bind|-port|dport|sport)[ =]+(\d{1,5})(?![\d.])/gi,
    ssEq: /\b[ds]port\s*(?:=|eq|==)\s*:?(\d{1,5})\b/gi,
    listen: /\b(?:EXPOSE|[Ll]isten)\s+(?:\[?[\w.:]*\]?:)?(\d{1,5})\b/g,
    yamlPort: /\b(?:containerPort|targetPort|hostPort|nodePort|servicePort|port|Port|PORT|listen_port|http_port)\s*[:=]\s*["']?(\d{1,5})\b/g,
    hostPort: /(?:\blocalhost|\b127\.0\.0\.1|\b0\.0\.0\.0|\[::1?\]|\*|\b(?:\d{1,3}\.){3}\d{1,3}|\b[a-z0-9][a-z0-9-]*(?:\.[a-z0-9-]+)*\.(?:com|net|org|io|local|internal|test|example|svc|cluster\.local|lan|corp|dev|app|cloud))(?::)(\d{2,5})(?![\d.:])/gi,
    mapping: /(?:\s-p\s+|\s--publish\s+|port-forward\s+\S+\s+)(?:[\d.]+:)?(\d{2,5}):(\d{2,5})\b/g,
    sshP: /\b(?:ssh|scp|sftp|mosh)\b[^\n|;]*?\s-[pP]\s*(\d{2,5})\b/g,
    ncPort: /\b(?:nc|ncat|netcat|telnet)\b(?:\s+-\w+)*\s+\S+\s+(\d{1,5})\b/g,
    nmapP: /\b(?:nmap|masscan|naabu|rustscan)\b[^\n|;]*?\s-p\s*([\d,-]+)/g,
    ufw: /\bufw\s+(?:allow|deny|reject|limit)\s+(?:in\s+|out\s+)?(?:proto\s+\w+\s+)?(?:from\s+\S+\s+)?(?:to\s+\S+\s+)?(?:port\s+)?(\d{1,5})\b/g,
    svcPort: /\b(SSH|SMTP|DNS|HTTPS?|RDP|SMB|LDAPS?|MySQL|PostgreSQL|Postgres|Redis|MongoDB|Kafka|NTP|SNMP|WinRM|VNC|Telnet|FTP|IMAPS?|etcd|kubelet|Vault|Prometheus|Grafana|Elasticsearch|Kibana|RabbitMQ|NFS)\b(?:\s+(?:on|at|uses|over|is))?\s*\(?(?:port\s+|:)?(\d{2,5})\)?/g,
    cve: /\bCVE-(\d{4})-(\d{4,7})\b/gi,
    mitre: /\b(T1\d{3}(?:\.\d{3})?)\b/g,
    eventId: /\b(?:event\s*(?:id|ID|Id)|EventID|EventCode|Event ID|evt)\s*[:=]?\s*(\d{3,5})\b/g,
    httpCtx: /\b(?:HTTP(?:\/[\d.]+)?|[Ss]tatus(?: code)?|returns?|returned|got|answers?(?: with)?|responds? with|code)\s*:?\s*([1-5]\d\d)\b/g,
    httpName: /\b([1-5]\d\d)\s+(?:OK|Created|Accepted|No Content|Moved|Found|See Other|Not Modified|Temporary Redirect|Permanent Redirect|Bad Request|Unauthorized|Forbidden|Not Found|Method Not Allowed|Conflict|Gone|Too Many Requests|Internal Server Error|Bad Gateway|Service Unavailable|Gateway Timeout)\b/g,
    httpPlain: /(?:^|[\s(])([45]\d\d)s?(?=[\s,.;)]|$)/g,
    path: /(?:^|[\s"'`(=:,])((?:\/(?:etc|var|proc|sys|usr|opt|home|root|tmp|run|dev|boot|srv|lib|lib64|mnt|media|bin|sbin)(?:\/[\w.@+%:-]*[\w*{}])+\/?)|~\/\.?[\w.-]+(?:\/[\w.@+-]+)*)/g,
    winPath: /\b([A-Z]:\\(?:[\w .$-]+\\)*[\w .$-]+)/g,
    dnsWord: /(?:^|[^\w-])(AAAA|CNAME|MX|TXT|NS|SOA|PTR|SRV|CAA|DNSKEY|DS|NAPTR|A)(?: and [A-Z]{1,5})?\s+records?\b/g,
    dnsList: /\b(AAAA|CNAME|MX|TXT|SOA|PTR|SRV|CAA|DNSKEY|NAPTR)\b/g,
    dig: /\b(?:dig|host -t|nslookup -(?:type|q|query)=?)\s*(?:@\S+\s+)?(?:\+\w+\s+)*(?:[\w.-]+\s+)?(a|aaaa|cname|mx|txt|ns|soa|ptr|srv|caa|dnskey|ds|any)\b/gi,
    zoneLine: /^\s*\S+\.?\s+(?:\d+\s+)?IN\s+(A|AAAA|CNAME|MX|TXT|NS|SOA|PTR|SRV|CAA)\b/gm
  };

  /* ---------------------------------------------------------------- find everything in one note
   * text = the prose (Markdown removed), code = the code lines joined, ctx = { topic, tags[], tools[] } */
  function extract(text, code, ctx) {
    ctx = ctx || {};
    var all = text + "\n" + code, out = {}, k;
    KINDS.forEach(function (x) { out[x[0]] = {}; });
    var addPort = function (p) { if (okPort(p)) out.port[String(+p)] = 1; };

    each(RE.portWord, all, function (m) { if (/[-_]$/.test(all.slice(Math.max(0, m.index - 1), m.index))) return; addPort(m[1]); (m[2] || "").replace(/\d{1,5}/g, function (p) { addPort(p); return p; }); });
    each(RE.slashProto, all, function (m) { addPort(m[1]); });
    var weak = function (m, g) { var p = +m[g]; if (PORTS[p] && p >= 21 && !RE.unit.test(all.slice(m.index + m[0].length, m.index + m[0].length + 12)) && !/MTU|jumbo|frame/i.test(all.slice(Math.max(0, m.index - 30), m.index))) addPort(p); };
    each(RE.l4, all, function (m) { weak(m, 1); });
    each(RE.onKnown, all, function (m) { weak(m, 1); });
    each(RE.forSvc, all, function (m) { if (PORTS[+m[1]]) addPort(m[1]); });
    each(RE.bareHost, all, function (m) { if (PORTS[+m[2]] && !/^(?:https?|ftp|ssh|node|python|nginx|redis|postgres|mysql|alpine|ubuntu|debian|golang|image|tag|v)$/i.test(m[1])) addPort(m[2]); });
    each(RE.flagPort, all, function (m) { addPort(m[1]); });
    each(RE.ssEq, all, function (m) { addPort(m[1]); });
    each(RE.listen, all, function (m) { addPort(m[1]); });
    each(RE.yamlPort, code, function (m) { addPort(m[1]); });
    each(RE.hostPort, all, function (m) { addPort(m[1]); });
    each(RE.mapping, code, function (m) { addPort(m[1]); addPort(m[2]); });
    each(RE.sshP, code, function (m) { addPort(m[1]); });
    each(RE.ncPort, code, function (m) { addPort(m[1]); });
    each(RE.ufw, code, function (m) { addPort(m[1]); });
    if (/\bufw\s+(?:allow|limit)\s+(?:in\s+)?"?OpenSSH/.test(code)) addPort(22);
    if (/\bufw\s+allow\s+(?:in\s+)?"?Nginx (?:Full|HTTPS)/.test(code)) { addPort(443); if (/Nginx Full/.test(code)) addPort(80); }
    each(RE.nmapP, code, function (m) {
      m[1].split(",").forEach(function (p) { if (/^\d+$/.test(p) && p.length <= 5) addPort(p); });
    });
    each(RE.svcPort, all, function (m) {
      var want = PORT_SVC[m[1].toLowerCase()], p = +m[2];
      if (okPort(p) && (want === p || (/port/i.test(m[0]) && PORTS[p]))) addPort(p);
    });

    PROTOS.forEach(function (w) { if (w.re.test(all)) out.proto[w.v] = 1; });
    SVCS.forEach(function (w) { if (w.re.test(all)) out.svc[w.v] = 1; });
    STDS.forEach(function (w) { if (w.re.test(all)) out.std[w.v] = 1; });
    // "Lambda", "Inspector", "Athena" are cloud services only in cloud notes
    var cloud = /cloud|aws|azure|gcp/i.test((ctx.topic || "") + " " + (ctx.tags || []).join(" "));
    ["lambda", "athena", "macie", "sns", "sqs", "waf", "elb", "efs", "ebs", "ecs", "sts"].forEach(function (v) { if (out.svc[v] && !cloud) delete out.svc[v]; });

    var tools = ctx.tools || [], tagstr = (ctx.tags || []).join(" ").toLowerCase(), topic = (ctx.topic || "").toLowerCase();
    var kube = /kubernetes/.test(topic) || /kubernetes|k8s|helm|kubectl/.test(tagstr) || tools.indexOf("kubectl") >= 0 || tools.indexOf("helm") >= 0;
    if (kube) K8S.forEach(function (w) { if (w.re.test(all)) out.k8s[w.v] = 1; });

    var dnsy = /dns/.test(topic + " " + tagstr) || tools.indexOf("dig") >= 0 || tools.indexOf("nslookup") >= 0 || /\bDNS\b/.test(all);
    if (dnsy) {
      each(RE.dnsWord, all, function (m) { out.dns[m[1]] = 1; });
      each(RE.dnsList, all, function (m) { out.dns[m[1]] = 1; });
      each(RE.dig, code, function (m) { var t = m[1].toUpperCase(); if (t !== "ANY") out.dns[t] = 1; });
      each(RE.zoneLine, code, function (m) { out.dns[m[1]] = 1; });
    }

    var webby = /http|api|web|nginx|curl|tls|proxy|cdn|load.?balanc|ingress|status code/i.test(topic + " " + tagstr + " " + tools.join(" ")) || /\bHTTP\b/.test(all);
    var addHttp = function (c) { if (HTTPCODES[c]) out.http[String(c)] = 1; };
    each(RE.httpCtx, all, function (m) { addHttp(+m[1]); });
    each(RE.httpName, all, function (m) { addHttp(+m[1]); });
    if (webby) each(RE.httpPlain, text, function (m) { addHttp(+m[1]); });

    each(RE.cve, all, function (m) { out.cve["cve-" + m[1] + "-" + m[2]] = 1; });
    each(RE.mitre, all, function (m) { out.mitre[m[1].toLowerCase()] = 1; });
    var windowsy = /windows|active directory|powershell|event.?log|siem|sentinel|incident|dfir|soc\b|detection/i.test(topic + " " + tagstr) || /\bEvent ?ID\b|\bwevtutil\b|Get-WinEvent/i.test(all);
    each(RE.eventId, all, function (m) { if (EVENTS[+m[1]] || windowsy) out.event[String(+m[1])] = 1; });
    if (windowsy) Object.keys(EVENTS).forEach(function (id) { if (new RegExp("(?:^|[^\\d.-])" + id + "(?![\\d.])").test(all)) out.event[id] = 1; });

    each(RE.path, all, function (m) {
      var p = m[1].replace(/[.,:;)]+$/, "");
      if (p.length > 2 && p.length < 90 && !/\/\/|\/\.\.$/.test(p) && !/^\/(?:var\/)?tmp\//.test(p) && p !== "/dev/null") out.path[p] = 1;
    });
    each(RE.winPath, all, function (m) { var p = m[1].replace(/[ .]+$/, ""); if (p.length > 3 && p.length < 90) out.path[p] = 1; });

    var res = {};
    for (k in out) res[k] = Object.keys(out[k]);
    return res;
  }

  /* ---------------------------------------------------------------- labels for the filter chips and the suggestions */
  var LABEL = { proto: {}, svc: {}, std: {}, k8s: {} };
  PROTOS.forEach(function (w) { LABEL.proto[w.v] = w.d; });
  SVCS.forEach(function (w) { LABEL.svc[w.v] = w.d; });
  STDS.forEach(function (w) { LABEL.std[w.v] = w.d; });
  K8S.forEach(function (w) { LABEL.k8s[w.v] = w.d; });
  function label(kind, v) {
    if (kind === "port") return v + (PORTS[+v] ? " · " + PORTS[+v] : "");
    if (kind === "http") return v + (HTTPCODES[+v] ? " · " + HTTPCODES[+v] : "");
    if (kind === "event") return v + (EVENTS[+v] ? " · " + EVENTS[+v] : "");
    if (kind === "cve") return v.toUpperCase();
    if (kind === "mitre") return v.toUpperCase();
    if (kind === "dns") return String(v).toUpperCase() + " record";
    return (LABEL[kind] && LABEL[kind][v]) || v;
  }
  /* the words a value is known by (for tech:ssh, port:ssh, proto:https …) */
  function aliases(kind, v) {
    var a = [String(v).toLowerCase()];
    if (kind === "port" && PORTS[+v]) a.push(PORTS[+v].toLowerCase());
    if (kind === "port") for (var s in PORT_SVC) if (PORT_SVC[s] === +v) a.push(s);
    if (kind === "http" && HTTPCODES[+v]) a.push(HTTPCODES[+v].toLowerCase());
    if (kind === "event" && EVENTS[+v]) a.push(EVENTS[+v].toLowerCase());
    if (kind === "cve") a.push(String(v).replace(/^cve-/, ""));
    var l = label(kind, v).toLowerCase(); if (a.indexOf(l) < 0) a.push(l);
    return a;
  }
  /* is note value x a match for what the user wrote (q)? */
  function eq(kind, x, q) {
    q = String(q).toLowerCase().trim();
    if (!q) return true;
    if (kind === "port") {
      var m;
      if ((m = /^(\d+)\s*(?:-|\.\.)\s*(\d+)$/.exec(q))) return +x >= +m[1] && +x <= +m[2];
      if (/^\d+$/.test(q)) return x === String(+q);
      return aliases(kind, x).some(function (a) { return a === q || a.indexOf(q) === 0; });
    }
    if (kind === "http") { if (/^[1-5]xx$/.test(q)) return x[0] === q[0]; if (/^\d+$/.test(q)) return x === q; }
    if (kind === "event" || kind === "cve" || kind === "mitre") { if (/^[\d.-]+$/.test(q) || /^t\d/.test(q) || /^cve-/.test(q)) return String(x).toLowerCase().indexOf(q.replace(/^cve-/, "cve-")) >= 0 || String(x).replace(/^cve-/, "").indexOf(q) === 0; }
    if (kind === "path") return x.toLowerCase().indexOf(q) === 0 || (q.indexOf("/") < 0 && x.toLowerCase().indexOf(q) >= 0);
    return aliases(kind, x).some(function (a) { return a === q || a.indexOf(q) === 0; });
  }
  /* a regex that marks the value in the note (for the yellow highlights) */
  function markRe(kind, v) {
    var esc = function (s) { return String(s).replace(/[.*+?^${}()|[\]\\]/g, "\\$&"); };
    if (kind === "port" || kind === "http" || kind === "event") return "(?:^|[^\\d.])(" + esc(v) + ")(?![\\d.])";
    if (kind === "cve" || kind === "mitre" || kind === "path") return "(" + esc(v) + ")";
    var src = { proto: PROTOS, svc: SVCS, std: STDS, k8s: K8S }[kind];
    if (src) for (var i = 0; i < src.length; i++) if (src[i].v === v) return src[i].re.source.replace(B, "(?:^|[^A-Za-z0-9_-])(") + ")";
    if (kind === "dns") return "(?:^|[^\\w-])(" + esc(v) + ")(?![\\w-])";
    return "";
  }

  return { KINDS: KINDS, PORTS: PORTS, extract: extract, label: label, aliases: aliases, eq: eq, markRe: markRe };
})();
if (typeof module !== "undefined" && module.exports) module.exports = NOTES_TECH;
