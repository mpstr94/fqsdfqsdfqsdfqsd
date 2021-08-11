import streamlit as st
import seaborn as sns
import json
import time
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from dateutil.relativedelta import *
import pandas as pd
from fqsdfqsdfqsdfqsd.simulations import MainSimulation

# SOME CONFIG STUFF
st.set_option('deprecation.showPyplotGlobalUse', False)

# def _max_width_():
#     max_width_str = f"max-width: 90vw;"
#     st.markdown(
#         f"""
#     <style>
#     .reportview-container .main .block-container{{
#         {max_width_str}
#     }}
#     </style>
#     """,
#         unsafe_allow_html=True,
#     )
# _max_width_()


def is_authenticated(password):
    return password == "credix_admin"


def generate_login_block():
    block1 = st.empty()
    block2 = st.empty()

    return block1, block2


def clean_blocks(blocks):
    for block in blocks:
        block.empty()


def login(blocks):
    blocks[0].markdown("""
            <style>
                input {
                    -webkit-text-security: disc;
                }
            </style>
        """, unsafe_allow_html=True)

    return blocks[1].text_input('Password')


def run_simulation(config, plotting_area, full_simulation):
    sim = MainSimulation(config=config)
    x_tick_labels = full_simulation["date"].tolist()

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
    deal_dates_df["idx"] = 0
    for idx, row in deal_dates_df.iterrows():
        deal_dates_df.loc[idx, "deal_launch"] = 0 - int(idx) * 0.5
        deal_dates_df.loc[idx, "idx"] = x_tick_labels.index(row["go_live"])

    simulation_df = sim.run()

    # first plot
    sns.lineplot(data=simulation_df[["date", "IT price"]].set_index("date"), palette=("red",), linewidth=0.5, drawstyle='steps-post')
    plt.xlim((0, len(x_tick_labels)))
    plt.xticks(ticks=range(0,len(x_tick_labels)), labels=x_tick_labels)
    plt.xticks(rotation=45, horizontalalignment='right', fontweight='light')
    plt.xticks(fontsize=6)
    plt.yticks(fontsize=6)
    max_price = max(full_simulation["IT price"])
    plt.ylim((1 - max_price / 100, max_price + max_price / 100))
    plt.legend(loc='upper left', prop={'size': 6})
    print(deal_dates_df)
    # second plot
    ax2 = plt.twinx()
    sns.lineplot(data=simulation_df.drop(columns=["IT price"]).set_index("date"), linewidth=0.5, ax=ax2, drawstyle='steps-post')
    ax2.tick_params(labelbottom=False)
    sns.scatterplot(data=deal_dates_df.set_index("idx"), linewidth=0.5)
    plt.yticks(fontsize=6)
    max_RT = max(full_simulation["RT"])
    plt.ylim((0 - max_RT / 10, max_RT + max_RT / 10))
    plt.legend(loc='upper right', prop={'size': 6})

    plotting_area.pyplot()


def main():
    deals = [{
                "months_after_sim_start": 1,
                "attributes": {
                    "time_to_maturity": 6,
                    "principal": 100000,
                    "financing_fee": 0.15,
                    "underwriter_fee": 0.2,
                    "leverage_ratio": 4
                }
            }]

    # MAIN TITLE
    st.title('Credix simulation')

    # SET COLUMNS
    st.subheader("configuration")
    row1_1, row1_2 = st.columns(2)
    start_date_input = row1_1.date_input('start date of the simulation', datetime.strptime("2021-01-01", "%Y-%m-%d"))
    duration_input = row1_2.number_input('duration (months) of the simulation', value=20)

    st.subheader("investors")
    row2_1, row2_2 = st.columns(2)
    n_investors_input = row2_1.number_input('number of investors', value=100)
    investors_USDC_balance_input = row2_2.slider('initial USDC balance', 0, 10000, (4000, 7000))

    st.subheader("underwriters")
    row3_1, row3_2 = st.columns(2)
    n_underwriters_input = row3_1.number_input('number of underwriters', value=10)
    underwriters_USDC_balance_input = row3_2.slider('initial USDC balance', 0, 100000, (10000, 50000))

    st.subheader("deals")
    deals_input = st.text_area('deals', value=json.dumps(deals, indent=2), height=600)

    row4_1, row4_2 = st.columns((6,1))
    simulate_button = row4_2.button(label="simulate")
    st.write("##")

    def get_config(month=False):
        if not month:
            month = duration_input

        config = {
            "investors": {
                "amount": n_investors_input,
                "USDC_balance": list(investors_USDC_balance_input)
            },
            "underwriters": {
                "amount": n_underwriters_input,
                "USDC_balance": list(underwriters_USDC_balance_input)
            },
            "simulation": {
                "start_date": start_date_input.strftime("%Y-%m-%d"),
                "duration_months": month,
            },
            "deals": json.loads(deals_input)
        }

        return config

    # RUN SIMULATION ON CLICK
    if simulate_button:
        st.header("Simulation")
        plotting_area = st.empty()
        full_simulation = MainSimulation(config=get_config()).run()
        for month in range(1, duration_input + 1):
            config = get_config(month)

            run_simulation(config, plotting_area, full_simulation)
            time.sleep(0.2)

login_blocks = generate_login_block()
password = login(login_blocks)

if is_authenticated(password):
   clean_blocks(login_blocks)
   main()
elif password:
   st.info("Please enter a valid password")