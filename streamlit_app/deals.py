import pandas as pd
import streamlit as st

deals = [{
            "months_after_sim_start": 1,
            "time_to_maturity": 6,
            "principal": 100000,
            "financing_fee": 0.15,
            "underwriter_fee": 0.2,
            "leverage_ratio": 4
        }]

deals_df = pd.DataFrame.from_dict(deals)


months_after_sim_start_input = st.number_input("months after start simulation", value=1)
time_to_maturity_input = st.number_input("time_to_maturity", value=6)
principal_input = st.number_input("principal", value=100000)
financing_fee_input = st.number_input("financing fee", value=0.15)
underwriter_fee_input = st.number_input("underwriter fee", value=0.2)
leverage_ratio_input = st.number_input("leverage ratio", value=4)
add_deal_button = st.button("add deal")

if add_deal_button:
    deal_row = {
        "months_after_sim_start": months_after_sim_start_input,
        "time_to_maturity": time_to_maturity_input,
        "principal": principal_input,
        "financing_fee": financing_fee_input,
        "underwriter_fee": underwriter_fee_input,
        "leverage_ratio": leverage_ratio_input
    }
    deals_df.append(deal_row, ignore_index=True)
    deals_table = st.write(deals_df)


deals_table = st.write(deals_df)
