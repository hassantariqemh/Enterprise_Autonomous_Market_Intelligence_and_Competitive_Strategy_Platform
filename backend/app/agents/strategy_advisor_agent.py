from app.services import strategy_advisor_service


def run(company: str) -> dict:
    """
    AI Strategy Advisor agent.
    """
    return strategy_advisor_service.generate_strategy(company)