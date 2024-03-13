import numpy as np
import pandas as pd

def sigmoid(x, start_val, end_val, k, x0):
    """
    Calculate the sigmoid function value for a given input x.

    Args:
        x (float or np.ndarray): Input value(s) for the sigmoid function.
        start_val (float): Starting value of the sigmoid function.
        end_val (float): Ending value of the sigmoid function.
        k (float): Steepness factor of the sigmoid function.
        x0 (float): Midpoint value of the sigmoid function.

    Returns:
        float or np.ndarray: Sigmoid function value(s) corresponding to the input x.
    """
    y = start_val + (end_val - start_val) / (1 + np.exp(-k * (x - x0)))
    return y

def calculate_costs(daily_tickets, days, ai_ticket_cost_base, ai_ticket_cost_success, agent_ticket_cost, start_deflection, end_deflection, target_time, discount=0.2):
    """
    Calculate the costs for handling tickets over the given number of days.

    Args:
        daily_tickets (int or list): Daily ticket volumes. If an integer, the same value is used for all days.
        days (int): Number of days to simulate.
        ai_ticket_cost_base (float): Cost per AI-handled (touched) ticket.
        ai_ticket_cost_success (float): Additional cost for AI-resolved tickets.
        agent_ticket_cost (float): Cost per agent-handled ticket.
        start_deflection (float): Initial deflection rate (percentage of tickets AI can handle).
        end_deflection (float): Target deflection rate.
        target_time (int): Number of days to reach the target deflection rate.
        discount (float, optional): Discount rate for purchases larger than $36k. Defaults to 0.2.

    Returns:
        pd.DataFrame: DataFrame containing the simulation results, including costs and ticket handling metrics.
    """
    x0 = target_time / 2  # Midpoint for sigmoid, assuming symmetry
    k = 4 / target_time  # Adjust 'k' to reach ~end_deflection at 'target_time'

    days_arr = np.arange(days)
    deflection_rates = sigmoid(days_arr, start_deflection, end_deflection, k, x0)

    if isinstance(daily_tickets, int):
        # Constant ticket volume case
        base_tickets = np.full(days, daily_tickets)
    else:
        # Variable ticket volume case
        base_tickets = np.array(daily_tickets)

    ai_handled = base_tickets * deflection_rates
    ai_resolved = ai_handled  # Assuming all AI-handled tickets are resolved for simplicity
    unsolved_tickets = base_tickets - ai_handled

    ai_cost = (ai_resolved * ai_ticket_cost_success) + ((ai_handled - ai_resolved) * ai_ticket_cost_base)
    agent_cost = unsolved_tickets * agent_ticket_cost
    total_cost = ai_cost + agent_cost

    annual_spend = np.cumsum(total_cost) / days * 365
    total_cost[annual_spend > 36000] *= (1 - discount)  # Applying discount if annual spend exceeds $36,000

    average_ticket_price = total_cost / base_tickets

    data = {
        "Day": days_arr + 1,
        "Deflection Rate": deflection_rates,
        "AI Handled Tickets": ai_handled,
        "AI Resolved Tickets": ai_resolved,
        "Unsolved Tickets": unsolved_tickets,
        "AI Cost": ai_cost,
        "Agent Cost": agent_cost,
        "Total Cost": total_cost,
        "Average Ticket Price": average_ticket_price
    }
    return pd.DataFrame(data)
