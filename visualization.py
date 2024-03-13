import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import streamlit as st

def create_ticket_handling_plot(simulation_data, baseline_data):
    """
    Create a line plot showing the ticket handling over time.

    Args:
        simulation_data (pd.DataFrame): DataFrame containing the simulation results.
        baseline_data (pd.DataFrame): DataFrame containing the baseline data.

    Returns:
        plotly.graph_objs._figure.Figure: Plotly figure object representing the ticket handling plot.
    """
    fig = px.line(simulation_data, x="Day", y=["AI Handled Tickets", "AI Resolved Tickets", "Unsolved Tickets"], title="Ticket Handling Over Time")
    fig.add_trace(go.Scatter(x=baseline_data['Cumulative Day'], y=baseline_data['Total Cases'], mode='lines+markers', name='Baseline Daily Tickets'))
    # Add average lines for the baseline
    fig.add_trace(go.Scatter(x=[baseline_data['Cumulative Day'].min(), baseline_data['Cumulative Day'].max()], y=[baseline_data['Total Cases'].mean()] * 2, mode='lines', name='Average Baseline Tickets', line=dict(color='firebrick', dash='dash')))
    fig.update_layout(hovermode="x unified")
    return fig

def create_costs_plot(simulation_data, baseline_data):
    """
    Create a line plot showing the costs over time.

    Args:
        simulation_data (pd.DataFrame): DataFrame containing the simulation results.
        baseline_data (pd.DataFrame): DataFrame containing the baseline data.

    Returns:
        plotly.graph_objs._figure.Figure: Plotly figure object representing the costs plot.
    """
    fig = px.line(simulation_data, x="Day", y=["AI Cost", "Agent Cost", "Total Cost"], title="Costs Over Time", labels={"value": "Cost ($)", "variable": "Type"})
    # Adding baseline costs for comparison
    fig.add_trace(go.Scatter(x=baseline_data['Cumulative Day'], y=baseline_data['Contact Center COST'], mode='lines+markers', name='Baseline Daily Costs', line=dict(color='firebrick', dash='dot')))
    # Add average lines for the baseline
    fig.add_trace(go.Scatter(x=[baseline_data['Cumulative Day'].min(), baseline_data['Cumulative Day'].max()], y=[baseline_data['Contact Center COST'].mean()] * 2, mode='lines', name='Average Baseline Cost', line=dict(color='firebrick', dash='dash')))
    fig.update_layout(hovermode="x unified")
    return fig

def create_price_per_ticket_plot(simulation_data, baseline_data):
    """
    Create a line plot showing the price per ticket over time.

    Args:
        simulation_data (pd.DataFrame): DataFrame containing the simulation results.
        baseline_data (pd.DataFrame): DataFrame containing the baseline data.

    Returns:
        plotly.graph_objs._figure.Figure: Plotly figure object representing the price per ticket plot.
    """
    if 'Current Price Per Ticket' not in baseline_data.columns:
        baseline_data['Current Price Per Ticket'] = baseline_data['Contact Center COST'] / baseline_data['Total Cases']
    fig = px.line(baseline_data, x="Cumulative Day", y="Current Price Per Ticket", title="Price Per Ticket Over Time", labels={"Day": "Day", "Current Price Per Ticket": "Price ($) Per Ticket"})
    fig.add_trace(go.Scatter(x=simulation_data['Day'], y=simulation_data['Average Ticket Price'], mode='lines+markers', name='Simulated Price Per Ticket', line=dict(color='green', dash='dot')))
    # add an average line for the baseline
    fig.add_trace(go.Scatter(x=[baseline_data['Cumulative Day'].min(), baseline_data['Cumulative Day'].max()], y=[baseline_data['Current Price Per Ticket'].mean()] * 2, mode='lines', name='Average Baseline Price', line=dict(color='firebrick', dash='dash')))
    fig.update_layout(hovermode="x unified")
    return fig


def display_key_metrics(simulation_data, baseline_data):
    """
    Display key metrics comparing the simulation results with the baseline data.

    Args:
        simulation_data (pd.DataFrame): DataFrame containing the simulation results.
        baseline_data (pd.DataFrame): DataFrame containing the baseline data.
    """
    col1, col2, col3 = st.columns(3)

    # Baseline cost
    baseline_total_cost = baseline_data['Contact Center COST'].sum()
    col1.metric("Baseline Cost", f"${baseline_total_cost:,.2f}")

    # Total cost for the simulated period
    total_cost = simulation_data['Total Cost'].sum()
    cost_savings = baseline_total_cost - total_cost
    col1.metric("Total Cost for the Simulated Period", f"${total_cost:,.2f}", f"{-cost_savings:,.2f} ({-100 * cost_savings / baseline_total_cost:.2f}%)", delta_color="inverse")

    # Percentage of tickets handled by AI
    total_tickets = simulation_data['AI Handled Tickets'].sum() + simulation_data['Unsolved Tickets'].sum()
    ai_handled_percentage = (simulation_data['AI Handled Tickets'].sum() / total_tickets) * 100
    col2.metric("Percentage of Tickets Handled by AI", f"{ai_handled_percentage:.2f}%")

    # Average deflection rate
    average_deflection_rate = simulation_data['Deflection Rate'].mean()
    col2.metric("Average Deflection Rate", f"{average_deflection_rate:.2f}")

    # Baseline Price per ticket
    baseline_average_price_per_ticket = (baseline_data['Contact Center COST'] / baseline_data['Total Cases']).mean()
    col3.metric("Baseline Average Price Per Ticket", f"${baseline_average_price_per_ticket:.2f}")

    # Average price per ticket
    average_price_per_ticket = simulation_data['Average Ticket Price'].mean()
    price_per_ticket_change = average_price_per_ticket - baseline_average_price_per_ticket
    col3.metric("Average Price Per Ticket", f"${average_price_per_ticket:.2f}", f"{price_per_ticket_change:.2f} ({100 * price_per_ticket_change / baseline_average_price_per_ticket:.2f}%)", delta_color="inverse")

    st.write("---")
