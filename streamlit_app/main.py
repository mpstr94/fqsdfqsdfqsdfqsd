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
        deal_maturity_date = deal_go_live_date + relativedelta(months=deal_config["time_to_maturity"])
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


def add_row_to_dataframe(dataframe_area, deal_row):
    try:
        st.session_state.df = st.session_state.df.append(deal_row, ignore_index=True)
        st.session_state.df = st.session_state.df.astype({
            "months_after_sim_start": 'int32',
            "time_to_maturity": 'int32',
            "principal": 'int32',
            "leverage_ratio": 'int32'
        })
        dataframe_area.dataframe(st.session_state.df)
    except:
        pass


def remove_row_from_dataframe(dataframe_area, index):
    if index in st.session_state.df.index:
        st.session_state.df = st.session_state.df.drop(index).reset_index(drop=True)
        dataframe_area.dataframe(st.session_state.df)


def main():
    # MAIN TITLE
    st.title('Credix simulation')

    # SET COLUMNS
    st.subheader("configuration")
    row1_1, row1_2 = st.columns(2)
    start_date_input = row1_1.date_input('start date of the simulation', datetime.strptime("2021-01-01", "%Y-%m-%d"))
    duration_input = row1_2.number_input('duration (months) of the simulation', value=20)

    row2_1, row2_2 = st.columns(2)
    row2_1.subheader("investors")
    n_investors_input = row2_1.number_input('number of investors', min_value=0, value=100)
    row2_2.subheader("underwriters")
    n_underwriters_input = row2_2.number_input('number of underwriters', min_value=0, value=10)

    # Create an empty dataframe
    deals = [{
        "months_after_sim_start": 1,
        "time_to_maturity": 6,
        "principal": 100000,
        "financing_fee": 0.15,
        "underwriter_fee": 0.2,
        "leverage_ratio": 4
    }]
    deals_df = pd.DataFrame.from_dict(deals)

    st.subheader("add deals")
    row3_1, row3_2, row3_3 = st.columns(3)
    months_after_sim_start_input = row3_1.number_input("go live (months)", value=1)
    time_to_maturity_input = row3_2.number_input("time to maturity", value=6)
    principal_input = row3_3.number_input("principal", value=100000)
    row4_1, row4_2, row4_3 = st.columns(3)
    financing_fee_input = row4_1.number_input("financing fee", value=0.15)
    underwriter_fee_input = row4_2.number_input("underwriter fee", value=0.2)
    leverage_ratio_input = row4_3.number_input("leverage ratio", value=4)

    add_deal_button = st.button("add deal")

    st.subheader("remove deals")
    row5_1, _, _ = st.columns(3)
    index_to_remove_input = row5_1.number_input("index to remove", value=0)
    remove_deal_button = st.button("remove deal by index")

    st.subheader("deals")
    # persist state of dataframe
    if 'df' not in st.session_state:
        st.session_state.df = deals_df
    dataframe_area = st.empty()
    dataframe_area.dataframe(st.session_state.df)

    row6_1, row6_2 = st.columns((6,1))
    simulate_button = row6_2.button(label="simulate")
    st.write("##")

    def get_config(month=False):
        if not month:
            month = duration_input

        config = {
            "investors": {
                "amount": n_investors_input,
                "USDC_balance": [4000,5000]
            },
            "underwriters": {
                "amount": n_underwriters_input,
                "USDC_balance": [10000, 50000]
            },
            "simulation": {
                "start_date": start_date_input.strftime("%Y-%m-%d"),
                "duration_months": month,
            },
            "deals": st.session_state.df.to_dict("records")
        }

        return config

    # DEALS INTERACTIVE DF
    if add_deal_button:
        # update dataframe state
        deal_row = {
            "months_after_sim_start": months_after_sim_start_input,
            "time_to_maturity": time_to_maturity_input,
            "principal": principal_input,
            "financing_fee": financing_fee_input,
            "underwriter_fee": underwriter_fee_input,
            "leverage_ratio": leverage_ratio_input
        }
        add_row_to_dataframe(dataframe_area, deal_row)

    if remove_deal_button:
        remove_row_from_dataframe(dataframe_area, index_to_remove_input)

    # RUN SIMULATION ON CLICK
    if simulate_button:
        st.header("Simulation")
        plotting_area = st.empty()
        print(get_config())
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