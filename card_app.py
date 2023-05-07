
<html>
<head>
	<title>My Website</title>
	<style>
		body {
			background-color: #F0F0F0; /* Grey background */
			font-family: Arial, sans-serif;
			margin: 0;
		}

		header {
			background-color: #333;
			color: #FFF;
			padding: 20px;
			text-align: center;
		}

		nav {
			background-color: #666;
			color: #FFF;
			display: flex;
			justify-content: space-between;
			padding: 10px;
		}

		nav a {
			color: #FFF;
			text-decoration: none;
			padding: 10px;
		}

		nav a:hover {
			background-color: #FFF;
			color: #333;
		}

		section {
			display: flex;
			flex-wrap: wrap;
			justify-content: center;
			padding: 20px;
		}

		article {
			background-color: #FFF;
			border-radius: 10px;
			box-shadow: 2px 2px 10px rgba(0,0,0,0.2);
			margin: 10px;
			padding: 20px;
			width: 300px;
		}

		h1, h2 {
			color: #333;
			font-weight: normal;
			text-align: center;
		}

		p {
			color: #666;
			line-height: 1.5;
			margin-top: 0;
		}

		footer {
			background-color: #333;
			color: #FFF;
			padding: 20px;
			text-align: center;
			position: fixed;
			bottom: 0;
			width: 100%;
		}
	</style>
</head>
<body>
	<header>
		<h1>Welcome to my website</h1>
	</header>
	<nav>
		<a href="#">Home</a>
		<a href="#">About</a>
		<a href="#">Contact</a>
	</nav>
	<section>
		<article>
			<h2>Article 1</h2>
			<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Quisque quis consequat libero, vitae ullamcorper est. Maecenas ut felis at est bibendum hendrerit. </p>
		</article>
		<article>
			<h2>Article 2</h2>
			<p>Sed eget ipsum ac diam posuere lobortis. Integer sit amet elit id erat euismod dapibus vitae ut lectus. Fusce gravida augue orci, vel convallis tortor lobortis id. </p>
		</article>
		<article>
			<h2>Article 3</h2>
			<p>Vivamus dapibus purus ex, vel egestas nulla fringilla ac. Praesent vel malesuada nibh, at luctus nisi. Nullam non nulla ultrices, blandit nunc eu, tincidunt quam. </p>
		</article>
	</section>
	<footer>
		<p>Copyright © 2023</p>
	</footer>
</body>
</html>


import easyocr as ocr  #OCR
import streamlit as st  #Web App
from PIL import Image #Image Processing
import numpy as np #Image Processing 
st. set_page_config(layout="wide")
import re
import pandas as pd

#title
st.title(":orange[BizCard-Extracting-Business-Card-Data]") 
st.write(" ")
col1, col2,col3= st.columns([3,0.5,4.5])
with col1:
    #image uploader
    st.write("## UPLOAD IMAGE")
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
        st.write("## EXTRACTED TEXT")
        st.write('##### :red[WEBSITE URL: ] '+ str(WEB))
        st.write('##### :red[EMAIL: ] '+ str(EMAIL)) 
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
