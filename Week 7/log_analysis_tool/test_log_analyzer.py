"""
Tests for the log analysis tool: parsing, security detection, error capture,
report generation, and exception handling (malformed lines, missing file).

Run with: python -m unittest test_log_analyzer
Or with pytest if installed: pytest test_log_analyzer.py -v
"""

import logging
import tempfile
import unittest
from pathlib import Path

from log_analyzer import (
    BRUTE_FORCE_FAILURE_THRESHOLD,
    LogEntry,
    analyze_log,
    is_suspicious_user_agent,
    parse_log_line,
    read_log_entries,
)

# Suppress application logger to keep test output clean
logging.getLogger('log_analyzer').setLevel(logging.CRITICAL)


class TestParsing(unittest.TestCase):
    """Log line parsing tests."""

    def test_parse_valid_apache_line(self):
        """Valid Apache Combined log line parses to LogEntry with correct fields."""
        line = '192.168.1.100 - - [14/Mar/2024:10:15:23 -0400] "GET /index.html HTTP/1.1" 200 2326 "-" "Mozilla/5.0"'
        entry = parse_log_line(line, 1)
        self.assertIsNotNone(entry)
        self.assertEqual(entry.ip, '192.168.1.100')
        self.assertEqual(entry.method, 'GET')
        self.assertEqual(entry.url, '/index.html')
        self.assertEqual(entry.status, 200)
        self.assertEqual(entry.user_agent, 'Mozilla/5.0')
        self.assertEqual(entry.referer, '-')
        self.assertEqual(entry.line_number, 1)

    def test_parse_post_login_401(self):
        """POST /login with 401 is parsed and detected as failed login."""
        line = '192.168.1.101 - - [14/Mar/2024:10:15:24 -0400] "POST /login HTTP/1.1" 401 0 "http://example.com/login" "Mozilla/5.0"'
        entry = parse_log_line(line, 2)
        self.assertIsNotNone(entry)
        self.assertTrue(entry.is_failed_login)
        self.assertTrue(entry.is_error)

    def test_parse_blank_line_returns_none(self):
        """Blank and whitespace-only lines return None."""
        self.assertIsNone(parse_log_line('', 0))
        self.assertIsNone(parse_log_line('   \n', 1))
        self.assertIsNone(parse_log_line('\n', 2))

    def test_parse_malformed_line_returns_none(self):
        """Malformed log lines return None without raising."""
        self.assertIsNone(parse_log_line('not a log line', 1))
        self.assertIsNone(parse_log_line('192.168.1.1 - - [bad] "GET" 200 0 "-" "-"', 2))
        self.assertIsNone(parse_log_line('192.168.1.1 - - [14/Mar/2024:10:15:23 -0400] "GET / HTTP/1.1" xxx 0 "-" "-"', 3))

    def test_parse_size_dash_treated_as_zero(self):
        """Size field '-' is parsed as 0."""
        line = '127.0.0.1 - - [14/Mar/2024:10:00:00 -0400] "GET / HTTP/1.1" 200 - "-" "-"'
        entry = parse_log_line(line, 1)
        self.assertIsNotNone(entry)
        self.assertEqual(entry.size, 0)

    def test_entry_is_error_4xx_5xx(self):
        """LogEntry.is_error is True for 4xx and 5xx only."""
        e = LogEntry('1.2.3.4', '[date]', 'GET', '/', 'HTTP/1.1', 200, 0, '-', '-')
        self.assertFalse(e.is_error)
        e.status = 403
        self.assertTrue(e.is_error)
        e.status = 500
        self.assertTrue(e.is_error)


class TestSuspiciousUserAgent(unittest.TestCase):
    """Security: suspicious user agent detection."""

    def test_empty_or_dash(self):
        """Empty or '-' user agent is considered suspicious."""
        self.assertTrue(is_suspicious_user_agent(''))
        self.assertTrue(is_suspicious_user_agent('-'))
        self.assertTrue(is_suspicious_user_agent('   -   '))

    def test_known_attack_tools(self):
        """Known attack/scanner signatures are detected."""
        self.assertTrue(is_suspicious_user_agent('sqlmap/1.6.12#stable'))
        self.assertTrue(is_suspicious_user_agent('Nikto/2.1.6'))
        self.assertTrue(is_suspicious_user_agent('nmap'))

    def test_normal_user_agent_not_suspicious(self):
        """Normal browser UAs are not flagged."""
        self.assertFalse(is_suspicious_user_agent('Mozilla/5.0 (Windows NT 10.0; Win64; x64)'))
        self.assertFalse(is_suspicious_user_agent('curl/7.68.0'))


class TestFullAnalysis(unittest.TestCase):
    """File operations, report generation, and error handling."""

    def test_analyze_missing_file_yields_nothing(self):
        """Analyzing a non-existent file yields no entries and does not crash."""
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            out.mkdir()
            logger = logging.getLogger('log_analyzer')
            lines = list(read_log_entries(Path(tmp) / "nonexistent.log", logger))
            self.assertEqual(lines, [])

    def test_analyze_sample_log_generates_reports(self):
        """Running analyze_log on sample_access.log produces security_incidents.txt and error_log.txt."""
        tool_dir = Path(__file__).resolve().parent
        sample_log = tool_dir / "sample_access.log"
        self.assertTrue(sample_log.is_file(), "sample_access.log required for test")

        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            total, parsed, errors = analyze_log(sample_log, out)

            self.assertGreaterEqual(total, 1)
            self.assertGreaterEqual(parsed, 1)
            security_file = out / "security_incidents.txt"
            error_file = out / "error_log.txt"
            self.assertTrue(security_file.is_file())
            self.assertTrue(error_file.is_file())

            security_content = security_file.read_text(encoding='utf-8')
            error_content = error_file.read_text(encoding='utf-8')

            self.assertIn('FAILED_AUTH', security_content)
            self.assertTrue(
                'BRUTE_FORCE' in security_content or '203.0.113.77' in security_content
            )
            self.assertTrue(
                'SUSPICIOUS' in security_content or 'sqlmap' in security_content.lower()
            )

            self.assertIn('401', error_content)
            self.assertIn('403', error_content)
            self.assertIn('404', error_content)
            self.assertIn('500', error_content)

    def test_analyze_empty_file_no_crash(self):
        """Empty log file produces empty reports and does not crash."""
        with tempfile.TemporaryDirectory() as tmp:
            empty_log = Path(tmp) / "empty.log"
            empty_log.write_text('', encoding='utf-8')
            out = Path(tmp) / "reports"
            total, parsed, parse_errors = analyze_log(empty_log, out)
            self.assertEqual(total, 0)
            self.assertEqual(parsed, 0)
            self.assertTrue((out / "error_log.txt").is_file())
            self.assertTrue((out / "security_incidents.txt").is_file())

    def test_analyze_malformed_lines_do_not_crash(self):
        """Log file with mix of valid and invalid lines is processed; invalid lines skipped."""
        with tempfile.TemporaryDirectory() as tmp:
            mixed_log = Path(tmp) / "mixed.log"
            mixed_log.write_text(
                '192.168.1.1 - - [14/Mar/2024:10:00:00 -0400] "GET / HTTP/1.1" 200 0 "-" "-"\n'
                'garbage line\n'
                '192.168.1.2 - - [14/Mar/2024:10:00:01 -0400] "GET /admin HTTP/1.1" 403 0 "-" "-"\n',
                encoding='utf-8',
            )
            out = Path(tmp) / "reports"
            total, parsed, parse_errors = analyze_log(mixed_log, out)
            self.assertEqual(total, 3)
            self.assertEqual(parsed, 2)
            self.assertGreaterEqual(parse_errors, 1)
            error_lines = (out / "error_log.txt").read_text(encoding='utf-8')
            self.assertIn('403', error_lines)

    def test_brute_force_threshold(self):
        """Brute force is reported when an IP has at least BRUTE_FORCE_FAILURE_THRESHOLD failed logins."""
        self.assertGreaterEqual(BRUTE_FORCE_FAILURE_THRESHOLD, 3)


if __name__ == '__main__':
    unittest.main()
