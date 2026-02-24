import hashlib
import logging
from pathlib import Path
#  -----------------
# Logging configuration
#  -----------------
# Ensure log file is created in the same directory
# as this Python script
# All authentication-related activies are logged
# to ensure traceability and security auditing.

LOG_FILE = Path(__file__).resolve().parent / "auth.log"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class User:
    """
    Represents a system user with authentication and access control.
    Encapsulation is strictly enforced to protect sensitive data.
    """
    def __init__(self, username, password, privilege_level):
        """
        Initialize a new User object.

        :param username: Unique identifier for the user
        :param password: Plain-text password (hashed internally)
        :param privilege_level: User privilege (admin/standard/guest)
        """
        self.set_username(username)
        self.__set_password(password)
        self.set_privilege_level(privilege_level)

        self.__login_attempts = 0
        self.__account_status = "active"

    # --------------------------------------------------
    # Private Utility Methods
    # --------------------------------------------------

    def __hash_password(self, password):
        """
        Hashed a password using SHA-256.

        :param password: Plain-text password
        :return: Hashed password
        """
        return hashlib.sha256(password.encode()).hexdigest()

    def __set_password(self, password):
        """
        Validates and securely stores the password.
        Passwords are never stored or exposed in plain text.

        :param password: Plain-text password
        """
        if not isinstance(password, str) or len(password) < 8:
            raise ValueError("Password must be at least 8 characters long.")

        self.__hashed_password = self.__hash_password(password)
        
    # --------------------------------------------------
    # Setter Methods with Input Validation
    # --------------------------------------------------
    def set_username(self, username):
        """
        Sets the username after validation.

        :param username: Username string
        """
        if not isinstance(username, str) or not username.strip():
            raise ValueError("Invalid username.")

        self.__username = username

    def set_privilege_level(self,level):
        """
        Set the privilege level after validation.

        :param level: admin, standard, or guest
        """
        if level not in ("admin", "standard","guest"):
            raise ValueError("Invalid privilege level.")
        self.__privilege_level = level

    # --------------------------------------------------
    # Authentication & Security Logic
    # --------------------------------------------------
    def authenticate(self,password):
        """
        Authenticates a user using a password.
        Locks the account after 3 failed attempts.

        :param password: Password attempt
        :return: True if authentication succeeds, False otherwise
        """
        if self.__account_status =="locked":
            self.log_activity("Login attempt on locked account.")
            return False
        
        if self.__hash_password(password) == self.__hashed_password:
            self.reset_login_attempts()
            self.log_activity("Successful login.")
            return True
        
        # Failed authentication
        self.__login_attempts += 1
        self.log_activity("Failed login attempt.")

        if self.__login_attempts >= 3:
            self.lock_account()
        return False
    
    def lock_account(self):
        """
        Locks the user account.
        """
        self.__account_status = "locked"
        self.log_activity('Account locked after multiple failed logins.')

    def reset_login_attempts(self):
        """
        Resets the failed login counter.
        """
        self.__login_attempts = 0

    # --------------------------------------------------
    # Access Control & Authorization
    # --------------------------------------------------
    def check_privileges(self, required_level):
        """
        Checks if the user has sufficient privileges.

        :param required_level: Required privilege level
        :return: Boolean result
        """
        privilege_hierarchy = {
            "guest": 1,
            "standard": 2,
            "admin": 3
        }
        
        return (
            privilege_hierarchy[self.__privilege_level] >= privilege_hierarchy[required_level]
        )
    
    def escalate_privilege(self, new_level, authorising_user):
        """
        Escalates privileges only when authorised by an admin.

        :param new_level: Target privilege level
        :param authorising_user: Admin user authorising the change
        """
        if (
            authorising_user.check_privileges("admin")
            and new_level in ("admin", "standard", "guest")
        ):
            self.__privilege_level = new_level
            self.log_activity(f"Privilege escalated to {new_level}.")
        else:
            raise PermissionError("Unauthorized privilege escalation attempt.")
    # --------------------------------------------------
    # Logging
    # --------------------------------------------------
    def log_activity(self, message):
        """
        Logs user activity for auditing purposes.

        :param message: Activity description
        """
        logging.info(f"User '{self.__username}': {message}")
    # --------------------------------------------------
    # Safe Data Exposure
    # --------------------------------------------------    
    def display_user_info(self):
        """
        Safely returns non-sensitive user information.
        
        :return: Dictionary of safe user details
        """
        return {
            "username": self.__username,
            "privilege_level": self.__privilege_level,
            "account_status": self.__account_status
        }
    def get_account_status(self):
        """
        Returns the account status

        :return: active or locked
        """
        return self.__account_status
    

    # --------------------------------------------------
# Program Entry Point (Lab Demonstration)
# --------------------------------------------------
if __name__ == "__main__":

    # Create users with different privilege levels
    admin = User("admin_user", "AdminPass123", "admin")
    standard = User("standard_user", "StandardPass123", "standard")
    guest = User("guest_user", "GuestPass123", "guest")

    # Successful login
    print(admin.authenticate("AdminPass123"))   # True

    # Failed login attempts (locks account)
    print(guest.authenticate("wrongpass"))      # False
    print(guest.authenticate("wrongpass"))      # False
    print(guest.authenticate("wrongpass"))      # False

    # Attempt login after lock
    print(guest.authenticate("GuestPass123"))   # False

    # Unauthorized privilege escalation
    try:
        guest.escalate_privilege("admin", guest)
    except PermissionError as e:
        print(e)

    # Authorized privilege escalation
    standard.escalate_privilege("admin", admin)

    # Safe display of user info
    print(admin.display_user_info())
    print(standard.display_user_info())
    print(guest.display_user_info())