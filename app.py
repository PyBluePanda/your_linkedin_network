import streamlit as st
from streamlit_extras.stylable_container import stylable_container
from streamlit_extras.buy_me_a_coffee import button
import warnings 
import pandas as pd
from janitor import clean_names
import streamlit.components.v1 as components
from pyvis import network as net
import networkx as nx


warnings.filterwarnings("ignore")

st.set_page_config(page_title="Your LinkedIn Connections", page_icon=":globe_with_meridians:")


with stylable_container(
    key="title_container",
    css_styles="""
        {
            padding: calc(1em - 1px);
            text-align: center;
        }
        """,
):
    st.markdown('''# :orange[Your LinkedIn Connections] :globe_with_meridians:''')

col1, col2 = st.columns([6,6])

with col1:
    with stylable_container(
        key="Intro",
        css_styles="""
            {
                border: 0.1px solid rgba(80, 80, 80, 0.5);
                border-radius: 0.5rem;
                padding: calc(1em - 1px);
                text-align: left;
                background-color: #CC5500;
            }
            """,
    ):

        st.markdown("""
            - Your Profile >
            - Account > Settings & Privacy >
            - Data Privacy > Get a Copy of your Data
            - Want something in particular? >
            - Connections > Request Archive >
            - Check your email for the file.
            """)
        # st.markdown("Want something in particular? > Connections > Request Archive > Check email for file.")

with col2:
    uploaded_file = st.file_uploader("Select your LinkedIn Connections.csv file here:")

    if uploaded_file is not None:
        df_ori = pd.read_csv(uploaded_file, skiprows=3) # remove top rows
    else:
        st.warning('Please upload a LinkedIn connections.csv file to begin.')
        st.stop()

# ==== data input form ====

form = st.form(key="form_settings")
form_col1, form_col2, form_col3 = form.columns([3,3,3])

num_conn = form_col1.number_input(
    "Min Number of Connections",
    1,
    20,
    step=1,
    key="num_conn",
    value=3
)

name = form_col2.text_input(
    "Your Name",
    key="name",
    value="Me"
)

timesteps = form_col3.number_input(
    "Simulation steps",
    20,
    80,
    step=5,
    key="timesteps",
    value=40
)

form.form_submit_button(label="Submit")
css="""
<style>
    [data-testid="stForm"] {
        background: #CC5500;
    }
</style>
"""
st.write(css, unsafe_allow_html=True)

# ==== end of form ====


df = (
    df_ori
    .clean_names() # remove spacing and capitalization
    .drop(columns=['first_name', 'last_name', 'email_address']) # drop for privacy
    .dropna(subset=['company', 'position']) # drop missing values in company and position
    .to_datetime('connected_on', format='%d %b %Y')
  )

pattern = "freelance|self-employed"
df = df[~df['company'].str.contains(pattern, case=False)]


# creating bar graphs
df_company = df['company'].value_counts().reset_index()
df_company.columns = ['company', 'count']
df_top_co = df_company.sort_values(by='count', ascending=False).head(15)

# co_graph = px.bar(df_top_co, x='count', y='company', color='count', orientation='h', color_continuous_scale=str_to_class(color_option)).update_layout(yaxis_categoryorder="total ascending")
# st.header('Connections by Company')
# st.write(co_graph)
# st.markdown('#')

df_pos = df['position'].value_counts().reset_index()
df_pos.columns = ['position', 'count']
df_top_pos = df_pos.sort_values(by='count', ascending=False).head(15)

# pos_graph = px.bar(df_top_pos, x='count', y='position', color='count', orientation='h', color_continuous_scale=str_to_class(color_option)).update_layout(yaxis_categoryorder="total ascending")
# st.header('Connections by Position')
# st.write(pos_graph)
# st.markdown('#')

# hist_values = px.histogram(df['connected_on'], nbins=15, orientation='h', color=df['connected_on'].dt.year, color_discrete_sequence=str_to_class(color_option)).update_layout(bargap=0.1)
# st.header('Connections by Date')
# st.write(hist_values)
# st.markdown('#')

count_option = num_conn
root_name = name
graph_option = "spoked"
color_network_option = ['#088CFF', '#36A3FF', '#64BAFE', '#91D1FE', '#BFE8FD', '#EDFFFD']


# prepping data for the first network graph
df_position = df['position'].value_counts().reset_index()
df_position.columns = ['position', 'count']
df_position = df_position.sort_values(by="count", ascending=False)

df_company_reduced = df_company.loc[df_company['count']>=count_option]


# px.colors.sequential.Inferno
# initialize graph
g = nx.Graph()
g.add_node(root_name)

# use iterrows tp iterate through the data frame
for _, row in df_company_reduced.iterrows():

  # store company name and count
  company = row['company']
  count = row['count']

  title = f"<b>{company}</b> – {count}"
  positions = set([x for x in df[company == df['company']]['position']])
  positions = ''.join('<li>{}</li>'.format(x) for x in positions)

  position_list = f"<ul>{positions}</ul>"
  hover_info = title + position_list

  g.add_node(company, size=count*5, weight=count, color=color_network_option, title=hover_info, borderWidth=4)
  g.add_edge(root_name, company, color='grey')

# generate the graph
nt = net.Network(height='700px', width='100%', bgcolor='#222222', font_color='white')

# set the physics layout of the network
# nt.barnes_hut()
# nt = net.Network('750px', '100%', bgcolor='#31333f', font_color='white')
nt.from_nx(g)
graph_option # user option for either a spoked or packed graph
nt.save_graph(f'company_graph.html')
st.header('Connections by Company Graph')
HtmlFile = open(f'company_graph.html','r',encoding='utf-8')

# Load HTML into HTML component for display on Streamlit
components.html(HtmlFile.read(), height=700, width=700)

with open("company_graph.html", "rb") as file:
     btn = st.download_button(
             label="Download company graph",
             data=file,
             file_name="company_graph.html",
             mime="file/html"
           )

st.markdown('#')


# # prepping data for the 2nd network graph
# df_position_reduced = df_pos.loc[df_pos['count']>=position_option]

# # initialize graph
# p = nx.Graph()
# p.add_node(root_name)

# # use iterrows tp iterate through the data frame
# for _, row in df_position_reduced.iterrows():

#   count = f"{row['count']}"
#   position= row['position']
  
#   p.add_node(position, size=count, weight=count, color=color_network_option, title=count, borderWidth=4, strokeWidth=2, strokeColor='black')
#   p.add_edge(root_name, position, color='grey')

# # generate the graph
# nt = net.Network('750px', '100%', bgcolor='#31333f',  font_color='white')
# nt.from_nx(p)
# graph_option # user option for either a spoked or packed graph
# nt.save_graph(f'position_graph.html')
# HtmlFile = open(f'position_graph.html','r',encoding='utf-8')

# # Load HTML into HTML component for display on Streamlit
# st.header('Connections by Position Graph')
# components.html(HtmlFile.read(), height=800, width=800)

# with open("position_graph.html", "rb") as file:
#      btn = st.download_button(
#              label="Download position graph",
#              data=file,
#              file_name="position_graph.html",
#              mime="file/html"
#            )
     

with stylable_container(
        key="end_container",
        css_styles="""
            {
                border: 0.1px solid rgba(80, 80, 80, 0.5);
                border-radius: 0.5rem;
                padding: calc(1em - 1px);
                background-color: #CC5500;
            }
            """,
    ):  
    end_col1, end_col2 = st.columns([4,2])
    with end_col1:
        
        st.markdown("More info and :star: at [github.com/"
                    "pybluepanda/covid-networkx](https://github.com/"
                    "PyBluePanda/covid-networkx.git)"
        )
    with end_col2:
        button(username="samvautier", floating=False, width=221)
        



