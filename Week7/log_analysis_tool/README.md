# Log Analysis Tool

A professional web server log analysis utility that parses Apache-style access logs, detects security issues, and generates reports. Uses only the Python standard library.

## Features

- **Log parsing**: Apache Combined format — IP, timestamp, method, URL, status, size, referer, user agent
- **Security analysis**: Failed authentication (POST /login → 401), brute-force detection (repeated failures from same IP), suspicious user agents (sqlmap, nikto, empty/dash)
- **Error capture**: All HTTP 4xx and 5xx responses written to `error_log.txt`
- **Reports**: `security_incidents.txt`, `error_log.txt`; timestamped application log files
- **Robust handling**: Line-by-line reading for large files; malformed lines logged and skipped

## Usage

```bash
# Analyze a log file; reports written to current directory
python3 log_analyzer.py /path/to/access.log

# Specify output directory for reports
python3 log_analyzer.py /path/to/access.log /path/to/output_dir
```

Programmatic use:

```python
from pathlib import Path
from log_analyzer import analyze_log

analyze_log(Path("access.log"), Path("./reports"))
```

## Output Files

| File | Description |
|------|-------------|
| `security_incidents.txt` | Failed auth, brute-force alerts, suspicious user agents |
| `error_log.txt` | All request lines with 4xx/5xx status codes |
| `log_analyzer_YYYYMMDD_HHMMSS.log` | Application log (warnings for security events, errors for parse failures) |

## Tests

```bash
cd log_analysis_tool
python3 -m unittest test_log_analyzer -v
```

## Sample Log Format

Apache Combined (single line per request):

```
192.168.1.100 - - [14/Mar/2024:10:15:23 -0400] "GET /index.html HTTP/1.1" 200 2326 "-" "Mozilla/5.0 ..."
```
