from app.services import scenario_service


def run(scenario: str, company: str = None) -> dict:
    """
    Scenario Simulation Engine agent.
    """
    return scenario_service.simulate_scenario(scenario, company)