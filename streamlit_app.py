import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd

st.title(f":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write(
  """Choose the fruits you want in your custom Smoothie!
  """
)
name_on_order = st.text_input("Name on Smoothie")
st.write("The name of your Smoothie will be", name_on_order)
cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
#st.dataframe(data=my_dataframe, use_container_width=True)
#st.stop()
pd_df=my_dataframe.to_pandas()
#st.dataframe(pd_df)
#st.stop()
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe,
    max_selections=5
)
if ingredients_list:
    INGREDIENTS_STRING = ''

    for fruit_chosen in ingredients_list:
        INGREDIENTS_STRING += fruit_chosen + ' '
      
        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        #st.write('The search value for ', fruit_chosen,' is ', search_on, '.')

        st.subheader(fruit_chosen + ' Nutrition Information')
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + search_on)
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

    my_insert_stmt = (
    "insert into smoothies.public.orders(ingredients, name_on_order) "
    "values ('" + INGREDIENTS_STRING + "', '" + name_on_order + "')")
    time_to_insert = st.button('Submit Order')
    if INGREDIENTS_STRING:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")
