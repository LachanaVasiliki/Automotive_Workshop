#!/usr/bin/env python
"""Η εντολή για τη διαχείριση του Django μέσω γραμμής εντολών."""

import os
import sys


def main():
    """Εκτελεί τις διαχειριστικές εργασίες του Django."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')  # Ορίζουμε τις ρυθμίσεις του Django
    try:
        from django.core.management import execute_from_command_line  # Εισάγουμε τη συνάρτηση για την εκτέλεση εντολών
    except ImportError as exc:
        raise ImportError(
            "Δεν μπόρεσα να εισάγω το Django. Είσαι σίγουρος ότι είναι εγκατεστημένο και "
            "διαθέσιμο στη μεταβλητή PYTHONPATH; Μήπως ξέχασες να ενεργοποιήσεις το virtual environment;"
        ) from exc
    execute_from_command_line(sys.argv)  # Εκτελεί την εντολή που δίνει ο χρήστης


if __name__ == '__main__':
    main()  # Εκκινεί την κύρια συνάρτηση όταν το script τρέχει απευθείας
