"""
Log Analysis Tool — Web server log parser and security analyzer.

Parses Apache-style access logs, detects security issues (failed authentication,
brute force, suspicious user agents), captures HTTP errors (4xx/5xx), and
generates security_incidents.txt and error_log.txt reports.
"""

import logging
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterator, Optional

# Apache Combined Log Format: IP - - [date] "method url protocol" status size "referer" "user_agent"
_APACHE_LOG_PATTERN = re.compile(
    r'^(\S+)\s+\S+\s+\S+\s+\[([^\]]+)\]\s+"(\S+)\s+(\S+)\s+(\S+)"\s+(\d+)\s+(\d+|-)\s+"([^"]*)"\s+"([^"]*)"\s*$'
)

# Known attack / scanner user-agent substrings (case-insensitive)
SUSPICIOUS_USER_AGENTS = (
    'sqlmap', 'nikto', 'nmap', 'masscan', 'dirbuster', 'gobuster',
    'wfuzz', 'burp', 'acunetix', 'nessus', 'metasploit', 'havij',
)

# Threshold: same IP with this many failed logins in a time window = brute force
BRUTE_FORCE_FAILURE_THRESHOLD = 3

# URL patterns that may indicate SQL injection attempts (case-insensitive)
SQL_INJECTION_PATTERNS = ('union', 'select', 'drop', 'insert', '--', ';')


def _setup_logging(log_dir: Path) -> logging.Logger:
    """Configure application logger with timestamped file, audit file, and console output."""
    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = log_dir / f"log_analyzer_{timestamp}.log"
    audit_file = log_dir / "analysis_audit.log"

    logger = logging.getLogger('log_analyzer')
    logger.setLevel(logging.DEBUG)
    for h in logger.handlers[:]:
        h.close()
        logger.removeHandler(h)

    fmt = '%(asctime)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(fmt)

    fh = logging.FileHandler(log_file, encoding='utf-8')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    # Fixed-name audit log (overwritten each run) for easy inspection
    audit = logging.FileHandler(audit_file, encoding='utf-8', mode='w')
    audit.setLevel(logging.DEBUG)
    audit.setFormatter(formatter)
    logger.addHandler(audit)

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger


@dataclass
class LogEntry:
    """Single parsed Apache-style access log entry."""

    ip: str
    timestamp_str: str
    method: str
    url: str
    protocol: str
    status: int
    size: int
    referer: str
    user_agent: str
    raw_line: str = ""
    line_number: int = 0

    @property
    def is_error(self) -> bool:
        """True if HTTP status is 4xx or 5xx."""
        return 400 <= self.status < 600

    @property
    def is_failed_login(self) -> bool:
        """True if POST to /login (or /login/) returned 401."""
        return (
            self.method.upper() == 'POST'
            and self.url.rstrip('/').endswith('/login')
            and self.status == 401
        )


def parse_log_line(line: str, line_number: int = 0) -> Optional[LogEntry]:
    """
    Parse a single Apache Combined-style log line into a LogEntry.

    Returns None for blank lines or unparseable lines. Raises no exceptions;
    callers should check return value and log parsing failures.
    """
    line = line.rstrip('\n\r')
    if not line.strip():
        return None

    match = _APACHE_LOG_PATTERN.match(line)
    if not match:
        return None

    ip, timestamp_str, method, url, protocol, status_str, size_str, referer, user_agent = match.groups()
    try:
        status = int(status_str)
    except ValueError:
        return None
    size = 0 if size_str == '-' else int(size_str)

    return LogEntry(
        ip=ip,
        timestamp_str=timestamp_str,
        method=method,
        url=url,
        protocol=protocol or "",
        status=status,
        size=size,
        referer=referer or "",
        user_agent=user_agent or "",
        raw_line=line,
        line_number=line_number,
    )


def is_suspicious_user_agent(user_agent: str) -> bool:
    """Return True if user agent matches known attack/scanner signatures or is empty."""
    if not user_agent or user_agent.strip() == '-':
        return True
    ua_lower = user_agent.lower()
    return any(s in ua_lower for s in SUSPICIOUS_USER_AGENTS)


def has_sql_injection_pattern(url: str) -> bool:
    """Return True if URL contains common SQL injection pattern substrings."""
    if not url:
        return False
    url_lower = url.lower()
    return any(pattern in url_lower for pattern in SQL_INJECTION_PATTERNS)


def read_log_entries(
    log_path: Path,
    logger: logging.Logger,
) -> Iterator[tuple[int, Optional[LogEntry], Optional[str]]]:
    """
    Read log file line-by-line and yield (line_number, entry, error_message).

    entry is None if the line was blank or malformed; error_message is set
    when parsing failed for a non-blank line to provide detailed context.
    """
    path = Path(log_path)
    if not path.is_file():
        logger.error("Log file does not exist or is not a file: %s", path)
        return

    try:
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            for line_number, line in enumerate(f, 1):
                entry = None
                err_msg = None
                try:
                    entry = parse_log_line(line, line_number)
                    if line.strip() and entry is None:
                        err_msg = f"Line {line_number}: format did not match Apache Combined log pattern"
                        logger.warning("%s. Raw line: %s", err_msg, line[:200])
                except Exception as e:
                    err_msg = f"Line {line_number}: parsing error - {e!s}"
                    logger.exception("Parsing error at line %d: %s", line_number, e)
                yield line_number, entry, err_msg
    except OSError as e:
        logger.critical("Cannot read log file %s: %s", path, e)
        raise


def analyze_log(
    log_path: Path,
    output_dir: Path,
    security_incidents_path: Optional[Path] = None,
    error_log_path: Optional[Path] = None,
    logger: Optional[logging.Logger] = None,
) -> tuple[int, int, int]:
    """
    Process a web server log file and generate security and error reports.

    Writes security_incidents.txt and error_log.txt under output_dir (or
    custom paths if provided). Uses line-by-line reading for large files.

    Returns (total_lines, parsed_entries, parse_errors).
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if security_incidents_path is None:
        security_incidents_path = output_dir / "security_incidents.txt"
    if error_log_path is None:
        error_log_path = output_dir / "error_log.txt"
    if logger is None:
        logger = _setup_logging(output_dir)

    # Restrict output paths to output_dir for security (no arbitrary writes)
    security_incidents_path = output_dir / security_incidents_path.name
    error_log_path = output_dir / error_log_path.name

    total_lines = 0
    parsed_count = 0
    parse_errors = 0

    # Traffic statistics (like reference implementation)
    unique_ips: set[str] = set()
    http_methods: Counter = Counter()
    urls: Counter = Counter()
    status_codes: Counter = Counter()

    # Accumulators for reports
    error_entries: list[LogEntry] = []
    security_incidents: list[str] = []
    failed_logins_by_ip: dict[str, list[LogEntry]] = defaultdict(list)
    forbidden_access: list[str] = []
    sql_injection_incidents: list[str] = []

    for line_number, entry, err_msg in read_log_entries(Path(log_path), logger):
        total_lines += 1
        if err_msg:
            parse_errors += 1
        if entry is None:
            continue
        parsed_count += 1

        # Update traffic statistics
        unique_ips.add(entry.ip)
        http_methods[entry.method] += 1
        urls[entry.url] += 1
        status_codes[entry.status] += 1

        # Capture 4xx and 5xx for error_log.txt
        if entry.is_error:
            error_entries.append(entry)

        # Failed authentication
        if entry.is_failed_login:
            failed_logins_by_ip[entry.ip].append(entry)
            security_incidents.append(
                f"[FAILED_AUTH] IP={entry.ip} {entry.timestamp_str} {entry.method} {entry.url} -> {entry.status} | UA: {entry.user_agent!r}"
            )
            logger.warning(
                "Security: failed authentication from %s at line %d",
                entry.ip,
                line_number,
            )

        # Forbidden access (403)
        if entry.status == 403:
            incident = f"Forbidden access attempt: {entry.ip} -> {entry.url}"
            forbidden_access.append(incident)
            security_incidents.append(
                f"[FORBIDDEN] IP={entry.ip} {entry.timestamp_str} {entry.method} {entry.url} -> 403"
            )
            logger.warning("Security: forbidden access %s -> %s", entry.ip, entry.url)

        # Potential SQL injection in URL
        if has_sql_injection_pattern(entry.url):
            incident = f"Potential SQL injection: {entry.ip} -> {entry.url}"
            sql_injection_incidents.append(incident)
            security_incidents.append(
                f"[SQL_INJECTION] IP={entry.ip} {entry.timestamp_str} {entry.method} {entry.url!r}"
            )
            logger.warning("Security: potential SQL injection from %s at line %d: %s", entry.ip, line_number, entry.url[:80])

        # Suspicious user agent
        if is_suspicious_user_agent(entry.user_agent):
            security_incidents.append(
                f"[SUSPICIOUS_UA] IP={entry.ip} {entry.timestamp_str} {entry.method} {entry.url} -> {entry.status} | UA: {entry.user_agent!r}"
            )
            logger.warning(
                "Security: suspicious user agent from %s at line %d: %s",
                entry.ip,
                line_number,
                entry.user_agent[:80] if entry.user_agent else "(empty)",
            )

    # Brute force: same IP with multiple failed logins
    for ip, entries in failed_logins_by_ip.items():
        if len(entries) >= BRUTE_FORCE_FAILURE_THRESHOLD:
            incident = (
                f"Brute force attempt from {ip} - {len(entries)} failed attempts"
            )
            security_incidents.append(f"[BRUTE_FORCE] {incident}")
            logger.warning("Security: possible brute force from IP %s (%d failures)", ip, len(entries))

    # Write summary_report.txt (traffic statistics)
    summary_path = output_dir / "summary_report.txt"
    try:
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write("=" * 70 + "\n")
            f.write("SERVER LOG ANALYSIS SUMMARY\n")
            f.write("=" * 70 + "\n\n")
            f.write("TRAFFIC STATISTICS\n")
            f.write("-" * 70 + "\n")
            f.write(f"Total Requests: {parsed_count}\n")
            f.write(f"Unique Visitors: {len(unique_ips)}\n\n")
            f.write("HTTP Methods:\n")
            for method, count in http_methods.most_common():
                f.write(f"  {method}: {count}\n")
            f.write("\nMost Requested URLs:\n")
            for url, count in urls.most_common(5):
                f.write(f"  {url}: {count} requests\n")
            f.write("\nStatus Code Distribution:\n")
            for status, count in sorted(status_codes.items()):
                f.write(f"  {status}: {count}\n")
            f.write("\n" + "=" * 70 + "\n")
        logger.info("Summary report generated: %s", summary_path)
    except OSError as e:
        logger.critical("Cannot write summary report %s: %s", summary_path, e)
        raise

    # Write error_log.txt (4xx and 5xx)
    try:
        with open(error_log_path, 'w', encoding='utf-8') as f:
            f.write("=" * 70 + "\n")
            f.write("HTTP ERRORS LOG\n")
            f.write("=" * 70 + "\n\n")
            f.write(f"Total Errors: {len(error_entries)}\n\n")
            f.write("-" * 70 + "\n")
            for e in error_entries:
                f.write(f"[{e.timestamp_str}] {e.ip} - {e.method} {e.url} - Status: {e.status}\n")
            f.write("\n" + "=" * 70 + "\n")
            f.write("\nRaw log lines:\n")
            f.write("-" * 70 + "\n")
            for e in error_entries:
                f.write(e.raw_line + "\n")
    except OSError as e:
        logger.critical("Cannot write error log file %s: %s", error_log_path, e)
        raise

    # Write security_incidents.txt with sections (like reference implementation)
    try:
        with open(security_incidents_path, 'w', encoding='utf-8') as f:
            f.write("=" * 70 + "\n")
            f.write("SECURITY INCIDENTS REPORT\n")
            f.write("=" * 70 + "\n\n")
            f.write(f"Total Security Incidents: {len(security_incidents)}\n\n")

            f.write("BRUTE FORCE ATTEMPTS\n")
            f.write("-" * 70 + "\n")
            for ip, entries in failed_logins_by_ip.items():
                if len(entries) >= BRUTE_FORCE_FAILURE_THRESHOLD:
                    f.write(f"IP: {ip} - {len(entries)} failed login attempts\n")
            f.write("\n")

            f.write("FORBIDDEN ACCESS ATTEMPTS\n")
            f.write("-" * 70 + "\n")
            for incident in forbidden_access:
                f.write(f"{incident}\n")
            f.write("\n")

            f.write("POTENTIAL SQL INJECTION\n")
            f.write("-" * 70 + "\n")
            for incident in sql_injection_incidents:
                f.write(f"{incident}\n")
            f.write("\n")

            f.write("ALL SECURITY INCIDENTS\n")
            f.write("-" * 70 + "\n")
            for line in security_incidents:
                f.write(f"{line}\n")
            f.write("\n" + "=" * 70 + "\n")
        logger.info("Security report generated: %s", security_incidents_path)
    except OSError as e:
        logger.critical("Cannot write security incidents file %s: %s", security_incidents_path, e)
        raise

    logger.info(
        "Analysis complete: %d lines, %d parsed, %d parse errors. "
        "Errors: %d, Security incidents: %d",
        total_lines,
        parsed_count,
        parse_errors,
        len(error_entries),
        len(security_incidents),
    )
    return total_lines, parsed_count, parse_errors


def main() -> None:
    """CLI entry point: analyze a log file and write reports to current directory."""
    import sys

    logging.getLogger('log_analyzer').handlers.clear()
    logger = _setup_logging(Path.cwd())

    if len(sys.argv) < 2:
        logger.error("Usage: python log_analyzer.py <path_to_access.log> [output_dir]")
        sys.exit(1)

    log_file = Path(sys.argv[1])
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path.cwd()

    if not log_file.is_file():
        logger.critical("Log file not found: %s", log_file)
        sys.exit(2)

    try:
        analyze_log(log_file, output_dir, logger=logger)
    except Exception as e:
        logger.exception("Analysis failed: %s", e)
        sys.exit(3)


if __name__ == '__main__':
    main()
