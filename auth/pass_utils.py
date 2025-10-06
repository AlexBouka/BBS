import bcrypt


class PasswordUtils:
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hashes a given password using bcrypt.

        :param password: The password to hash
        :type password: str
        :return: The hashed password
        :rtype: str
        """
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verifies a given plaintext password against a hashed password.

        :param plain_password: The plaintext password to verify
        :type plain_password: str
        :param hashed_password: The hashed password to verify against
        :type hashed_password: str
        :return: Whether the plaintext password matches the hashed password
        :rtype: bool
        """
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"))


pwd_utils = PasswordUtils()
