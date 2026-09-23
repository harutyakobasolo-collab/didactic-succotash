class SDETFlowError(Exception):
    """Base exception for framework errors."""


class CaseValidationError(SDETFlowError):
    """Raised when a case file does not match the expected schema."""


class RenderError(SDETFlowError):
    """Raised when a template variable cannot be resolved."""


class ExtractionError(SDETFlowError):
    """Raised when response data cannot be extracted."""


class AssertionFailure(SDETFlowError):
    """Raised when a response assertion fails."""

