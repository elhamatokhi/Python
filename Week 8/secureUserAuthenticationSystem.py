import hashlib
import logging

#  -----------------
# Logging configuration
#  -----------------
# All authentication-related activies are logged
# to ensure traceability and security auditing.

logging.basicConfig(
    filename="auth.log",
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

    def __set_password(self,password):
        """
        Validates and securely stores the password.
        Passwords are never stored or exposed in plain-text.

        :param password: Plain-text password
        """

        if not isinstance(password, str) or len(password) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        
        self.__hash_password = self.__hash_password(password)

    # --------------------------------------------------
    # Setter Methods with Input Validation
    # --------------------------------------------------

    