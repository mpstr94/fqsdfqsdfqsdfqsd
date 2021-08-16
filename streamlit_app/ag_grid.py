import streamlit as st
import pandas as pd
import numpy as np
import SessionState

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
row1_1, row1_2, row1_3 = st.columns(3)
months_after_sim_start_input = row1_1.number_input("months after start simulation", value=1)
time_to_maturity_input = row1_2.number_input("time_to_maturity", value=6)
principal_input = row1_3.number_input("principal", value=100000)
row2_1, row2_2, row2_3 = st.columns(3)
financing_fee_input = row2_1.number_input("financing fee", value=0.15)
underwriter_fee_input = row2_2.number_input("underwriter fee", value=0.2)
leverage_ratio_input = row2_3.number_input("leverage ratio", value=4)

add_deal_button = st.button("add deal")

st.subheader("remove deals")
row3_1, _, _ = st.columns(3)
index_to_remove_input = row3_1.number_input("index to remove", value=0)
remove_deal_button = st.button("remove deal by index")

st.subheader("deals")
# persist state of dataframe
if 'df' not in st.session_state:
    st.session_state.df = deals_df
dataframe_area = st.empty()
dataframe_area.dataframe(st.session_state.df)

def add_row_to_dataframe(dataframe_area, deal_row):
    try:
        st.session_state.df = st.session_state.df.append(deal_row, ignore_index=True)
        dataframe_area.dataframe(st.session_state.df)
    except:
        pass


def remove_row_from_dataframe(dataframe_area, index):
    if index in st.session_state.df.index:
        st.session_state.df = st.session_state.df.drop(index).reindex()
        dataframe_area.dataframe(st.session_state.df)


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
    print("im here")
    print(st.session_state.df)

if remove_deal_button:
    remove_row_from_dataframe(dataframe_area, index_to_remove_input)