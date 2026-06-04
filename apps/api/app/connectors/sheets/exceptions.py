class SheetsError(Exception):
    """Base exception for Google Sheets connector failures."""


class WorksheetNotFoundError(SheetsError):
    """Raised when a configured worksheet cannot be found."""


class SheetAccessError(SheetsError):
    """Raised when the spreadsheet cannot be accessed."""


class InvalidSheetDataError(SheetsError):
    """Raised when sheet rows cannot be validated or mapped."""
