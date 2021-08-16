import streamlit as st
import streamlit.components.v1 as components
import seaborn as sns
import json
import time
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from dateutil.relativedelta import *
import pandas as pd
from fqsdfqsdfqsdfqsd.simulations import MainSimulation


def simulation_page():
    # hidden div with anchor
    st.markdown("<div id='linkto_top'></div>", unsafe_allow_html=True)

    def run_simulation(config, plotting_area):
        sim = MainSimulation(config=config)
        simulation_df = sim.run()
        x_tick_labels = simulation_df["date"].tolist()

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

        # first plot
        sns.lineplot(data=simulation_df[["date", "IT price"]].set_index("date"), palette=("red",), linewidth=0.5,
                     drawstyle='steps-post')
        plt.xlim((0, len(x_tick_labels)))
        plt.xticks(ticks=range(0, len(x_tick_labels)), labels=x_tick_labels)
        plt.xticks(rotation=45, horizontalalignment='right', fontweight='light')
        plt.xticks(fontsize=6)
        plt.yticks(fontsize=6)
        max_price = max(simulation_df["IT price"])
        plt.ylim((1 - max_price / 100, max_price + max_price / 100))
        plt.legend(loc='upper left', prop={'size': 6})
        # second plot
        ax2 = plt.twinx()
        sns.lineplot(data=simulation_df.drop(columns=["IT price"]).set_index("date"), linewidth=0.5, ax=ax2,
                     drawstyle='steps-post')
        ax2.tick_params(labelbottom=False)
        sns.scatterplot(data=deal_dates_df.set_index("idx"), linewidth=0.5)
        plt.yticks(fontsize=6)
        max_RT = max(simulation_df["RT"])
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

        st.markdown("""---""")
        # SET COLUMNS
        st.subheader("configuration")
        row1_1, row1_2 = st.columns(2)
        start_date_input = row1_1.date_input('start date of the simulation',
                                             datetime.strptime("2021-01-01", "%Y-%m-%d"))
        duration_input = row1_2.number_input('duration (months) of the simulation', value=20)

        st.markdown("""---""")
        row2_1, row2_2 = st.columns(2)
        row2_1.subheader("investors")
        n_investors_input = row2_1.number_input('number of investors', min_value=0, value=100)
        row2_2.subheader("underwriters")
        n_underwriters_input = row2_2.number_input('number of underwriters', min_value=0, value=10)

        st.markdown("""---""")
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

        st.subheader("DEALS")
        # persist state of dataframe
        if 'df' not in st.session_state:
            st.session_state.df = deals_df
        dataframe_area = st.empty()
        dataframe_area.dataframe(st.session_state.df)

        row3_1, _, _, row3_4 = st.columns((3, 3, 0.5, 3))
        row3_1.subheader("add deals")
        row3_4.subheader("remove deals")

        row4_1, row4_2, row4_3, row4_4 = st.columns((3, 3, 0.5, 3))
        months_after_sim_start_input = row4_1.number_input("go live (months)", value=1)
        time_to_maturity_input = row4_2.number_input("time to maturity", value=6)
        principal_input = row4_1.number_input("principal", value=100000)
        financing_fee_input = row4_2.number_input("financing fee", value=0.15)
        underwriter_fee_input = row4_1.number_input("underwriter fee", value=0.2)
        leverage_ratio_input = row4_2.number_input("leverage ratio", value=4)

        row4_1, _, _ = st.columns((6, 0.5, 3))
        add_deal_button = row4_1.button("add deal")

        index_to_remove_input = row4_4.number_input("index to remove", value=0)
        remove_deal_button = row4_4.button("remove deal")

        st.markdown("""---""")
        simulate_button = st.button(label="simulate")
        st.write("##")

        def get_config():
            config = {
                "investors": {
                    "amount": n_investors_input,
                    "USDC_balance": [4000, 5000]
                },
                "underwriters": {
                    "amount": n_underwriters_input,
                    "USDC_balance": [10000, 50000]
                },
                "simulation": {
                    "start_date": start_date_input.strftime("%Y-%m-%d"),
                    "duration_months": duration_input,
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
            run_simulation(get_config(), plotting_area)
            time.sleep(0.2)

        st.markdown("<a href='#linkto_top' id='goToTop'>Back to top</a>", unsafe_allow_html=True)

    main()
