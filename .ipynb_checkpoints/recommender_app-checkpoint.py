import streamlit as st
import streamlit.components.v1 as stc
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load Dataset
def load_data(data):
    df = pd.read_csv(data, index_col=0)
    return df

# function to vectorize + find cosine similarity matrix
def vectorize_text_cosine(data):
    count_vect = CountVectorizer()
    cv_mat = count_vect.fit_transform(data)
    # get cosine
    cos_sim_matrix = cosine_similarity(cv_mat)
    return cos_sim_matrix

# function for recommendation system
@st.cache
def get_recommendation(title,cos_sim_matrix,df,num_of_rec=5):
    # indices of the hikes
    hike_indices = pd.Series(df.index, index=df['name']).drop_duplicates()
    #index of hike
    idx = hike_indices[title]
    # look into cosine matrix for that index
    sim_scores = list(enumerate(cos_sim_matrix[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    selected_hike_indices = [i[0] for i in sim_scores[1:]]
    selected_hike_scores = [i[1] for i in sim_scores[1:]]
    # get dataframe and title
    result_df = df.iloc[selected_hike_indices]
    result_df['similarity_score'] = selected_hike_scores
    final_recommened_hikes = result_df[['name','region','type','time_h','length_km','totalAscent','similarity_score']]
    return final_recommened_hikes[:num_of_rec]
    
    
# function for searching for hikes
@st.cache
def search_term_if_not_found(term, df):
    result_df = df[df['name'].str.contains(term)]
    return result_df

# CSS Style for ~Aesthetics~
RESULT_TEMP = """
<h4>{}</h4>
<p style = "color:black;"><span style="color:red;">Region: </span>{}</p>
<p style = "color:black;"><span style="color:red;">Trail Type: </span>{}</p>
<p style = "color:black;"><span style="color:red;">Time (h): </span>{}</p>
<p style = "color:black;"><span style="color:red;">Length (km): </span>{}</p>
<p style = "color:black;"><span style="color:red;">Total Ascent (m): </span>{}</p>

</div>
"""
import base64

@st.cache(allow_output_mutation=True)
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_png_as_page_bg(png_file):
    bin_str = get_base64_of_bin_file(png_file)
    page_bg_img = '''
    <style>
    body {
    background-image: url("data:image/png;base64,%s");
    background-size: cover;
    }
    </style>
    ''' % bin_str
    
    st.markdown(page_bg_img, unsafe_allow_html=True)
    return


def main():
    set_png_as_page_bg('images/background.png')
    st.title('New Zealand Hiking Trail Recommender')
    
    menu = ['Recommend','About']
    choice = st.selectbox("Directory", menu)
    
    df = load_data("data/WalkingKiwi_Tracks4.csv")
    
        
    if choice == "Recommend":
        st.subheader("Recommend Hikes")
        cos_sim_matrix = vectorize_text_cosine(df['name'])
        search_term = st.text_input('Search by Trail Name')
        num_rec = st.number_input("Number of Recommended Hikes",5,25,5)
        if st.button("Recommend"):
            if search_term is not None:
                try:
                    results = get_recommendation(search_term, cos_sim_matrix,df,num_of_rec=num_rec)
                    for row in results.iterrows():
                        rec_title = row[1][0]
                        rec_region = row[1][1]
                        rec_type = row[1][2]
                        rec_time = row[1][3]
                        rec_length = row[1][4]
                        rec_ascent = row[1][5]
                        rec_score = row[1][6]
                        
                        stc.html(RESULT_TEMP.format(rec_title,rec_region,rec_type,rec_time,rec_length,rec_ascent,rec_score), height=300)
                        #left, right = st.beta_columns(2)
                        #output = stc.html(RESULT_TEMP.format(rec_title,rec_region,rec_type,rec_time,rec_length,rec_ascent,rec_score), height=350)
                        #left.write(output)
                        #right.text_input("later fill")
                except:
                    results = 'Trail Name Not Found'
                    st.warning(results)
                    st.info("Suggested Hiking Trails:")
                    result_df = search_term_if_not_found(search_term, df)
                    for row in result_df['name']:
                        st.write(row)
                        
    if choice == "About":
        st.subheader("Home")
        st.write('Welcome to the hiking trail recommender system for New Zealand. Some of the hiking trail information was assembled from the [Department of Conservation (DOC)](https://www.doc.govt.nz) and used under the [Creative Commons 3.0 license](https://creativecommons.org/licenses/by/3.0/nz/) in combination with track data obtained from other sources. \n\n Recommender systems are among the most popular applications of data science today. They help to overcome the problem of being inundated with choices, and that does away with needing to filter choices based on a plethora of attributes such as location, preference, etc. With this recommendation system you can parse through trailheads to find appropriate hikes that suite your needs and help you get out and enjoy the beauty of New Zealand.')
        if st.button("Recommend Hikes"):
            choice = "Recommend"
        
        st.write('Check out the following table for all the track information:')
        st.dataframe(df.drop(columns=['coordinates','trackElevation','url','lng','lat']))
                
    
if __name__ == '__main__':
    main()