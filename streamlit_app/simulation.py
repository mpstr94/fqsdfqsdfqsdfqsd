import streamlit as st
import seaborn as sns
import json
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from dateutil.relativedelta import *
import pandas as pd
from fqsdfqsdfqsdfqsd.simulations import MainSimulation

# SOME CONFIG STUFF
st.set_option('deprecation.showPyplotGlobalUse', False)

def _max_width_():
    max_width_str = f"max-width: 90vw;"
    st.markdown(
        f"""
    <style>
    .reportview-container .main .block-container{{
        {max_width_str}
    }}
    </style>    
    """,
        unsafe_allow_html=True,
    )
_max_width_()

# MAIN TITLE
st.title('Credix simulation')

# SET COLUMNS
col1, col2 = st.columns(2)

# COL 1
config = {
    "underwriters": {
        "amount": 100,
        "USDC_balance": [10000,50000]
    },
    "investors": {
        "amount": 1000,
        "USDC_balance": [4000,5000]
    },
    "deals": [
        {
            "months_after_sim_start": 1,
            "attributes": {
                "time_to_maturity": 6,
                "principal": 10000,
                "financing_fee": 0.15,
                "underwriter_fee": 0.2,
                "leverage_ratio": 4
            }
        },
        {
            "months_after_sim_start": 8,
            "attributes": {
                "time_to_maturity": 6,
                "principal": 10000,
                "financing_fee": 0.15,
                "underwriter_fee": 0.2,
                "leverage_ratio": 4
            }
        }
    ],
    "simulation": {
        "start_date": "2021-01-01",
        "duration_months": 20,
    }
}

config_box = col1.text_area('Set the simulation parameters', value=json.dumps(config, indent=2), height=600)
simulate_button = col1.button(label="simulate")

# COL 2
def run_simulation(config):
    sim = MainSimulation(config=config)

    deal_go_live_dates = []
    deal_maturity_dates = []
    for deal_config in config["deals"]:
        deal_go_live_date = datetime.strptime(config["simulation"]["start_date"], "%Y-%m-%d") + relativedelta(
            months=deal_config["months_after_sim_start"])
        deal_maturity_date = deal_go_live_date + relativedelta(months=deal_config["attributes"]["time_to_maturity"])
        deal_go_live_dates.append(deal_go_live_date.strftime("%Y/%m/%d"))
        deal_maturity_dates.append(deal_maturity_date.strftime("%Y/%m/%d"))

    deal_dates_df = pd.DataFrame().from_dict({"go_live": deal_go_live_dates, "maturity": deal_maturity_dates})
    deal_dates_df["deal_launch"] = 1
    for idx, row in deal_dates_df.iterrows():
        deal_dates_df.loc[idx, "deal_launch"] = 0 - int(idx) * 0.5


    simulation_df = sim.run()

    # first plot
    chart_1 = sns.lineplot(data=simulation_df[["date", "IT price"]].set_index("date"), palette=("red",), linewidth=0.5)
    locator = mdates.MonthLocator(interval=1)
    chart_1.xaxis.set_major_locator(locator)
    plt.xticks(rotation=45,horizontalalignment='right',fontweight='light')
    plt.xticks(fontsize=6)
    plt.yticks(fontsize=6)
    plt.legend(prop={'size': 6})
    # second plot
    ax2 = plt.twinx()
    chart_2 = sns.lineplot(data=simulation_df.drop(columns=["IT price"]).set_index("date"), linewidth=0.5, ax=ax2)
    locator = mdates.MonthLocator(interval=1)
    chart_2.xaxis.set_major_locator(locator)
    ax2.tick_params(labelbottom=False)
    sns.scatterplot(data=deal_dates_df.set_index("go_live"), linewidth=0.5)
    # plt.setp(ax2.get_xticklabels(), fontsize=6)
    plt.yticks(fontsize=6)
    plt.legend(prop={'size': 6})

    col2.pyplot()


# RUN SIMULATION ON CLICK
if simulate_button:
    gif_runner = col2.image("./static/loading-53.gif")
    config = json.loads(config_box)
    run_simulation(config)
    gif_runner.empty()