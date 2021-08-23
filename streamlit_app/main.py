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
st.markdown("<div id='start'></div>", unsafe_allow_html=True)

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


def plot_chart(plotting_area, simulation_df, deal_go_live_and_maturity, withdrawal_dates, column, locator, title, ylabel):
    dates_x_axis = list(simulation_df.date)
    fig, axs = plt.subplots(2,1,figsize=(16,12), gridspec_kw={'height_ratios': [4, 1]})
    sns.lineplot(data=simulation_df[["date", column]].set_index("date"), palette=("blue",), linewidth=1, ax=axs[0])
    axs[0].get_xaxis().set_visible(False)
    axs[0].set_title(title, fontdict={'fontsize': 24}, pad=20)
    axs[0].set_ylabel(ylabel, fontdict={'fontsize': 16})
    axs[0].get_legend().remove()
    for deal in deal_go_live_and_maturity:
        axs[0].axvline(x=dates_x_axis.index(deal[0]), linewidth=0.5, linestyle='dashed', color='green')
        axs[0].axvline(x=dates_x_axis.index(deal[1]), linewidth=0.5, linestyle='dashed', color='red')
    for withdrawal_date in withdrawal_dates:
        axs[0].axvline(x=dates_x_axis.index(withdrawal_date), linewidth=0.5, linestyle='dashed', color='black')
    set_x_ticks(plt)
    plt.setp(axs[0].get_xticklabels(), visible=False)

    min_height, max_height = plot_deals(deal_go_live_and_maturity, axs[1], dates_x_axis)
    plot_widthdrawals(withdrawal_dates, axs[1], dates_x_axis)
    axs[1].set_ylim(ymin = min_height - 0.1, ymax = max_height + 0.1)
    axs[1].sharex(axs[0])
    axs[1].xaxis.set_major_locator(locator)
    axs[1].set_xlim(xmin = 0, xmax = len(dates_x_axis))
    axs[1].get_yaxis().set_visible(False)
    axs[1].set_title("Deals (---) & withdrawals (◼️)", fontdict={'fontsize': 18})

    plotting_area.pyplot()


def set_x_ticks(plt):
    plt.xticks(rotation=45, horizontalalignment='right', fontweight='light')
    plt.xticks(fontsize=10)
    plt.yticks(fontsize=10)


def plot_deals(deal_go_live_and_maturity, ax, dates_x_axis):
    height = 1
    for deal in deal_go_live_and_maturity:
        ax.plot([dates_x_axis.index(deal[0]), dates_x_axis.index(deal[1])], [height, height], linewidth=1, linestyle='dashed', color='black')
        ax.scatter([dates_x_axis.index(deal[0])], [height], s=100, linewidth=1, linestyle='dashed', color='green')
        ax.scatter([dates_x_axis.index(deal[1])], [height], s=100, linewidth=1, linestyle='dashed', color='red')
        height -= 0.1
    return height - 0.1, 1.1


def plot_widthdrawals(withdrawal_dates, ax, dates_x_axis):
    for withdrawal_date in withdrawal_dates:
        ax.scatter([dates_x_axis.index(withdrawal_date)], [1.1], s=100, color='black', marker="s")


def run_simulation(config, plotting_areas):
    sim = MainSimulation(config=config)
    simulation_df, deal_go_live_and_maturity, withdrawal_dates = sim.run()
    locator = mdates.MonthLocator(interval=1)
    plot_chart(plotting_areas[0], simulation_df, deal_go_live_and_maturity, withdrawal_dates, "APY 30d trailing", locator, "30-day trailing APY (investors)", "%")
    plot_chart(plotting_areas[1], simulation_df, deal_go_live_and_maturity, withdrawal_dates, "IT", locator, "Investor Tokens (IT)", "amount")
    plot_chart(plotting_areas[2], simulation_df, deal_go_live_and_maturity, withdrawal_dates, "RT", locator, "Reserve Tokens (RT)", "amount")
    plot_chart(plotting_areas[3], simulation_df, deal_go_live_and_maturity, withdrawal_dates, "IT price", locator, "IT Price", "IT price (in USDC)")
    plot_chart(plotting_areas[4], simulation_df, deal_go_live_and_maturity, withdrawal_dates, "TVL", locator, "Total Value Locked (without reserve)", "USDC")
    plot_chart(plotting_areas[5], simulation_df, deal_go_live_and_maturity, withdrawal_dates, "credit outstanding", locator, "Credit outstanding", "USDC")
    plot_chart(plotting_areas[6], simulation_df, deal_go_live_and_maturity, withdrawal_dates, "repayment pool", locator, "Repayment Pool", "USDC")
    plot_chart(plotting_areas[7], simulation_df, deal_go_live_and_maturity, withdrawal_dates, "credix fees", locator, "Credix fees", "USDC")


def add_row_to_dataframe(dataframe_area, dataframe_name, deal_row):
    try:
        st.session_state[dataframe_name] = st.session_state[dataframe_name].append(deal_row, ignore_index=True)
        # st.session_state.deals_df = st.session_state.deals_df.astype({
        #     "time_to_maturity": 'int64',
        #     "principal": 'int64',
        #     "leverage_ratio": 'int64'
        # })
        dataframe_area.dataframe(st.session_state[dataframe_name])
    except:
        pass


def remove_row_from_dataframe(dataframe_area, dataframe_name, index):
    if index in st.session_state[dataframe_name].index:
        st.session_state[dataframe_name] = st.session_state[dataframe_name].drop(index).reset_index(drop=True)
        dataframe_area.dataframe(st.session_state[dataframe_name])


##############
# MAIN TITLE #
##############
st.title('Credix simulation')
st.text("We've built a fully fledged simulation model to test our token flows, and crypto economics. ")
st.markdown("""---""")

#################
# CONFIGURATION #
#################
st.subheader("configuration")
row1_1, row1_2 = st.columns(2)
start_date_input = row1_1.date_input('start date of the simulation', datetime.strptime("2021-01-01", "%Y-%m-%d"))
duration_input = row1_2.number_input('duration (months) of the simulation', value=36)
st.markdown("""---""")

################
# STAKEHOLDERS #
################
st.subheader("STAKEHOLDERS")
stakeholder_expander = st.expander(label='Learn about our stakeholders')
with stakeholder_expander:
    st.markdown(stakeholders_text)

row2_1, row2_2 = st.columns(2)
row2_1.subheader("investors")
n_investors_input = row2_1.number_input('number of investors', min_value=0, value=20, help="Set the number of investors. Each investor has 10.000 USDC in its wallet at the start of the simulation.")
row2_2.subheader("underwriters")
n_underwriters_input = row2_2.number_input('number of underwriters', min_value=0, value=5, help="Set the number of underwriters. Each underwriter has 100.000 USDC in its wallet at the start of the simulation.")
st.markdown("""---""")

#########
# DEALS #
#########
deals = [
    {
        "deal_go_live": "2021-02-01",
        "time_to_maturity": 12,
        "principal": 100000,
        "financing_fee": 0.15,
        "underwriter_fee": 0.2,
        "leverage_ratio": 4,
        "repay_fraction_interest": 1,
        "repay_fraction_principal": 1
    },
    {
        "deal_go_live": "2021-08-01",
        "time_to_maturity": 12,
        "principal": 100000,
        "financing_fee": 0.15,
        "underwriter_fee": 0.2,
        "leverage_ratio": 4,
        "repay_fraction_interest": 1,
        "repay_fraction_principal": 1
    },
    {
        "deal_go_live": "2022-03-01",
        "time_to_maturity": 12,
        "principal": 100000,
        "financing_fee": 0.15,
        "underwriter_fee": 0.2,
        "leverage_ratio": 4,
        "repay_fraction_interest": 1,
        "repay_fraction_principal": 1
    },
]

deals_df = pd.DataFrame.from_dict(deals)

st.subheader("DEALS")
deal_expander = st.expander(label='Learn about deals')
with deal_expander:
    st.markdown(deals_text)
# persist state of dataframe
if 'deals_df' not in st.session_state:
    st.session_state["deals_df"] = deals_df
deals_dataframe_area = st.empty()
deals_dataframe_area.dataframe(st.session_state["deals_df"])

row3_1, _, _, row3_4 = st.columns((3, 3, 0.5, 3))
row3_1.subheader("add deals")
row3_4.subheader("remove deals")

row4_1, row4_2, row4_3, row4_4 = st.columns((3, 3, 0.5, 3))
deal_go_live_input = row4_1.date_input('go live date', datetime.strptime("2021-02-01", "%Y-%m-%d"))
# months_after_sim_start_input = row4_1.number_input("go live (months)", value=1)
time_to_maturity_input = row4_2.number_input("time to maturity", value=6, help="Number of months before the principal is paid back in full.")
principal_input = row4_1.number_input("principal", value=100000, help="The total amount of the credit line in USDC.")
financing_fee_input = row4_2.number_input("financing fee", value=0.15, help="The percentage of the principal (= sur plus) that has to be repaid as interest, e.g. 15% (⇒ total interest = USDC 150.000).")
underwriter_fee_input = row4_1.number_input("underwriter fee", value=0.2, help="The percentage taken by the underwriters on the repaid interest to the investors. Acts as a reward for taking more risk.")
leverage_ratio_input = row4_2.number_input("leverage ratio", value=4, help="The ratio of the size of the senior tranche over the junior tranche e.g. 4 ⇒ For every 4 parts senior tranche, there is 1 part junior tranche (= 80% senior, 20% junior).")
repay_fraction_interest_input = row4_1.number_input("repay fraction of interest", value=1.0, help="In an ideal scenario, the full interest payment is made every month. Using this setting, you can simulate unhappy flows by changing the percentage per interest payment that is made. If an interest payment is 100 USDC and this setting is 0.8, only 80 USDC will be repaid every month.")
repay_fraction_principal_input = row4_2.number_input("repay fraction of principal", value=1.0, help="In an ideal scenario, the full principal payment is made at time of maturity. Using this setting, you can simulate unhappy flows by changing the percentage of the principal payment that is made. If the principal payment is 1000 USDC and this setting is 0.8, only 800 USDC will be repaid at time of maturity.")

row5_1, _, _ = st.columns((6, 0.5, 3))
add_deal_button = row5_1.button("add deal")

index_to_remove_deal_input = row4_4.number_input("deal index to remove", value=0, help="In the table above, every deal has an index (most outer left column). You can delete deals by index.")
remove_deal_button = row4_4.button("remove deal")
st.markdown("""---""")

# DEALS INTERACTIVE DF
if add_deal_button:
    # update dataframe state
    deal_row = {
        "deal_go_live": deal_go_live_input.strftime("%Y-%m-%d"),
        "time_to_maturity": time_to_maturity_input,
        "principal": principal_input,
        "financing_fee": financing_fee_input,
        "underwriter_fee": underwriter_fee_input,
        "leverage_ratio": leverage_ratio_input,
        "repay_fraction_interest": repay_fraction_interest_input,
        "repay_fraction_principal": repay_fraction_principal_input
    }
    add_row_to_dataframe(deals_dataframe_area, "deals_df", deal_row)

if remove_deal_button:
    remove_row_from_dataframe(deals_dataframe_area, "deals_df", index_to_remove_deal_input)

###############
# WITHDRAWALS #
###############
IT_withdrawals = [
        {
            "withdrawal_date": "2021-10-01",
            "IT_amount": 2000
        },
        {
            "withdrawal_date": "2022-07-01",
            "IT_amount": 100000
        }
    ]

withdrawals_df = pd.DataFrame.from_dict(IT_withdrawals)

st.subheader("WITHDRAWALS")

# persist state of dataframe
if 'withdrawals_df' not in st.session_state:
    st.session_state["withdrawals_df"] = withdrawals_df
withdrawals_dataframe_area = st.empty()
withdrawals_dataframe_area.dataframe(st.session_state["withdrawals_df"])

row6_1, _, _, row6_4 = st.columns((3, 3, 0.5, 3))
row6_1.subheader("add withdrawal")
row6_4.subheader("remove withdrawal")

row7_1, row7_2, row7_3, row7_4 = st.columns((3, 3, 0.5, 3))
withdrawal_date_input = row7_1.date_input('withdrawal date', datetime.strptime("2021-06-01", "%Y-%m-%d"), help="At this date, a number of investors will be selected to withdraw 'IT amount' from Credix. Their IT will be converted into USDC at the current IT price. Credix will first try to swap IT's with RT holders. If there are no RT holders, IT's will be burned and the investors will receive USDC from the repayment pool.")
IT_amount_input = row7_2.number_input("IT amount", value=10000, help="The total amount of IT to be withdrawn.")

row8_1, _, _ = st.columns((6, 0.5, 3))
add_withdrawal_button = row8_1.button("add withdrawal")

index_to_remove_withdrawal_input = row7_4.number_input("withdrawal index to remove", value=0, help="In the table above, every withdrawal has an index (most outer left column). You can delete withdrawals by index.")
remove_withdrawal_button = row7_4.button("remove withdrawal")
st.markdown("""---""")

# WITHDRAWALS INTERACTIVE DF
if add_withdrawal_button:
    # update dataframe state
    withdrawal_row = {
        "withdrawal_date": withdrawal_date_input.strftime("%Y-%m-%d"),
        "IT_amount": IT_amount_input
    }
    add_row_to_dataframe(withdrawals_dataframe_area, "withdrawals_df", withdrawal_row)

if remove_withdrawal_button:
    remove_row_from_dataframe(withdrawals_dataframe_area, "withdrawals_df", index_to_remove_withdrawal_input)

##############
# SIMULATION #
##############
simulate_button = st.button(label="simulate")
st.write("##")


def get_config():
    config = {
        "investors": {
            "amount": n_investors_input,
            "USDC_balance": [10000,10000]
        },
        "underwriters": {
            "amount": n_underwriters_input,
            "USDC_balance": [100000, 100000]
        },
        "simulation": {
            "start_date": start_date_input.strftime("%Y-%m-%d"),
            "duration_months": duration_input,
        },
        "deals": st.session_state["deals_df"].to_dict("records"),
        "IT_withdrawals": st.session_state["withdrawals_df"].to_dict("records")
    }

    return config


st.header("Simulation")
plotting_area_1 = st.empty()
st.markdown("""---""")
plotting_area_2 = st.empty()
st.markdown("""---""")
plotting_area_3 = st.empty()
st.markdown("""---""")
plotting_area_4 = st.empty()
st.markdown("""---""")
plotting_area_5 = st.empty()
st.markdown("""---""")
plotting_area_6 = st.empty()
st.markdown("""---""")
plotting_area_7 = st.empty()
st.markdown("""---""")
plotting_area_8 = st.empty()
st.markdown("""---""")
plotting_areas = [plotting_area_1, plotting_area_2, plotting_area_3, plotting_area_4,
                  plotting_area_5, plotting_area_6, plotting_area_7, plotting_area_8]

# RUN SIMULATION ON CLICK
if simulate_button:
    run_simulation(get_config(), plotting_areas)

# run_simulation(get_config(), plotting_areas)

st.markdown("<a href='#start' id='goToTop'>Back to top</a>", unsafe_allow_html=True)

top_of_page_html = '''
    <script language="javascript">
    document.addEventListener('DOMContentLoaded', (event) => {
      document.getElementById('goToTop').click();
      console.log("scrolling to top");
    })
    </script>
    '''
components.html(top_of_page_html)
