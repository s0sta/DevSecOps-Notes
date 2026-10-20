"""Decide if a short string is a command / code, and mark commands inside prose."""
import re

# Tools that are never normal English words
STRONG = set("""
kubectl aws docker docker-compose podman terraform tofu az gcloud curl wget git gh python python3 pip pip3 npm npx node dbt jq yq argocd flux helm
helmfile kustomize kind minikube k9s openssl certbot systemctl journalctl timedatectl hostnamectl localectl loginctl systemd-analyze dig nslookup
nmap ufw apt apt-get apt-cache apt-mark dpkg dnf dnf-automatic yum rpm snap nvidia-smi tar gzip gunzip zstd xz bzip2 unzip zip ansible
ansible-playbook ansible-vault ansible-galaxy ls psql pg_dump pg_restore pg_basebackup pg_ctl pgbench mysql mysqldump mysqladmin mariadb redis-cli
mongosh sqlite3 ss netstat df du grep egrep rg awk sed lsblk blkid findmnt fdisk parted mkfs mkfs.ext4 mkfs.xfs xfs_growfs resize2fs tune2fs fsck
e2fsck mdadm pvcreate pvs pvdisplay vgcreate vgextend vgs vgdisplay lvcreate lvextend lvs lvdisplay lvresize trivy grype syft cosign gitleaks
semgrep checkov tfsec conftest opa kube-bench falco promtool amtool etcdctl crictl ctr nerdctl kubeadm kubelet echo printf ip ip6tables iptables nft
nftables firewall-cmd semanage restorecon chcon getenforce setenforce sestatus getsebool setsebool ausearch aureport audit2why audit2allow
ssh ssh-keygen ssh-copy-id ssh-keyscan sshd scp sftp rsync restic borg rclone tail cat zcat less tcpdump tshark ping ping6 traceroute tracepath
mtr tracert pathping ipconfig netsh nbtstat arp route nmcli netplan resolvectl ethtool whois crontab chmod chown chgrp chattr lsattr getfacl
setfacl umask useradd usermod userdel groupadd groupmod passwd chage visudo sudo su whoami pwd cd mkdir rmdir rm cp mv ln stat lsof strace
ltrace dmesg uname lscpu lsmem lspci lsusb lshw dmidecode vmstat iostat mpstat sar pidstat htop btop ps pgrep pkill killall nice renice nohup
logger logrotate rsyslogd journald shellcheck yamllint hadolint make cmake gcc nginx apachectl httpd php php-fpm composer wp manage-bde DISM dism
sfc chkdsk dcdiag repadmin nltest w32tm dsregcmd gpupdate gpresult powercfg robocopy wmic tasklist taskkill klist setspn bcdedit
kafka-topics kafka-console-consumer kafka-console-producer kafka-consumer-groups kafka-get-offsets kafka-configs feast spark-submit
vault sops age gpg truncate dd shred wc sort uniq cut tr xargs tee head base64 sha256sum md5sum mktemp envsubst export unset alias source
hostname reboot shutdown poweroff vi vim nano tmux screen watch timeout ./deploy.sh molly-guard fail2ban-client sysctl modprobe lsmod
update-grub grub2-mkconfig dracut systemd-resolve hdparm smartctl nvme iotop iftop nload nethogs bpftrace perf
mount umount lastb lastlog nc ncat netcat telnet nx turbo lerna bazel k k3s eksctl aks kubens kubectx stern skaffold tilt
""".split())
# Normal English words that are also commands: only code when an argument follows
WEAK = set("free last top type who kill find host file time test which make sort cut head date id w net watch read set join uptime".split())
SQL_START = re.compile(r"^(SELECT|SHOW|EXPLAIN|CREATE|ALTER|INSERT|UPDATE|DELETE|GRANT|REVOKE|SET|RESET|VACUUM|ANALYZE|REINDEX|CLUSTER|COPY|BEGIN|START|STOP|CHANGE|FLUSH|PURGE|KILL|OPTIMIZE|CHECK|REPAIR|COMMIT|ROLLBACK|WITH|DROP|TRUNCATE|DECLARE|FETCH|LISTEN|NOTIFY|PREPARE|EXECUTE|DO|CALL|REFRESH|LOCK|USE|DESCRIBE)\b")
REDIS = re.compile(r"^(EXISTS|GET|SET|DEL|UNLINK|EXPIRE|TTL|PERSIST|INCR|INCRBY|DECR|MSET|MGET|HSET|HGET|HGETALL|HDEL|HINCRBY|HSCAN|SCAN|KEYS|TYPE|XADD|XLEN|XREAD|XRANGE|LPUSH|RPUSH|LRANGE|SADD|SMEMBERS|ZADD|ZRANGE|INFO|MONITOR|SLOWLOG|CONFIG|CLIENT|PUBLISH|SUBSCRIBE|PING|FLUSHDB|DBSIZE)\b( |$)")
PS_CMDLET = re.compile(r"^[A-Z][a-z]+-[A-Z][A-Za-z]+\b")
STOP = set("the a an to of on in for with and or is are be it every all your you before after from not this that than then if when how what why who".split())


def first_token(s):
    t = s.strip().split()
    if not t:
        return ""
    if t[0] in ("sudo", "time", "watch", "nohup", "env") and len(t) > 1 and t[1] in STRONG:
        return t[1]
    return t[0]


PROSE = {"free tier at least", "terraform plan, read, then apply", "export, then spot-check", "restic and borg encrypt",
         "SELECT * in every query", "COPY . . early in the file", "make test in CI", "kubectl get pods -A -o jsonpath on securityContext"}


def is_code(s, spec_field=True):
    """True when s looks like a command, query or config line (not prose)."""
    s = (s or "").strip()
    if not s or s in PROSE or ", then " in s or re.search(r", (with|and|but|so|without)\b", s):
        return False
    toks = s.split()
    words = [w.strip(",.;:()").lower() for w in toks]
    stops = sum(1 for w in words if w in STOP)
    t0 = first_token(s).rstrip(";,")
    if s.startswith("-") and re.match(r"^--?[A-Za-z]", s):          # flags only: -p 5432:5432
        return True
    if re.match(r"^(FROM|RUN|COPY|ADD|ENV|USER|WORKDIR|EXPOSE|CMD|ENTRYPOINT|ARG|LABEL|HEALTHCHECK|VOLUME|SHELL) \S", s) and stops == 0:
        return True                                                   # Dockerfile line
    if re.match(r"^(for|while|until|if) .*(; *do\b|; *then\b|\]\]?;?)", s) or re.match(r"^[a-z_][a-z0-9_]*=\S", s):
        return True                                                   # shell loop / assignment
    if re.match(r"^[A-Z][a-z]+(?:[A-Z][a-z]+)+ \S+$", s):              # sshd_config: PermitRootLogin no
        return True
    if re.match(r"^[a-z]+(?:\.[a-z_]+)+$", s) or (re.match(r"^[a-z][a-z0-9]*(?:_[a-z0-9]+)+$", s)):
        return True                                                   # pm.max_children, metric_name_total
    if t0 in STRONG:
        if stops == 0 or (re.search(r"\b(on|off);?$", s) and len(toks) <= 4):
            return True
        return stops <= 2 and bool(re.search(r"[-/$|=.'\"]|\d", s)) and not re.search(r"\b(on|for|to) (a|an|the)\b", s)
    if t0.rstrip(";") in WEAK:
        rest = toks[1:]
        if not rest:
            return spec_field            # "top" alone in a command field
        return rest[0].startswith(("-", "/", "~", "$", "'", '"', ".")) or (spec_field and stops == 0)
    if s.startswith(("./", "/", "~/", "$ ", "${", "*/", "UUID=", "\\")) and stops == 0:
        return True
    if re.match(r"^\d+(/\d+)?( [\d*/,-]+){4} \S", s):          # cron line
        return True
    if SQL_START.match(s) and len(toks) >= 2:
        return True
    if re.match(r"^(select|explain|show|create|alter|insert|update|delete|vacuum|analyze)\b", s) and (s.endswith(";") or "from" in words):
        return True
    if REDIS.match(s) and s.upper().split()[0] == toks[0] and stops <= 2:
        return True
    if PS_CMDLET.match(s):
        return True
    if re.match(r"^[a-z_][\w.]*\s+[^\s].*;$", s) and stops == 0:   # nginx / php-fpm directive
        return True
    if re.match(r"^[a-z_][\w.]*\s*=\s*\S", s) and "_" in toks[0] and stops == 0:   # php.ini / config key = value
        return True
    if re.match(r"^[a-z][\w]*:\s*\S", s) and stops == 0 and len(toks) <= 4 and not re.match(r"^\w+://", s):   # yaml key: value
        return True
    if re.search(r"\w\([^)]*\)|\[[0-9]+[smhd]\]|\{[^}]*=~?\"", s) and stops <= 1:   # functions, PromQL
        return True
    return False


def lang_of(s):
    s = s.strip()
    if SQL_START.match(s) or re.match(r"^(select|explain|with)\b", s):
        return "sql"
    if REDIS.match(s):
        return "text"
    if PS_CMDLET.match(s) or first_token(s) in ("ipconfig", "netsh", "sfc", "DISM", "dism", "chkdsk", "dcdiag", "repadmin", "nltest", "w32tm",
                                               "dsregcmd", "gpupdate", "gpresult", "powercfg", "manage-bde", "tracert", "pathping", "robocopy"):
        return "powershell"
    if re.search(r"histogram_quantile|rate\(|increase\(|sum\(rate", s):
        return "promql"
    if s.startswith("\\"):
        return "text"
    return "bash"


# ---------------------------------------------------------------- inline code inside prose
PATH_RE = re.compile(r"(?<![\w/`.])(/(?:etc|var|usr|opt|home|root|tmp|dev|proc|sys|srv|boot|run|mnt|data|app|bin|sbin|lib)(?:/[\w.@*+-]+)*/?)")
VAR_RE = re.compile(r"(?<![\w`$])(\$\{[A-Za-z_][A-Za-z0-9_]*(?::[?-][^}]*)?\}|\$[A-Z_][A-Z0-9_]*\b|\$\?|\$PATH)")
FILE_RE = re.compile(r"(?<![\w/`.-])([\w.-]+\.(?:conf|cfg|yaml|yml|json|py|sh|log|tf|tfstate|tfvars|txt|ini|service|timer|toml|env|pem|crt|key|csr|sql|php|js|xml|md))\b")
# Kubernetes-style labels and apiVersions: pod-security.kubernetes.io/enforce=restricted, backstage.io/v1alpha1, apps/v1
LABEL_RE = re.compile(r"(?<![\w`/.-])((?:[a-z0-9-]+\.)+[a-z]{2,}/[a-z0-9.-]+=[\w.-]+)")
APIVER_RE = re.compile(r"(?<![\w`/.-])((?:[a-z0-9-]+\.)*[a-z0-9-]+/v\d+(?:(?:alpha|beta)\d+)?)(?![\w/])")
GPU_RE = re.compile(r"(?<![\w`/.-])((?:nvidia|amd)\.com/gpu)\b")
LONGFLAG_RE = re.compile(r"(?<![\w`-])(--[a-z][\w-]+(?:=[^\s,;]+)?)")
CRON_LEFT_RE = re.compile(r"((?:(?:\d+(?:[-,/]\d+)*|\*(?:/\d+)?) ){5})$")
FLAG_CMD_RE = None


def _flag_cmd_re():
    global FLAG_CMD_RE
    if FLAG_CMD_RE is None:
        names = sorted((c for c in STRONG | WEAK if re.match(r"^[\w.-]+$", c)), key=len, reverse=True)
        FLAG_CMD_RE = re.compile(r"(?<![\w`/.-])((?:sudo )?(?:" + "|".join(map(re.escape, names)) +
                                 r")(?: (?!(?:with|and|or|the|a|an|to|of|in|on|for|by|from|at|as|is|it|its|then|than|when|if)\b)[a-z][\w-]*(?:\.[a-z][\w-]*)*)?(?: +(?:--?|\+)[A-Za-z][\w-]*(?:=[^\s,;]+)?(?: [A-Z0-9][\w./:@%-]*| [a-z][\w./:@%-]*\.[\w/:@%-]+| [/~$'\"][^\s,;]*)?)+)(?![\w-])")
    return FLAG_CMD_RE


ARG_SPECIAL = re.compile(r"[0-9/.:=+'\"{}<>*|_~$@%&]")
FLAG_TOK = re.compile(r"^(?:--?|\+)[A-Za-z0-9][\w=.,:'\"%|{}/@+*-]*$")
# values that follow a flag: -o yaml, -p tcp, -u nginx, --restart nginx
FLAG_VALUES = set("""tcp udp icmp yaml json wide name jsonpath root prod production staging dev default all kube-system nginx ssh sshd
apache2 httpd docker mysql mysqld mariadb postgresql postgres redis cron crond kubelet containerd fail2ban avc ext4 xfs main master
origin text table csv html""".split())
# words that may sit between a tool and its flags: kubectl auth can-i --list, docker image inspect --format
SUBCMD = set("""auth can-i app sync image inspect logs exec get describe apply delete rollout status restart run compose up down ps
port-forward debug create config list show plan init validate fmt import state workspace install upgrade uninstall template repo add
update search pull push build tag commit log diff reset switch checkout stash rebase merge branch remote fetch clone s3 ec2 iam sts eks
rds cloudwatch describe-instances cp ls seed deps snapshot release history rollback lint scan sbom verify sign attest login logout
policy role secret secrets configmap pod pods svc service deployment deploy node nodes ns namespace topic topics""".split())
ENGLISH_CMD = set("k age source export alias head tail less sort screen make echo route turbo nice logger kind flux feast vault perf watch timeout tee".split())
FSTAB_RE = re.compile(r"(?<![\w`/])((?:UUID=\S+|/dev/\S+)\s+/\S*\s+(?:ext4|xfs|btrfs|vfat|nfs|nfs4|swap|tmpfs)\s+\S+\s+\d\s+\d)\b")


def _absorbable(tok, prev):
    if tok.lower() in STOP or tok.lower() in ("e.g", "i.e", "etc"):
        return False
    if FLAG_TOK.match(tok):
        return True
    if ARG_SPECIAL.search(tok) and not re.match(r"^[A-Z][a-z]+$", tok):
        return True
    if len(tok) == 1 and tok.islower():
        return True
    after_flag = bool(FLAG_TOK.match(prev or "")) and "=" not in (prev or "")
    if after_flag and (tok in FLAG_VALUES or re.match(r"^[a-z][a-z0-9]*-[a-z0-9-]+$", tok)):
        return True
    if re.match(r"^-[A-Za-z]$", prev or "") and tok.isupper() and len(tok) <= 8:
        return True
    return False


def _grow(text, spans):
    """Let a command span take the arguments that follow it, the command words before a bare flag,
    and join spans that only a space separates: kubectl logs <pod> --previous, --group g, -p tcp --dport 443."""
    out = []
    for a, b in spans:
        seg = text[a:b]
        # left: "kubectl auth can-i" + "--list"
        first = seg.split()[0] if seg.split() else ""
        if FLAG_TOK.match(first) or first.startswith(("/", "<", "~/")) or re.match(r"^[\w-]+\.[a-z]{2,4}$", first):
            j, steps = a, 0
            while steps < 4:
                m = re.search(r"(\S+) $", text[:j])
                if not m:
                    break
                tok = m.group(1)
                if tok.lower() in STOP or re.search(r"[.,;:!?)]$", tok) or tok.startswith("`"):
                    break
                if tok in STRONG and tok not in ENGLISH_CMD:
                    a = m.start(1)
                    break
                if not (tok in SUBCMD or re.match(r"^<[\w.-]+>$", tok) or FLAG_TOK.match(tok) or re.match(r"^[\w.-]*[0-9/=:][\w./=:-]*$", tok)):
                    break
                j, steps = m.start(1), steps + 1
        # right: arguments
        prev = text[a:b].split()[-1] if text[a:b].split() else ""
        i = b
        m = re.match(r"(?:,[\w.:=-]*[\w:=-])+", text[b:])     # --format=csv,noheader,nounits (a comma with no space is part of it)
        if m:
            i = b + m.end()
        while True:
            m = re.match(r" (\S+)", text[i:])
            if not m:
                break
            tok = m.group(1)
            core = tok.rstrip(".,;:)")
            if not core or not _absorbable(core, prev):
                break
            i += 1 + len(core)
            prev = core
            if len(core) != len(tok):
                break
        out.append((a, i))
    out.sort()
    merged = []
    for a, b in out:
        if merged and (a <= merged[-1][1] or (text[merged[-1][1]:a] == " " and not text[merged[-1][0]:merged[-1][1]].endswith(";"))):
            merged[-1] = (merged[-1][0], max(b, merged[-1][1]))
        else:
            merged.append((a, b))
    return merged


def mark_inline(text, known):
    """Wrap commands in `backticks`: first the exact commands of this note, then safe patterns."""
    spans = []

    def taken(a, b):
        return any(not (b <= x or a >= y) for x, y in spans)

    for k in sorted(set(known), key=len, reverse=True):
        if len(k) < 3:
            continue
        start = 0
        while True:
            i = text.find(k, start)
            if i < 0:
                break
            j = i + len(k)
            ok_left = i == 0 or not (text[i - 1].isalnum() or text[i - 1] in "_-/$")
            ok_right = j == len(text) or not (text[j].isalnum() or text[j] in "_-/")
            if ok_left and ok_right and not taken(i, j):
                spans.append((i, j))
            start = j
    for rx in (FSTAB_RE, _flag_cmd_re(), LABEL_RE, APIVER_RE, GPU_RE, PATH_RE, VAR_RE, FILE_RE, LONGFLAG_RE):
        for m in rx.finditer(text):
            a, b = m.span(1)
            seg = text[a:b].rstrip(".,;:)")
            b = a + len(seg)
            if len(seg) >= 2 and not taken(a, b):
                spans.append((a, b))
    spans.sort()
    spans = _grow(text, spans)
    # a cron schedule right before a command belongs to it: 0 8 * * * python3 x.py
    for k, (a, b) in enumerate(spans):
        m = CRON_LEFT_RE.search(text[:a])
        if m and (k == 0 or spans[k - 1][1] <= m.start(1)):
            spans[k] = (m.start(1), b)
    out, last = [], 0
    for a, b in spans:
        out.append(("t", text[last:a]))
        out.append(("c", text[a:b]))
        last = b
    out.append(("t", text[last:]))
    return out
