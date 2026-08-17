from app.services import swot_service


def run(company: str) -> dict:
    """
    SWOT Intelligence Generator agent.
    """
    return swot_service.generate_swot(company)