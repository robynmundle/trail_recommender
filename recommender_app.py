import streamlit as st
import streamlit.components.v1 as stc
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from path import Path
import base64
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import euclidean_distances

# Load Dataset
def load_data(data):
    df = pd.read_csv(data, index_col=0)
    return df

def euclidean_rec(title, df,num_of_rec):
    # change route type and regions into dummy values -- if filtered, the dummies will update appropriately for the current df
    trail_recomm = pd.get_dummies(df[['name','type','time_h','length_km','netElevation','totalAscent','lng','lat','region']], columns=['type','region'])
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
    # Find the num_rec indices with the minimum distance (highest similarity) to the hike we're looking at
    ordered_indices = distances.argsort()
    closest_indices = ordered_indices[1:num_of_rec+1]
    # Get the hikes for these indices abnd relate back to original df
    closest_trails = trail_recomm.iloc[closest_indices]
    hike_names = closest_trails['name'].tolist()
    # go back to df
    result_df = df[df['name'].isin(hike_names)][['name','region','type','time_h','length_km','totalAscent','trackElevation']]
    return result_df

# function for searching for hikes without trail name
@st.cache
def search_term_if_not_found(term, df):
    result_df = df[df['name'].str.contains(term)]
    return result_df[['name','region','type','time_h','length_km','totalAscent','trackElevation']]

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

header_html = "<img src='data:image/png;base64,{}' class='img-fluid'>".format(img_to_bytes("images/Recommender_Header.png"))
st.markdown(header_html, unsafe_allow_html=True,)

def main():       
    menu = ['Recommend','Data Overview']
    choice = st.sidebar.radio("Directory", menu)
    st.sidebar.write('Welcome to the hiking trail recommender system for New Zealand.\n\n Recommender systems are among the most popular applications of data science today. They help to overcome the problem of being inundated with choices. With this recommendation system you can parse through trailheads to find appropriate hikes that suite your needs and help you get out and enjoy the beauty of New Zealand.\n\nSome of the hiking trail information was assembled from the [Department of Conservation (DOC)](https://www.doc.govt.nz) and used under the [Creative Commons 3.0 license](https://creativecommons.org/licenses/by/3.0/nz/) in combination with track data obtained from other sources.')
    
    df = load_data("data/WalkingKiwi_Tracks4.csv")
    
    if choice == "Recommend":
        st.subheader("Hike Search Engine")
        
        search_term = st.text_input('Search by Trail Name')
        
        # extra search parameters -- filter dataset based on given parameters
        with st.beta_expander("Filter Search Parameters"):
            region_selection, type_selection = st.beta_columns(2)
            regions = sorted(df.region.unique())
            regions.insert(0,'All Regions')
            with region_selection: 
                region_opt = st.selectbox('Search by Region', regions)
                if region_opt != 'All Regions': 
                    df = df[df['region'] == region_opt]
            types = sorted(df.type.unique())
            types.insert(0,'All Route Types')
            with type_selection:
                type_opt = st.selectbox('Search by Route Type', types)
                if type_opt != 'All Route Types': 
                    df = df[df['type'] == type_opt]
                    
            time_selection, length_selection = st.beta_columns(2)
            times = ['All Lengths (h)','Short (< 1 hour)','Medium (1 - 5 hours)','Long (5+ hours)']
            with time_selection: 
                time_opt = st.selectbox('Search by Duration', times)
                if time_opt == 'Short (< 1 hour)': 
                    df = df[df['time_h'] < 1]
                elif time_opt == 'Medium (1 - 5 hours)': 
                    df = df[(df['time_h'] >= 1) & (df['time_h'] < 5)]
                elif time_opt == 'Long (5+ hours)':
                    df = df[df['time_h'] >= 5]
            lengths = ['All Lengths (km)','Short (< 5 km)','Medium (5 - 10 km)','Long (10+ km)']
            with length_selection:
                length_opt = st.selectbox('Search by Length', lengths)
                if length_opt == 'Short (< 5 km)': 
                    df = df[df['length_km'] < 5]
                elif length_opt == 'Medium (5 - 10 km)': 
                    df = df[(df['length_km'] >= 5) & (df['time_h'] < 10)]
                elif length_opt == 'Long (10+ km)':
                    df = df[df['length_km'] >= 10]
                    
            ascent_selection, num_selection = st.beta_columns(2)
            grade = ['All Elevations (m)','Easy (< 100 m)','Moderate (100 - 600 m)','Challenging (600+ m)']
            with ascent_selection: 
                ascent_opt = st.selectbox('Search by Total Elevation', grade)
                if ascent_opt == 'Easy (< 100 m)': 
                    df = df[df['totalAscent'] < 100]
                elif ascent_opt == 'Moderate (100 - 600 m)': 
                    df = df[(df['totalAscent'] >= 100) & (df['totalAscent'] < 600)]
                elif ascent_opt == 'Challenging (600+ m)':
                    df = df[df['totalAscent'] >= 600]
            with num_selection:
                num_rec = st.number_input("Number of Hikes to Recommend",3,25,5)
                
        if st.button("Recommend"):            
            if search_term is not None:
                try:
                    result_df = euclidean_rec(search_term, df, num_of_rec=num_rec)
                    col1, col2 = st.beta_columns(2)
                    for row in result_df.iterrows():
                        with st.beta_expander(row[1][0]):
                            col1, col2 = st.beta_columns(2)
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
                                stc.html(RESULT_TEMP.format(rec_title,rec_region,rec_type,rec_hour,rec_min,rec_length,rec_ascent), height=250)
                            with col2:
                                st.image('images/02432-Queenstown-Queenstown-Sara-Orme.jpg', use_column_width='auto')
                            fig, ax = plt.subplots();
                            sns.lineplot(y=rec_elev, x=np.arange(start=0, stop=float(rec_length), step=rec_length/len(rec_elev)), ax=ax);
                            ax.set(title=rec_title, xlabel='Distance (km)', ylabel='Elevation (m)');
                            ax.grid();
                            st.pyplot(fig);                        
                except:
                    st.info("Suggested Hiking Trail Names:")
                    result_df = search_term_if_not_found(search_term, df)[:num_rec]
                    for row in result_df.iterrows():
                        with st.beta_expander(row[1][0]):
                            col1, col2 = st.beta_columns(2)
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
                                stc.html(RESULT_TEMP.format(rec_title,rec_region,rec_type,rec_hour,rec_min,rec_length,rec_ascent), height=250)
                            with col2:
                                st.image('images/0434-Lake-Matheson-West-Coast-Miles-Holden.jpg', use_column_width='auto')
                            fig, ax = plt.subplots();
                            sns.lineplot(y=rec_elev, x=np.arange(start=0, stop=float(rec_length), step=rec_length/len(rec_elev)), ax=ax);
                            ax.set(title=rec_title, xlabel='Distance (km)', ylabel='Elevation (m)');
                            ax.grid();
                            st.pyplot(fig);  

    elif choice == "Data Overview":
        st.subheader("Data Overview")
        st.write('Check out the following table for all the track information:')
        st.dataframe(df[['name','region','type','time_h','length_km','totalAscent','netElevation','minElevation','maxElevation']])
                
    
if __name__ == '__main__':
    main()