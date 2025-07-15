import streamlit as st
import pandas as pd
import csv
import os

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
file_path = os.path.join(root_dir, 'purchase_order.csv')  
print(root_dir)
print(file_path)

st.title('PO Review')


po_df = pd.read_csv(
    file_path,
    quoting=csv.QUOTE_MINIMAL,   
    on_bad_lines='skip',         
    encoding='utf-8'            
)

# po_df = pd.read_csv(file_path,encoding='ISO-8859-1')

# st.radio('PO Filter',['All','Open'])
po_number=st.selectbox('PO Number',placeholder="Select PO",options=po_df['Purchase_Order_ID'].to_list())

material_id_options=po_df[po_df['Purchase_Order_ID']==po_number]['RawMaterial_ID'].to_list()
material_id=st.selectbox('Material ID',placeholder="Select Material ID",options=material_id_options)
supplier_id=st.selectbox('Supplier ID',placeholder="Select Supplied ID", options=['S001','S002','S003'])
supplier_name=f'Supplier_{supplier_id}'
st.text(f'Supplier Name: {supplier_name}')

c1,c2,c3=st.columns(3)
with c2:
    st.button('Assign Supplier to PO',type="primary",use_container_width=True)