# coding=utf-8
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


# SOME CONFIG STUFF
st.set_option('deprecation.showPyplotGlobalUse', False)

m = st.markdown("""
<style>
button {
    width: 100% !important;
}
</style>""", unsafe_allow_html=True)

# hidden div with anchor
st.markdown("<div id='linkto_top'></div>", unsafe_allow_html=True)

stakeholders_text = '''
### Borrowers

Today, Fintechs and non-bank lending businesses in underserved markets are often limited to sourcing capital locally. But why do they actually need debt financing? Here's a clearer picture: local banks see them as competitors and thus do not want to lend them any capital. Because they do not provide them access, they are dependent on family offices and institutional investors. This can require high interest rates and long and non-efficient capital sourcing cycles. At Credix we work closely with our investors and borrowers to automate the sourcing and create more efficient access to capital. This way our borrowers can focus on what they do best, providing loans to those in need. 

Credix works with non-bank financial institutions and lenders in emerging countries to distribute the capital to their end-clients. The borrowers draw down stable coins from our automated smart contract driven credit facilities and convert this into their local currency (fiat). Credix selects those lending businesses / partners based on historical loan performance, defaults, and risk management processes. To achieve the most accurate due-diligence and risk scoring, we will be assisted by specialised firms.

### Underwriters

Our underwriters are represented by a group of institutional investors and high-net worth individuals. These accredited investors supply the junior tranche of our credit deals. Meaning they take a higher risk (first-loss capital) but have potentially higher yields because of the senior tranche leverage. They analyze our deals as individual investment opportunities. Their confidence in supplying capital gives trust for our investors in the junior tranche. Underwriters will receive an underwriter fee (avg. 20%) on the accrued interest paid out monthly after the senior tranche. 

### Investors

Individuals, financial organizations, and corporates can supply capital to our liquidity pool to earn a low-risk but stable and attractive yield. Their capital is allocated to the deals underwritten by the Underwriters, representing the senior tranche. They are thus protected by the first-loss capital as provided by the underwriters. 
'''
deals_text = '''
Borrowers can create deals on the Credix platform. Each deal has its own parameters such as principal amount, financing fee, time to maturity, and leverage ratio. Once a deal is created, it's not active yet. For a deal to go live and the borrower to receive the requested principal, underwriters have to assess the deal. They base their assessment on the borrower's information (current debt, end-borrowers, balance sheet...) and past performance as found on the Credix platform. If an underwriter decides that the deal looks interesting, they stake USDC in the deal's junior tranche. In return, they receive an Underwriter Token (UT) representing their stake. As soon as the junior tranche is full, the senior tranche is opened. The senior tranche will be funded by our investors. In contrast to the underwriters, the investors do not participate on a deal-to-deal basis. They invest in the liquidity pool and receive Investor Tokens (IT) whose price is reflected by the Net Asset Value of our credit fund. When both tranches are funded, the deal goes live and the borrower receives the principal amount in USDC. 

On a monthly basis, the borrower performs an interest repayment. Those re-payments lead to an increase of the IT price, and thus profit for the investors. The principal is repaid at the time of maturity (similar to interest-only bullet loans). The investors are protected by the underwriters as the latter take losses first. Due to this higher risk, the underwriters get an underwriter fee, represented as a fixed percentage (20%) of the interest paid out to the investors.  

All stakeholders are rewarded using Credix Tokens (CRED). Underwriters and borrowers receive an amount of BTs depending on how much USDC they stake in the credit fund, and the duration they stay locked. Borrowers get BTs if they re-pay on time and the correct amount. The supply of BTs will decrease over time, and they can be used to participate in governance decisions, and get other benefits such as early access to deals.
'''


def is_authenticated(password):
    return password == "p"


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


def run_simulation(config, plotting_areas):
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
    sns.lineplot(data=simulation_df[["date", "IT price"]].set_index("date"), palette=("red",), linewidth=0.5, drawstyle='steps-post')
    plt.xlim((0, len(x_tick_labels)))
    plt.xticks(ticks=range(0,len(x_tick_labels)), labels=x_tick_labels)
    plt.xticks(rotation=45, horizontalalignment='right', fontweight='light')
    plt.xticks(fontsize=6)
    plt.yticks(fontsize=6)
    max_price = max(simulation_df["IT price"])
    plt.ylim((1 - max_price / 100, max_price + max_price / 100))
    plt.legend(loc='upper left', prop={'size': 6})
    # second axis
    ax2 = plt.twinx()
    sns.lineplot(data=simulation_df.drop(columns=["IT price"]).set_index("date"), linewidth=0.5, ax=ax2, drawstyle='steps-post')
    ax2.tick_params(labelbottom=False)
    sns.scatterplot(data=deal_dates_df.set_index("idx"), linewidth=0.5)
    plt.yticks(fontsize=6)
    max_RT = max(simulation_df["RT"])
    plt.ylim((0 - max_RT / 10, max_RT + max_RT / 10))
    plt.legend(loc='upper right', prop={'size': 6})
    plotting_areas[0].pyplot()

    # second plot
    sns.lineplot(data=simulation_df[["date", "IT price"]].set_index("date"), palette=("red",), linewidth=0.5,
                 drawstyle='steps-post')
    plt.xlim((0, len(x_tick_labels)))
    plt.xticks(ticks=range(0, len(x_tick_labels)), labels=x_tick_labels)
    plt.xticks(rotation=45, horizontalalignment='right', fontweight='light')
    plt.xticks(fontsize=6)
    plt.yticks(fontsize=6)
    plt.legend(loc='upper left', prop={'size': 6})
    plotting_areas[1].pyplot()

    # second plot
    sns.lineplot(data=simulation_df[["date", "repayment pool"]].set_index("date"), palette=("red",), linewidth=0.5,
                 drawstyle='steps-post')
    plt.xlim((0, len(x_tick_labels)))
    plt.xticks(ticks=range(0, len(x_tick_labels)), labels=x_tick_labels)
    plt.xticks(rotation=45, horizontalalignment='right', fontweight='light')
    plt.xticks(fontsize=6)
    plt.yticks(fontsize=6)
    plt.legend(loc='upper left', prop={'size': 6})
    plotting_areas[2].pyplot()


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


def render_simulation():
    # MAIN TITLE
    st.title('Credix simulation')
    st.text("We've built a fully fledged simulation model to test our token flows, and crypto economics. ")

    st.markdown("""---""")
    # SET COLUMNS
    st.subheader("configuration")
    row1_1, row1_2 = st.columns(2)
    start_date_input = row1_1.date_input('start date of the simulation', datetime.strptime("2021-01-01", "%Y-%m-%d"))
    duration_input = row1_2.number_input('duration (months) of the simulation', value=20)

    st.markdown("""---""")
    st.subheader("STAKEHOLDERS")
    stakeholder_expander = st.expander(label='Learn about our stakeholders')
    with stakeholder_expander:
        st.markdown(stakeholders_text)

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
    deal_expander = st.expander(label='Learn about deals')
    with deal_expander:
        st.markdown(deals_text)
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
                "USDC_balance": [4000,5000]
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
        plotting_area_1 = st.empty()
        plotting_area_2 = st.empty()
        plotting_area_3 = st.empty()
        plotting_area_4 = st.empty()
        plotting_area_5 = st.empty()
        plotting_area_6 = st.empty()
        plotting_areas = [plotting_area_1, plotting_area_2, plotting_area_3, plotting_area_4, plotting_area_5, plotting_area_6]
        run_simulation(get_config(), plotting_areas)

    st.markdown("<a href='#linkto_top' id='goToTop'>Back to top</a>", unsafe_allow_html=True)


# LOGIN PART
login_blocks = generate_login_block()
password = login(login_blocks)

if is_authenticated(password):
    clean_blocks(login_blocks)
    render_simulation()
    # SCROLL TO TOP OF PAGE
    top_of_page_html = '''
    <script language="javascript">
     console.log("scrolling to top")
     document.getElementById('goToTop').click();
    </script>
    '''
    components.html(top_of_page_html)
elif password:
    st.info("Please enter a valid password")