import easyocr as ocr  #OCR
import streamlit as st  #Web App
from PIL import Image #Image Processing
import numpy as np #Image Processing 
st.set_page_config(layout="wide")

# Set the background color
def set_background():
    # Add CSS to change the background color
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #FFC0CB;
            color: black;
        }
        .container {
            background-color: white;
            border: 2px solid black;
            padding: 10px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# Call the function to set the background color
set_background()

#title
st.title(":lime[BizCard: Extracting Business Card Data]") 
st.write(" ")

# Define a container for the image uploader
with st.container():
    # Add a heading for the image uploader
    st.markdown("<h2><span style='background-color: #32D7AC; color: #00008B; font-weight: bold;'>UPLOAD IMAGE</span> <span style='background-color: #32D7AC;'>⬇️</span></h2>", unsafe_allow_html=True)
    # Add a file uploader
    image = st.file_uploader(label="", type=['png', 'jpg', 'jpeg'])
    # Add an image preview
    if image is not None:
        input_image = Image.open(image)
        st.image(input_image, use_column_width=True)

# Load the OCR model
@st.cache
def load_model(): 
    reader = ocr.Reader(['en'])
    return reader 

reader = load_model()

if image is not None:
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
        pass # Replace this line with your code to extract data from the OCR result     
        
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
        st.write("## EXTRACTED DATA")
        st.write('##### :red[WEBSITE URL: ] '+ str(WEB))
        st.write('##### :red[EMAIL ADDRESS: ] '+ str(EMAIL)) 
        st.write('##### :red[PIN CODE: ] '+ str(PIN)) 
        ph_str = ', '.join(PH)
        st.write('##### :red[PHONE NUMBER(S): ] '+ph_str)
        add_str = ' '.join([str(elem) for elem in ADD])
        st.write('##### :red[ADDRESS: ] ', add_str)

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
        st.write('##### :red[CARD HOLDER & COMPANY DETAILS: ] ')
        for i in fin:
            st.write('##### '+i)
            
#         st.write(result_text)
#         st.write(PH)
