"""
Custom Exceptions for GreenPass
"""


class GreenPassException(Exception):
    """Base exception for GreenPass"""
    pass


class GeometryValidationError(GreenPassException):
    """Raised when geometry validation fails"""
    pass


class ExternalAPIError(GreenPassException):
    """Raised when an external API call fails"""
    def __init__(self, service: str, message: str, status_code: int = None):
        self.service = service
        self.status_code = status_code
        super().__init__(f"{service} API Error: {message}")


class DeforestationDetectedError(GreenPassException):
    """Raised when deforestation is detected after cutoff date"""
    def __init__(self, loss_hectares: float, detection_year: int):
        self.loss_hectares = loss_hectares
        self.detection_year = detection_year
        super().__init__(
            f"Deforestation detected: {loss_hectares:.2f} ha in {detection_year}"
        )


class WaterRiskViolationError(GreenPassException):
    """Raised when parcel is in a water veda zone"""
    def __init__(self, aquifer_name: str):
        self.aquifer_name = aquifer_name
        super().__init__(f"Parcel is in water veda zone: {aquifer_name}")


class ProjectNotFoundError(GreenPassException):
    """Raised when a project is not found"""
    pass
