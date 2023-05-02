from pydoc import doc
from pyparsing import col
import streamlit as st
import pandas as pd
import os
from st_aggrid.shared import GridUpdateMode, DataReturnMode
import base64,random
import time,datetime
from pyresparser import ResumeParser
from pdfminer3.layout import LAParams, LTTextBox
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager
from pdfminer3.pdfinterp import PDFPageInterpreter
from pdfminer3.converter import TextConverter
import io,random
from streamlit_tags import st_tags
from PIL import Image
import pyodbc
from Courses import ds_course,web_course,android_course,ios_course,uiux_course,resume_videos,interview_videos
import pafy
import plotly.express as px
import spacy
from st_aggrid import AgGrid,GridOptionsBuilder
spacy.load('en_core_web_sm')


import nltk
from streamlit_option_menu import option_menu
#from streamlit_lottie import st_lottie
import json
from PyPDF2 import PdfFileReader
import pyodbc



#**************************************************************************************************************
connection = pyodbc.connect(r'DRIVER={SQL Server};'
    r'SERVER=DESKTOP-PTQ7CTJ\SQLEXPRESS;'
    r'DATABASE=sra;'
    r'Trusted_Connection=yes;') 
cursor = connection.cursor()

def insert_data(name,email,res_score,timestamp,no_of_pages,reco_field,cand_level,skills,recommended_skills,courses):
    DB_table_name= 'user_dataa'
    insert_sql = "insert into " + DB_table_name + """
    values (0,?,?,?,?,?,?,?,?,?,?)"""
    rec_values = (name, email, str(res_score), timestamp,str(no_of_pages), reco_field, cand_level, skills,recommended_skills,courses)
    cursor.execute(insert_sql, rec_values)
    connection.commit()

ds_keyword = [ 'Programming', 'Audio', 'Hotel', 'Visual', 'Information technology', 'Supervising', 'Security', 'Database', 'Statistics', 'Mysql','Gis', 'Ubuntu', 'Installation', 'Prototype', 'International', 'Linux', 'Postgresql','Php','Autocad', 'Lean', 'Word','Html', 'Robot', 'Java', 'Css', 'Photoshop','Matlab', 'Python', 'Excel','C','ios','ios development','swift','cocoa','cocoa touch','xcode','android','android development','flutter','kotlin','xml','kivy','react', 'django', 'node jS', 'react js', 'php', 'laravel', 'magento', 'wordpress',
                            'javascript', 'angular js', 'c#', 'flask','tensorflow','keras','pytorch','machine learning','deep Learning','flask','streamlit']
            
def fetch_yt_video(link):
    video = pafy.new(link)
    return video.title

def get_table_download_link(df,filename,text):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    # href = f'<a href="data:file/csv;base64,{b64}">Download Report</a>'
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href

def pdf_reader(file):
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
    page_interpreter = PDFPageInterpreter(resource_manager, converter)
    with open(file, 'rb') as fh:
        for page in PDFPage.get_pages(fh,
                                      caching=True,
                                      check_extractable=True):
            page_interpreter.process_page(page)
            print(page)
        text = fake_file_handle.getvalue()

    # close open handles
    converter.close()
    fake_file_handle.close()
    return text


def show_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    # pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf">'
    pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

def course_recommender(course_list):
    st.subheader("**Courses & Certificates🎓 Recommendations**")
    c = 0
    rec_course = []
    no_of_reco = st.slider('Choose Number of Course Recommendations:', 1, 10, 4)
    random.shuffle(course_list)
    for c_name, c_link in course_list:
        c += 1
        st.markdown(f"({c}) [{c_name}]({c_link})")
        rec_course.append(c_name)
        if c == no_of_reco:
            break
    return rec_course

choose = option_menu("MyCv Parser",["Home","Parser","Rapport"],
    icons=['house','file','graph-up'],
    menu_icon = "list", default_index=0,
    styles={
        "container": {"padding": "5!important", "background-color": ""},
        "icon": {"color": "orange", "font-size": "18px"}, 
        "nav-link": {"font-size": "10px", "text-align": "left", "margin":"5px", "--hover-color": ""},
        "nav-link-selected": {"background-color": ""},
    },orientation = "horizontal"
    )

#*****************************************************************************************************   

if choose=="Parser":
    skillselected = st.sidebar.multiselect("Chose Skills",ds_keyword)
       
    st.sidebar.title("Import cv")
    pdf_file = st.sidebar.file_uploader("Choose your Resume",type=["pdf"])
    if pdf_file is not None:
            
            # st.write(type(pdf_file))
            # file_details = {"filename":pdf_file.name,"filetype":pdf_file.type,"filesize":pdf_file.size}
            # st.write(file_details)
            save_image_path = pdf_file.name
            with open(save_image_path, "wb") as f:
                f.write(pdf_file.getbuffer())
            show_pdf(save_image_path)
            
            resume_data= ResumeParser(save_image_path).get_extracted_data()
            if resume_data:
                    resume_text = pdf_reader(save_image_path)

                    st.header("**Resume Analysis**")
                    st.success("Hello "+ resume_data['name'])
                    st.subheader("**Your Basic info**")
                    try:
                        st.text('Name: '+resume_data['name'])
                        st.text('Email: ' + resume_data['email'])
                        st.text('Contact: ' + resume_data['mobile_number'])
                        st.text('Resume pages: '+str(resume_data['no_of_pages']))
                        st.text('Skills: '+str(resume_data['skills']))
                        skill = resume_data['skills']
                        score = []
                        for i in skill:
                            for j in skillselected:
                                if (i==j):
                                    score.append(i)
                        percent =len(score)*100/len(skillselected)
                        
                        
                    except:
                        pass  
                    cand_level = ''
                    if resume_data['no_of_pages'] == 1:
                        cand_level = "Fresher"
                    elif resume_data['no_of_pages'] == 2:
                        cand_level = "Intermediate"
                    elif resume_data['no_of_pages'] >=3:
                        cand_level = "Experienced"
                    ## Skill shows
                    keywords = st_tags(label='### Skills that you have',
                    text='See our skills recommendation',
                        value=resume_data['skills'],key = '1')

                    ##  recommendation
                    ds_keyword = ['tensorflow','keras','pytorch','machine learning','deep Learning','flask','streamlit']
                    web_keyword = ['react', 'django', 'node jS', 'react js', 'php', 'laravel', 'magento', 'wordpress',
                                'javascript', 'angular js', 'c#', 'flask']
                    android_keyword = ['android','android development','flutter','kotlin','xml','kivy']
                    ios_keyword = ['ios','ios development','swift','cocoa','cocoa touch','xcode']
                    uiux_keyword = ['ux','adobe xd','figma','zeplin','balsamiq','ui','prototyping','wireframes','storyframes','adobe photoshop','photoshop','editing','adobe illustrator','illustrator','adobe after effects','after effects','adobe premier pro','premier pro','adobe indesign','indesign','wireframe','solid','grasp','user research','user experience']

                    recommended_skills = []
                    reco_field = ''
                    rec_course = ''
                    ## Courses recommendation
                    for i in resume_data['skills']:
                        ## Data science recommendation
                        if i.lower() in ds_keyword:
                            print(i.lower())
                            reco_field = 'Data Science'
                            st.success("** Our analysis says you are looking for Data Science Jobs.**")
                            recommended_skills = ['Data Visualization','Predictive Analysis','Statistical Modeling','Data Mining','Clustering & Classification','Data Analytics','Quantitative Analysis','Web Scraping','ML Algorithms','Keras','Pytorch','Probability','Scikit-learn','Tensorflow',"Flask",'Streamlit']
                            recommended_keywords = st_tags(label='### Recommended skills for you.',
                            text='Recommended skills generated from System',value=recommended_skills,key = '2')
                            st.markdown('''<h4 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h4>''',unsafe_allow_html=True)
                            rec_course = course_recommender(ds_course)
                            break

                        ## Web development recommendation
                        elif i.lower() in web_keyword:
                            print(i.lower())
                            reco_field = 'Web Development'
                            st.success("** Our analysis says you are looking for Web Development Jobs **")
                            recommended_skills = ['React','Django','Node JS','React JS','php','laravel','Magento','wordpress','Javascript','Angular JS','c#','Flask','SDK']
                            recommended_keywords = st_tags(label='### Recommended skills for you.',
                            text='Recommended skills generated from System',value=recommended_skills,key = '3')
                            st.markdown('''<h4 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h4>''',unsafe_allow_html=True)
                            rec_course = course_recommender(web_course)
                            break

                        ## Android App Development
                        elif i.lower() in android_keyword:
                            print(i.lower())
                            reco_field = 'Android Development'
                            st.success("** Our analysis says you are looking for Android App Development Jobs **")
                            recommended_skills = ['Android','Android development','Flutter','Kotlin','XML','Java','Kivy','GIT','SDK','SQLite']
                            recommended_keywords = st_tags(label='### Recommended skills for you.',
                            text='Recommended skills generated from System',value=recommended_skills,key = '4')
                            st.markdown('''<h4 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h4>''',unsafe_allow_html=True)
                            rec_course = course_recommender(android_course)
                            break

                        ## IOS App Development
                        elif i.lower() in ios_keyword:
                            print(i.lower())
                            reco_field = 'IOS Development'
                            st.success("** Our analysis says you are looking for IOS App Development Jobs **")
                            recommended_skills = ['IOS','IOS Development','Swift','Cocoa','Cocoa Touch','Xcode','Objective-C','SQLite','Plist','StoreKit',"UI-Kit",'AV Foundation','Auto-Layout']
                            recommended_keywords = st_tags(label='### Recommended skills for you.',
                            text='Recommended skills generated from System',value=recommended_skills,key = '5')
                            st.markdown('''<h4 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h4>''',unsafe_allow_html=True)
                            rec_course = course_recommender(ios_course)
                            break

                        ## Ui-UX Recommendation
                        elif i.lower() in uiux_keyword:
                            print(i.lower())
                            reco_field = 'UI-UX Development'
                            st.success("** Our analysis says you are looking for UI-UX Development Jobs **")
                            recommended_skills = ['UI','User Experience','Adobe XD','Figma','Zeplin','Balsamiq','Prototyping','Wireframes','Storyframes','Adobe Photoshop','Editing','Illustrator','After Effects','Premier Pro','Indesign','Wireframe','Solid','Grasp','User Research']
                            recommended_keywords = st_tags(label='### Recommended skills for you.',
                            text='Recommended skills generated from System',value=recommended_skills,key = '6')
                            st.markdown('''<h4 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h4>''',unsafe_allow_html=True)
                            rec_course = course_recommender(uiux_course)
                            break      
                    st.subheader("**Resume Score📝**")
                    st.markdown(
                        """
                        <style>
                            .stProgress > div > div > div > div {
                                background-color: #d73b5c;
                            }
                        </style>""",
                        unsafe_allow_html=True,)
                    st.title("Scoring")
                    resume_score = 0
                    if 'Objective' in resume_text:
                        resume_score = resume_score+20
                    if 'Declaration'  in resume_text:
                        resume_score = resume_score + 20
                    if 'Hobbies' or 'Interests'in resume_text:
                        resume_score = resume_score + 20
                    if 'Achievements' in resume_text:
                        resume_score = resume_score + 20
                    if 'Projects' in resume_text:
                        resume_score = resume_score + 20
                    my_bar = st.progress(0)
                    score1 = 0
                    for percent_complete in range(int(resume_score)):
                        score1 +=1
                        time.sleep(0.1)
                        my_bar.progress(percent_complete + 1)
                    st.success('** Your Resume skills Score: ' + str(score1)+'**')
                    
                    ## Insert into table
                    ts = time.time()
                    cur_date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                    cur_time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                    timestamp = str(cur_date+'_'+cur_time)


                    
                    insert_data(resume_data['name'], resume_data['email'], str(resume_score), timestamp,
                                str(resume_data['no_of_pages']), reco_field, cand_level, str(resume_data['skills']),
                                str(recommended_skills), str(rec_course))
                    st.balloons()
                    
elif choose=="Rapport":
        ## Admin Side
        st.success('Welcome to Admin Side')
        # st.sidebar.subheader('**ID / Password Required!**')

        ad_user = st.text_input("Username")
        ad_password = st.text_input("Password", type='password')
        if st.button('Login'):
            if ad_user == 'toto' and ad_password == '123':
                st.success("Welcome")
                # Display Data
                cursor.execute('''SELECT*FROM user_dataa''')
                data = cursor.fetchall()
                st.header("**User's👨‍💻 Data**")
                df = pd.read_sql_query('''SELECT*FROM user_dataa''',connection)
                st.dataframe(df)
                st.markdown(get_table_download_link(df,'User_Data.csv','Download Report'), unsafe_allow_html=True)
                ## Admin Side Data
                query = 'select * from user_dataa;'
                plot_data = pd.read_sql(query, connection)

                ## Pie chart for predicted field recommendations
                labels = plot_data.Predicted_Field.unique()
                print(labels)
                values = plot_data.Predicted_Field.value_counts()
                print(values)
                st.subheader("📈 **Pie-Chart for Predicted Field Recommendations**")
                fig = px.pie(df, values=values, names=labels, title='Predicted Field according to the Skills')
                st.plotly_chart(fig)

                ### Pie chart for User's👨‍💻 Experienced Level
                labels = plot_data.User_level.unique()
                values = plot_data.User_level.value_counts()
                st.subheader("📈 ** Pie-Chart for User's👨‍💻 Experienced Level**")
                fig = px.pie(df, values=values, names=labels, title="Pie-Chart📈 for User's👨‍💻 Experienced Level")
                st.plotly_chart(fig)


            else:
                st.error("Wrong ID & Password Provided")


    
elif choose=="Home":
        st.title("Smart Resume Analyser")
        img = Image.open('SRA_Logo.ico')
        img = img.resize((250,250))
        st.image(img)
