import streamlit as st
import streamlit.components.v1 as stc
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from path import Path
import base64
import pydeck as pdk
import altair as alt
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import euclidean_distances
import copy

st.set_page_config(layout="wide")
# -----------------------------------------------------
# Load Dataset
def load_data(data):
    df = pd.read_csv(data, index_col=0)
    return df
# Modify Dataset
def param_filter(df, region_opt, time_opt, length_opt, ascent_opt):
    filtered_df = df.copy(deep=True)
    
    if region_opt != 'All Regions': 
        filtered_df = filtered_df[filtered_df['region'] == region_opt]
    
    if time_opt == 'Short (< 1 hour)': 
        filtered_df = filtered_df[filtered_df['time_h'] < 1]
    elif time_opt == 'Medium (1 - 5 hours)': 
        filtered_df = filtered_df[(filtered_df['time_h'] >= 1) & (filtered_df['time_h'] < 5)]
    elif time_opt == 'Long (5+ hours)':
        filtered_df = filtered_df[filtered_df['time_h'] >= 5]
    
    if length_opt == 'Short (< 5 km)': 
        filtered_df = filtered_df[filtered_df['length_km'] < 5]
    elif length_opt == 'Medium (5 - 10 km)': 
        filtered_df = filtered_df[(filtered_df['length_km'] >= 5) & (df['length_km'] < 10)]
    elif length_opt == 'Long (10+ km)':
        filtered_df = filtered_df[filtered_df['length_km'] >= 10]
    
    if ascent_opt == 'Easy (< 100 m)': 
        filtered_df = filtered_df[filtered_df['totalAscent'] < 100]
    elif ascent_opt == 'Moderate (100 - 600 m)': 
        filtered_df = filtered_df[(filtered_df['totalAscent'] >= 100) & (df['totalAscent'] < 600)]
    elif ascent_opt == 'Challenging (600+ m)':
        filtered_df = filtered_df[filtered_df['totalAscent'] >= 600]
    
    return filtered_df
# -----------------------------------------------------
# geographical map of hiking trails loaded
def main_map(filtered_df):
    st.pydeck_chart(pdk.Deck(
        layers=[pdk.Layer('ScatterplotLayer', filtered_df, get_position=['lon', 'lat'],
                          auto_highlight=True, get_radius=1250, # Radius is given in meters
                          get_fill_color=[255, 0, 0, 1000], pickable=True)], 
        initial_view_state=pdk.ViewState(longitude=np.average(filtered_df['lon']), latitude=np.average(filtered_df['lat']),
                                         zoom=6, min_zoom=4, max_zoom=10, pitch=40.5, bearing=0),
        map_style='mapbox://styles/mapbox/outdoors-v11', 
        tooltip={'html': '{name}', 'style': {'color': 'white'}}))
# -----------------------------------------------------
# find closest euclidean distance as recommendation engine
def euclidean_rec(title, df, filtered_df, num_of_rec):
    # change route type into dummy values
    trail_recomm = pd.get_dummies(df[['name','time_h','length_km','netElevation','totalAscent','type']], columns=['type'])
    X = trail_recomm.drop(columns='name').values
    # Standardize the features so that no feature dominates the distance computations due to unit scale
    scaler = StandardScaler().fit(X)
    X = scaler.transform(X)
    # the hike you searched for
    hike_lookup = trail_recomm.loc[trail_recomm['name'] == title]
    hike_lookup = hike_lookup.drop(columns='name').values
    hike_lookup = scaler.transform(hike_lookup)
    # Distance from all other hikes
    distances = euclidean_distances(X, hike_lookup)
    distances = distances.reshape(-1)
    # Find the indices with the minimum distance (highest similarity) to the hike we're looking at
    ordered_indices = distances.argsort()
    closest_indices = ordered_indices[:26] 
    # Get the hikes for these indices abnd relate back to original df or filtered df if appropriate
    closest_trails = trail_recomm.iloc[closest_indices]
    hike_names = closest_trails['name'].tolist()
    # go back to df wqith parameter filtering
    result_df = filtered_df[filtered_df['name'].isin(hike_names)][['name','region','type','time_h','length_km','totalAscent','trackElevation','lat','lon','coordinates']]
    result_df = result_df.iloc[pd.Categorical(result_df['name'], categories=hike_names, ordered=True).argsort()]
    print(result_df)
    return result_df[:num_of_rec+1]
# -----------------------------------------------------
# function for searching for hikes without trail name
def search_term_if_not_found(term, df):
    result_df = df[df['name'].str.contains(term)]
    return result_df[['name','region','type','time_h','length_km','totalAscent','trackElevation','lat','lon','coordinates']]
# -----------------------------------------------------
def hike_summary(search_term, df):
    for row in df[df['name'] == search_term].iterrows():
        rec_time = row[1][3]
        rec_hour, rec_min = str(rec_time).split('.')
        rec_min = int(int(rec_min)*.60)
        st.subheader(f"Trails Relating to **{row[1][0]}**")
        st.text(f"Region: {row[1][13]} \t Time: {rec_hour}h, {rec_min}min \t Total Elevation: {row[1][7]}")
# -----------------------------------------------------
def output_results(result_df):
    for row in result_df.iterrows():
        with st.beta_expander(row[1][0]):
            col1, col2 = st.beta_columns([1,2])
            with col1:
                rec_title = row[1][0]
                rec_region = row[1][1]
                rec_type = row[1][2]
                rec_time = row[1][3]
                rec_hour, rec_min = str(rec_time).split('.')
                rec_min = int(int(rec_min)*.60)
                rec_length = row[1][4]
                rec_ascent = row[1][5]
                rec_elev = row[1][6]
                rec_elev = str(rec_elev).split(',')
                rec_elev = [float(i) for i in rec_elev]
                rec_lat = row[1][7]
                rec_lon  = row[1][8]
                rec_coord = row[1][9]
                stc.html(RESULT_TEMP.format(rec_title,rec_region,rec_type,rec_hour,rec_min,rec_length,rec_ascent), height=250)
            with col2:
                source = pd.DataFrame({'Elevation (m)': rec_elev, 'Distance (km)': np.arange(start=0, stop=float(rec_length), step=rec_length/len(rec_elev))})
                c  = alt.Chart(source).mark_line().encode(x='Distance (km)', y='Elevation (m)', tooltip=['Distance (km)','Elevation (m)'])
                st.altair_chart(c, use_container_width=True)
            
            st.pydeck_chart(pdk.Deck(layers=[pdk.Layer('ScatterplotLayer', result_df, get_position=['lon', 'lat'], get_radius=50, # Radius is given in meters
                          get_fill_color=[255, 0, 0, 1000])],
                                     initial_view_state=pdk.ViewState(latitude=rec_lat, longitude=rec_lon, zoom=12, bearing=0, pitch=45),
                                     map_style='mapbox://styles/mapbox/satellite-streets-v11'))
            
# ------------------ Page Set-Up ------------------
# CSS Style for ~Aesthetics~
RESULT_TEMP = """
<p style = "color:black;margin-bottom: -10px;"><b>{}</b></p>
<p style = "color:black;margin-bottom: -10px;"><span style="color:red;">Region: </span>{}</p>
<p style = "color:black;margin-bottom: -10px;"><span style="color:red;">Trail Type: </span>{}</p>
<p style = "color:black;margin-bottom: -10px;"><span style="color:red;">Time: </span>{}<span> hr, </span>{}<span> min</span></p>
<p style = "color:black;margin-bottom: -10px;"><span style="color:red;">Length: </span>{}<span> km</span></p>
<p style = "color:black;margin-bottom: -10px;"><span style="color:red;">Total Ascent: </span>{}<span> m</span></p>
"""

def img_to_bytes(img_path):
    img_bytes = Path(img_path).read_bytes()
    encoded = base64.b64encode(img_bytes).decode()
    return encoded

header_html = "<img src='data:image/png;base64,{}' class='img-fluid'>".format(img_to_bytes("images/Recommender_Header_wide.png"))
st.markdown(header_html, unsafe_allow_html=True,)

menu = ['Recommend','Data Overview']
choice = st.sidebar.radio("Directory", menu)
st.sidebar.write('Welcome to the hiking trail recommender system for New Zealand.\n\n Recommender systems are among the most popular applications of data science today. They help to overcome the problem of being inundated with choices. With this recommendation system you can parse through trailheads to find appropriate hikes that suite your needs and help you get out and enjoy the beauty of New Zealand.\n\nSome of the hiking trail information was assembled from the [Department of Conservation (DOC)](https://www.doc.govt.nz) and used under the [Creative Commons 3.0 license](https://creativecommons.org/licenses/by/3.0/nz/) in combination with track data obtained from other sources.')
# ------------------ Page Set-Up ------------------

def main():   
    df = load_data("data/WalkingKiwi_Tracks5.csv")

    if choice == "Recommend":
        st.subheader("Hike Search Engine")
        search_term = st.text_input('Search by Trail Name')
        left, right = st.beta_columns(2)
        with left:
            # extra search parameters -- filter dataset based on given parameters
            regions = sorted(df.region.unique())
            regions.insert(0,'All Regions')
            region_opt = st.selectbox('Search by Region', regions)
            times = ['All Lengths (h)','Short (< 1 hour)','Medium (1 - 5 hours)','Long (5+ hours)']
            time_opt = st.selectbox('Search by Duration', times)            
            lengths = ['All Lengths (km)','Short (< 5 km)','Medium (5 - 10 km)','Long (10+ km)']
            length_opt = st.selectbox('Search by Length', lengths)            
            grade = ['All Elevations (m)','Easy (< 100 m)','Moderate (100 - 600 m)','Challenging (600+ m)']
            ascent_opt = st.selectbox('Search by Total Elevation', grade)            
            num_rec = st.number_input("Number of Hikes to Recommend",3,25,5)
            filtered_df = param_filter(df, region_opt, time_opt, length_opt, ascent_opt)            
        with right:
            st.write(" ")
            st.write(' ')
            main_map(filtered_df)

        if st.button("Recommend"):            
            try:
                result_df = euclidean_rec(search_term, df, filtered_df, num_of_rec=num_rec)
                hike_summary(search_term, df)
                output_results(result_df)
            except:
                st.info("Suggested Hiking Trail Names:")
                results_df = search_term_if_not_found(search_term, filtered_df)[:num_rec]
                output_results(results_df)

    elif choice == "Data Overview":
        st.subheader("Data Overview")
        st.write('Check out the following table for all the track information:')
        st.dataframe(df[['name','region','type','time_h','length_km','totalAscent','netElevation','minElevation','maxElevation']])

# -----------------------------------------------------    
if __name__ == '__main__':
    main()