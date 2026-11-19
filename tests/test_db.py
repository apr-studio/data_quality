import unittest
from unittest.mock import patch

import db


class DatabaseConfigTests(unittest.TestCase):
    def test_accepts_complete_database_config(self):
        with patch.object(db, "DB_PASSWORD", "secret"):
            db.validate_db_config()

    def test_rejects_missing_database_config(self):
        with patch.object(db, "DB_HOST", ""):
            with self.assertRaises(db.DatabaseConfigurationError) as context:
                db.validate_db_config()

        self.assertIn("DB_HOST", str(context.exception))

    def test_rejects_invalid_database_port(self):
        with patch.object(db, "DB_PASSWORD", "secret"):
            with patch.object(db, "DB_PORT", 70000):
                with self.assertRaises(db.DatabaseConfigurationError) as context:
                    db.validate_db_config()

        self.assertIn("DB_PORT", str(context.exception))

    def test_rejects_missing_password_before_connecting(self):
        with patch.object(db, "DB_PASSWORD", ""):
            with self.assertRaises(db.DatabaseConfigurationError):
                db.get_connection()

    def test_passes_valid_config_to_psycopg(self):
        connection = object()

        with patch.object(db, "DB_PASSWORD", "secret"):
            with patch("db.psycopg.connect") as mock_connect:
                mock_connect.return_value = connection
                result = db.get_connection()

        self.assertIs(result, connection)
        mock_connect.assert_called_once_with(
            host=db.DB_HOST,
            port=db.DB_PORT,
            dbname=db.DB_NAME,
            user=db.DB_USER,
            password="secret",
        )


if __name__ == "__main__":
    unittest.main()
