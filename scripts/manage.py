#!/usr/bin/env python
import os
import sys

import dotenv


def main():
    base_url = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(base_url, 'ea_copy_be')
    if base_url not in sys.path:
        sys.path.append(base_url)
    if path not in sys.path:
        sys.path.append(path)
    dotenv.read_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ea_copy_be.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        )(exc)
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
