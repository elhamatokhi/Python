from datetime import datetime, timedelta
from typing import List
import logging
from pathlib import Path

LOG_FILE = Path(__file__).resolve().parent / "deviceLogs.log"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ----------------------------
# User Class
# ----------------------------
class User:
    def __init__(self, username: str, role: str = "standard"):
        if role not in {"standard", "admin"}:
            raise ValueError("Role must be 'standard' or 'admin'")
        self.username = username
        self.role = role

    def is_admin(self) -> bool:
        return self.role == "admin"


# ----------------------------
# Device Class
# ----------------------------
class Device:
    SCAN_VALIDITY_DAYS = 30

    def __init__(
        self,
        device_id: str,
        device_type: str,
        firmware_version: str,
        owner: User,
        compliance_status: bool = False,
        last_security_scan: datetime | None = None,
        is_active: bool = True,
    ):
        if not device_id or not device_type or not firmware_version:
            raise ValueError("Device ID, type, and firmware version are required")

        if not isinstance(owner, User):
            raise ValueError("Owner must be a User object")

        self.device_id = device_id
        self.device_type = device_type
        self.firmware_version = firmware_version
        self.owner = owner
        self.compliance_status = compliance_status
        self.last_security_scan = last_security_scan
        self.is_active = is_active
        self.quarantined = False
        self.logs: List[str] = []

        self._log("Device created")

    # ----------------------------
    # Logging
    # ----------------------------
    def _log(self, action: str):
        timestamp = datetime.utcnow().isoformat()
        msg = f"[{timestamp}] {action}"
        self.logs.append(msg)        # Keep internal logs if needed
        logging.info(msg)            # Also write to deviceLogs.log

    # ----------------------------
    # Compliance & Security
    # ----------------------------
    def run_security_scan(self):
        self.last_security_scan = datetime.utcnow()
        self.compliance_status = True
        self._log("Security scan completed; device marked compliant")

    def update_firmware(self, new_version: str):
        if not new_version:
            raise ValueError("Firmware version cannot be empty")

        self.firmware_version = new_version
        self.compliance_status = False
        self._log(f"Firmware updated to {new_version}; compliance reset")

    def check_compliance(self) -> bool:
        if not self.last_security_scan:
            self.compliance_status = False
            return False

        if datetime.utcnow() - self.last_security_scan > timedelta(days=self.SCAN_VALIDITY_DAYS):
            self.compliance_status = False
            self._log("Compliance expired due to outdated security scan")

        return self.compliance_status

    # ----------------------------
    # Access Control
    # ----------------------------
    def authorise_access(self, user: User, override: bool = False) -> bool:
        if not self.is_active or self.quarantined:
            self._log(f"Access denied to {user.username}: device inactive or quarantined")
            return False

        self.check_compliance()

        if user.is_admin():
            if not self.compliance_status and override:
                self._log(f"Admin override access granted to {user.username}")
                return True
            elif self.compliance_status:
                self._log(f"Admin access granted to {user.username}")
                return True
            else:
                self._log(f"Admin access denied to {user.username}: non-compliant device")
                return False

        if user.username != self.owner.username:
            self._log(f"Access denied to {user.username}: not device owner")
            return False

        if not self.compliance_status:
            self._log(f"Access denied to {user.username}: device non-compliant")
            return False

        self._log(f"Access granted to owner {user.username}")
        return True

    # ----------------------------
    # Quarantine
    # ----------------------------
    def quarantine(self, admin_user: User):
        if not admin_user.is_admin():
            raise PermissionError("Only admin users can quarantine devices")

        self.quarantined = True
        self.is_active = False
        self._log(f"Device quarantined by admin {admin_user.username}")
class DeviceManager:
    def __init__(self):
        self.devices: dict[str, Device] = {}

    def add_device(self, device: Device):
        if device.device_id in self.devices:
            raise ValueError("Device ID already exists")
        self.devices[device.device_id] = device

    def remove_device(self, device_id: str):
        if device_id not in self.devices:
            raise KeyError("Device not found")
        del self.devices[device_id]

    def quarantine_device(self, device_id: str, admin_user: User):
        device = self.devices.get(device_id)
        if not device:
            raise KeyError("Device not found")
        device.quarantine(admin_user)

    def generate_security_report(self) -> dict:
        report = {
            "total_devices": len(self.devices),
            "compliant": 0,
            "non_compliant": 0,
            "quarantined": 0,
        }

        for device in self.devices.values():
            device.check_compliance()
            if device.quarantined:
                report["quarantined"] += 1
            elif device.compliance_status:
                report["compliant"] += 1
            else:
                report["non_compliant"] += 1

        return report
    
admin = User("alice", "admin")
user1 = User("bob", "standard")
user2 = User("eve", "standard")

device = Device(
    device_id="D-1001",
    device_type="Router",
    firmware_version="1.0.0",
    owner=user1
)

manager = DeviceManager()
manager.add_device(device)

# Standard user access
device.run_security_scan()
assert device.authorise_access(user1) is True
assert device.authorise_access(user2) is False

# Firmware update breaks compliance
device.update_firmware("1.1.0")
assert device.authorise_access(user1) is False

# Admin override
assert device.authorise_access(admin, override=True) is True

# Quarantine
manager.quarantine_device("D-1001", admin)
assert device.authorise_access(admin) is False