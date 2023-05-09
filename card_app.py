import easyocr as ocr  #OCR
import streamlit as st  #Web App
from PIL import Image #Image Processing
import numpy as np #Image Processing 
st. set_page_config(layout="wide")
import re
import pandas as pd

# Set the background color
def set_background():
    # Add CSS to change the background color
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #e0ebeb;
            color: black;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# Call the function to set the background color
set_background()

#title
icon = "https://cdn-icons-png.flaticon.com/512/262/262239.png"

st.markdown("<h1 style='text-align: center; font-weight: bold; color: white ; background-color:#800080;'>BizCard: Extracting Business Card Data </h1>", unsafe_allow_html=True)

st.image(icon, width="20%")
st.write(" ")

col1, col2,col3= st.columns([3.25,1.5,3.5])
with col1:
    #image uploader
    
    st.markdown("<h2><span style='background-color: #00008B; color: #ffffff; font-weight: bold;'>UPLOAD IMAGE</span> <span style='background-color: #ff3300;'>⬇️</span></h2>", unsafe_allow_html=True)
    image = st.file_uploader(label = "",type=['png','jpg','jpeg'])

@st.cache
def load_model(): 
    reader = ocr.Reader(['en'])#,model_storage_directory='.')
    return reader 

reader = load_model() #load model

if image is not None:
    input_image = Image.open(image) #read image
    with col1:
        #st.write("## YOUR IMAGE")
        st.image(input_image) #display image        
    
    result = reader.readtext(np.array(input_image))
    result_text = [] #empty list for results
    for text in result:
        result_text.append(text[1])
          
    PH=[]
    PHID=[]  
    ADD=set()
    AID=[]
    EMAIL=''
    EID=''
    PIN=''
    PID=''
    WEB=''
    WID=''
    
    for i, string in enumerate(result_text):   
        #st.write(string.lower())   
        
        # TO FIND EMAIL
        if re.search(r'@', string.lower()):
            EMAIL=string.lower()
            EID=i
        
        # TO FIND PINCODE
        match = re.search(r'\d{6,7}', string.lower())
        if match:
            PIN=match.group()
            PID=i
                       
        # TO FIND PHONE NUMBER    
        # match = re.search(r'(?:ph|phone|phno)?(?:[+-]?\d*){7,}', string)
        #match = re.search(r'(?:ph|phone|phno)?\s*(?:[+-]?\d\s*){7,}', string)
        match = re.search(r'(?:ph|phone|phno)?\s*(?:[+-]?\d\s*[\(\)]*){7,}', string)
        if match and len(re.findall(r'\d', string)) > 7:
            PH.append(string)
            PHID.append(i)


            
        # TO FIND ADDRESS 
        keywords = ['road', 'floor', ' st ', 'st,', 'street', ' dt ', 'district',
                    'near', 'beside', 'opposite', ' at ', ' in ', 'center', 'main road',
                   'state','country', 'post','zip','city','zone','mandal','town','rural',
                    'circle','next to','across from','area','building','towers','village',
                    ' ST ',' VA ',' VA,',' EAST ',' WEST ',' NORTH ',' SOUTH ']
        # Define the regular expression pattern to match six or seven continuous digits
        digit_pattern = r'\d{6,7}'
        # Check if the string contains any of the keywords or a sequence of six or seven digits
        if any(keyword in string.lower() for keyword in keywords) or re.search(digit_pattern, string):
            ADD.add(string)
            AID.append(i)
            
        # TO FIND STATE (USING SIMILARITY SCORE)
        states = ['Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh', 'Goa', 'Gujarat', 
          'Haryana','Hyderabad', 'Himachal Pradesh', 'Jharkhand', 'Karnataka', 'Kerala', 'Madhya Pradesh',
            'Maharashtra', 'Manipur', 'Meghalaya', 'Mizoram', 'Nagaland', 'Odisha', 'Punjab', 
            'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Telangana', 'Tripura', 'Uttar Pradesh', 'Uttarakhand', 'West Bengal',
              "United States", "China", "Japan", "Germany", "United Kingdom", "France", "India", 
               "Canada", "Italy", "South Korea", "Russia", "Australia", "Brazil", "Spain", "Mexico", 'USA','UK']

        import Levenshtein
        def string_similarity(s1, s2):
            distance = Levenshtein.distance(s1, s2)
            similarity = 1 - (distance / max(len(s1), len(s2)))
            return similarity * 100
        
        for x in states:
            similarity = string_similarity(x.lower(), string.lower())
            if similarity > 50:
                ADD.add(string)
                AID.append(i)
                
        # WEBSITE URL          
        if re.match(r"(?!.*@)(www|.*com$)", string):
            WEB=string.lower()
            WID=i 
    with col3: 
        # DISPLAY ALL THE ELEMENTS OF BUSINESS CARD 
        st.markdown("<h2><span style='background-color: #00008B; color:#ffffff ; font-weight: bold;'>EXTRACTED DATA</span></h2>", unsafe_allow_html=True)
        
        IDS= [EID,PID,WID]
        IDS.extend(AID)
        IDS.extend(PHID)
#         st.write(IDS)
        oth=''                               
        fin=[]                        
        for i, string in enumerate(result_text):
            if i not in IDS:
                if len(string) >= 4 and ',' not in string and '.' not in string and 'www.' not in string:
                    if not re.match("^[0-9]{0,3}$", string) and not re.match("^[^a-zA-Z0-9]+$", string):
                        numbers = re.findall('\d+', string)
                        if len(numbers) == 0 or all(len(num) < 3 for num in numbers) and not any(num in string for num in ['0','1','2','3','4','5','6','7','8','9']*3):
                            fin.append(string)
        st.markdown("<h4 style='color:red;'>CARD HOLDER & COMPANY DETAILS:</h4>", unsafe_allow_html=True)
        # Collect all the strings in fin list and join them using comma separator
        i_values = ', '.join(fin)

        # Write the i_values to the Streamlit app
        st.write('#### ' + i_values)

        st.markdown('#### <span style="color: red;">EMAIL ADDRESS: </span>' + str(EMAIL), unsafe_allow_html=True)
        ph_str = ', '.join(PH)
        st.markdown('#### <span style="color: red;">PHONE NUMBER(s): </span>' + ph_str, unsafe_allow_html=True)
        st.markdown('#### <span style="color: red;">WEBSITE URL: </span>' + str(WEB), unsafe_allow_html=True)
        add_str = ' '.join([str(elem) for elem in ADD])
        st.markdown('#### <span style="color: red;">ADDRESS: </span>' + add_str, unsafe_allow_html=True)
        st.markdown('#### <span style="color: red;">PIN CODE: </span>' + str(PIN), unsafe_allow_html=True)

        
