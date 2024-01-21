######################

## IMPORT LIBRARIES ##
######################
import requests
import feedparser
import schedule
import time

from time import sleep
from datetime import timedelta, datetime
from dateutil import parser

###########################################
## IMPORT BOT API CONNECTION INFORMATION ##
###########################################
# Get Info from non public .PY-file to connect to Bot
from Non_Public_Info import Bot_Auth_Token, Bot_Channel_ChatID


###################
## RSS FEED URLS ##
###################
URLs = ["https://www.mpg.de/feeds/jobs.rss",  # Max-Planck Institute (< 4 weeks Feed provided!)
        "https://kidoktorand.varbi.com/en/what:rssfeed",  # Karolinska Institute
        "https://uu.varbi.com/what:rssfeed/",  # Uppsala University
        "https://portal.mytum.de/jobs/wissenschaftler/asRss", # Technical University of Munich
        "https://adb.zuv.uni-heidelberg.de/info/INFO_FDB$.rss_feed",  # Heidelberg University
        "https://www.universiteitleiden.nl/vacatures/rss.xml",  # Leiden University (< 1 week Feed provided!)
        "https://www.fz-juelich.de/++api++/@@rss?portal_type=Joboffer"] # FZ Juelich (Helmholtz)
	    # "https://employment.ku.dk/phd/?get_rss=1", # University of Copenhagen (< 1 week Feed provided!) # Wrong links provided via RSS




###################################
## BOT DATA FOR SENDING MESSAGES ##
###################################

def Send_To_Channel(Message):
    bot_token = Bot_Auth_Token  # Hidden Token
    bot_chatID = Bot_Channel_ChatID  # Hidden Chat-ID

    send_text = 'https://api.telegram.org/bot' + bot_token + \
                '/sendMessage?chat_id=' + bot_chatID + \
                '&text=' + Message

    response = requests.get(send_text)

    return response.json()  # Get response Info


################################################
## IMPORT RSS DATA AND CHECK FOR NEW POSTINGS ##
################################################

# List of relevant strings in title to check for
titles = ["Doktorand", "Doctoral",
          "Doktorand*innen", "DoktorandInnen", "Doktorand*in", "Doktorand/in",
          "Promotionsstelle", "Promotion",
          "PhD", "PHD", " Ph.D", "Ph.D.", "(PhD)", "PhD-Student*",
          "pre-doctoral"]

# TAGS ##v
keywords_diseases = ["Alzheimer's Disease", "Parkinson's Disease", "Huntington's Disease", "Multiple Sclerosis", "Amyotrophic Lateral Sclerosis (ALS)", "Cancer", "Diabetes", "HIV/AIDS", "Tuberculosis", "Malaria", "Dengue Fever", "Zika Virus", "Ebola", "Influenza", "COVID-19", "Hepatitis", "Cholera", "Rabies", "Leprosy", "Polio", "Measles", "Mumps", "Rubella", "Chickenpox", "Shingles", "Pneumonia", "Bronchitis", "Asthma", "COPD (Chronic Obstructive Pulmonary Disease)", "Emphysema", "Cystic Fibrosis", "Lung Cancer", "Breast Cancer", "Colon Cancer", "Prostate Cancer", "Ovarian Cancer", 
                     "Osteoarthritis", "Gout", "Lupus", "Fibromyalgia", "Crohn's Disease", "Ulcerative Colitis", "Irritable Bowel Syndrome (IBS)", "Gastritis", "Peptic Ulcer Disease", "GERD (Gastroesophageal Reflux Disease)", "Kidney Stones", "Bladder Infections", "Glaucoma", "Cataracts", "Macular Degeneration", "Retinitis Pigmentosa", "Hearing Loss", "Tinnitus", "Meniere's Disease", "Epilepsy", "Migraine", "Schizophrenia", "Bipolar Disorder", "Depression", "Anxiety Disorders", "Obsessive-Compulsive Disorder (OCD)", "Post-Traumatic Stress Disorder (PTSD)", "Autism Spectrum Disorder", 
                     "Fragile X Syndrome", "Tourette Syndrome", "Williams Syndrome", "Turner Syndrome", "Klinefelter Syndrome", "Colorectal Cancer", "Liver Cancer", "Oral Cancer", "Laryngeal Cancer", "Nasopharyngeal Cancer", "Brain Cancer", "Bone Cancer", "Testicular Cancer", "Penile Cancer", "Vaginal Cancer", "Vulvar Cancer", "Uterine Cancer", "Cervical Cancer", "ADHD (Attention-Deficit/Hyperactivity Disorder)", "Down Syndrome", "Cerebral Palsy", "Muscular Dystrophy", "Hemolytic Anemia", "Deep Vein Thrombosis (DVT)", 
                     "Sjogren's Syndrome", "Myasthenia Gravis", "Lyme Disease", "Fibrous Dysplasia", "Marfan Syndrome", "Polycystic Kidney Disease", "Wilson's Disease", "Sarcoidosis", "Gallstones", "Hemochromatosis", "Osteoporosis", "Psoriasis", "Liver Cancer", "Pancreatic Cancer", "Gallbladder Cancer", "Bile Duct Cancer", "Throat Cancer", "Esophageal Cancer", "Stomach Cancer", "Leukemia", "Lymphoma", "Sickle Cell Anemia", "Hemophilia", "Thalassemia", "Rheumatoid Arthritis", "Autism Spectrum Disorder", 
                     "Vitiligo", "Eczema", "Rosacea", "Acne", "Hirsutism", "Alopecia", "Vaginal Yeast Infection", "Endometriosis", "Polycystic Ovary Syndrome (PCOS)", "Premenstrual Syndrome (PMS)", "Erectile Dysfunction", "Premature Ejaculation", "Infertility", "Prostatitis", "Interstitial Cystitis", "Dermatitis", "Cellulitis", "Melanoma", "Basal Cell Carcinoma", "Kaposi's Sarcoma", "Thyroid Disorders", "Hashimoto's Thyroiditis", "Graves' Disease", "Pituitary Disorders", "Addison's Disease", "Cushing's Syndrome", "Pernicious Anemia", "Sickle Cell Disease", "G6PD Deficiency",
                     "Pulmonary Embolism", "Atherosclerosis", "Hypertension", "Congestive Heart Failure", "Arrhythmia", "Atrial Fibrillation", "Coronary Artery Disease", "Valvular Heart Disease", "Hemorrhoids", "Diverticulitis", "Pancreatitis", "Gastric Ulcer", "Celiac Disease", "Hepatitis C", "Cirrhosis", "Fatty Liver Disease", "Wilson Disease", "Non-Alcoholic Fatty Liver Disease (NAFLD)", "Pancreatic Cancer", "Gallbladder Cancer", "Bile Duct Cancer", "Throat Cancer", "Esophageal Cancer", "Stomach Cancer", "Colorectal Cancer", 
                     "Gestational Trophoblastic Disease", "Mesothelioma", "Kawasaki Disease", "Crohn's Disease", "Ulcerative Colitis", "Irritable Bowel Syndrome (IBS)", "Gastritis", "Peptic Ulcer Disease", "GERD (Gastroesophageal Reflux Disease)", "Kidney Stones", "Bladder Infections", "Glaucoma", "Cataracts", "Macular Degeneration", "Retinitis Pigmentosa", "Hearing Loss", "Tinnitus", "Meniere's Disease", "Epilepsy", "Migraine", "Schizophrenia", "Bipolar Disorder", "Depression", "Anxiety Disorders", "Obsessive-Compulsive Disorder (OCD)", "Post-Traumatic Stress Disorder (PTSD)", 
                     "ADHD (Attention-Deficit/Hyperactivity Disorder)", "Down Syndrome", "Cerebral Palsy", "Muscular Dystrophy", "Fragile X Syndrome", "Tourette Syndrome", "Williams Syndrome", "Turner Syndrome", "Klinefelter Syndrome", "Sjogren's Syndrome", "Myasthenia Gravis", "Lyme Disease", "Fibrous Dysplasia", "Marfan Syndrome", "Polycystic Kidney Disease", "Wilson's Disease", "Sarcoidosis", "Gallstones", "Hemochromatosis", "Osteoporosis", "Psoriasis", "Vitiligo", "Eczema", "Rosacea", "Acne", "Hirsutism", "Alopecia", "Vaginal Yeast Infection", "Endometriosis", "Polycystic Ovary Syndrome (PCOS)", 
                     "Premenstrual Syndrome (PMS)", "Erectile Dysfunction", "Premature Ejaculation", "Infertility", "Prostatitis", "Interstitial Cystitis", "Dermatitis", "Cellulitis", "Melanoma", "Basal Cell Carcinoma", "Kaposi's Sarcoma", "Thyroid Disorders", "Hashimoto's Thyroiditis", "Graves' Disease", "Pituitary Disorders", "Addison's Disease", "Cushing's Syndrome", "Pernicious Anemia",]

keywords_techniques = ["Spectroscopy", "Chromatography", "Mass Spectrometry", "XRD", "NMR", "SEM", "TEM", "AFM", "GC-MS", "LC-MS", "HPLC", "PCR", "Gel Electrophoresis", "MRI", "DSC", "XPS", "CD", "FTIR", "UV-Vis", "Raman Spectroscopy", "NMR", "X-ray Crystallography", "EPR", "AAS", "ICP-MS", "SIMS", "AES",  "SEM", "ESEM", "STEM"
                       "AFM", "STM", "XPS", "EDS", "EPMA", "SIMS", "TOF-SIMS", "AES", "LEED", "XRD", "SAXS", "MRI", "PET", "SPECT", "CT", "MRS", "fMRI", "DWI", "PET-CT", "X-ray Fluoroscopy", "Radiography", "Ultrasound", "PAI", "PET-CT", "XRF", "NAA", "XAS", "XES", "AES", "SPM", "LIBS", "FTMS", "CID", "MS/MS", "SERS", "EM", "SEM", "TEM",
                       "XANES", "EXAFS", "ToF-SIMS", "LA-ICP-MS", "DESI", "MALDI-MS", "ESI-MS", "GC-MS/MS", "HPLC-MS", "GC-FID", "GC-ECD", "GC-TCD", "GC-PID", "GC-NPD", "GC-MS/MS", "ICP-AES", "FTIR", "NIRS", "XRF", "EPR", "LEIS", "SXPS", "SXRD", "SAXS", "WDXRF", "SIMS", "MBE", "AES", "ISS", "SNMS", "SPM", "AFM", "STM", "TEM",]

keywords_mixed = ["Bioinformatics", "Pharmacometrics", "Biotechnology", "Immunology", "Neuroscience", "Genetics", "Xenobiology",
                  "Biology", "Physics", "Chemistry", "Material Science", "Biochemistry",
                  "Machine Learning", "Imaging", "Oncology",
                  "Python", "UNIX", "MATLAB", "SQL",
                  "PKPD", "DMPK", "PBPK",
                  "Quantum", "Genomics", "Nanotechnology", "Astrophysics", "Neuroscience", "Environmental", "Climate", "Evolution", "Ecology", "Biodiversity", "Geology", "Chemistry", "Physics", "Botany", "Zoology", "Microbiology", "Bioinformatics", "Biotechnology", "Statistics", "Fieldwork", "Observation", "Experimentation", "Data Analysis", "Hypothesis", "Genetics", "Astronomy", "Oceanography", "Geophysics", "Seismology", "Meteorology", "Climatology",  "Immunotherapy", "Bioremediation", "Environmental Microbiology", "Biofuels", "Pharmaceuticals", "Neurodegenerative", "Immunotherapies", 
                  "Hydrology", "Hydrogeology", "Aerospace", "Biomechanics", "Epidemiology", "Remote Sensing", "Ecosystems", "Genome", "Proteomics", "Metagenomics", "Nuclear", "Radiation", "Cosmology", "Astrobiology", "Particle Physics", "Nuclear Physics", "Quantum Mechanics", "Optics", "Biochemistry", "Chemical Engineering", "Material Science", "Genetic Engineering", "Stem Cells", "Microscopy", "Spectroscopy", "Neuroimaging", "X-ray", "Mass Spectrometry", "Machine Learning", "Artificial Intelligence", "Big Data", "Robotics", "Nanomaterials", "Renewable Energy", "Green Chemistry", 
                  "Cell Biology", "Neurophysiology", "Immunology", "Pharmacology", "Toxicology", "Biophysics", "Aquatic", "Terrestrial", "Atmospheric", "Marine", "Terrestrial", "Aquatic", "Ecotoxicology", "Hydroponics", "Biomarkers", "Geospatial", "Geoinformatics", "Environmental Impact", "Genetic Variation", "Phylogenetics", "Taxonomy", "Eco-evolutionary", "Microbes", "Microplastics", "Aquaponics", "Aquaculture", "Eco-Tourism", "Wildlife", "Plant Physiology", "Soil Science", "Geomorphology", "Volcanology", "Tectonics", "Geodesy", "Planetary Science", "Ornithology", "Entomology", "Herpetology", "Ichthyology", 
                  "Genome Mapping", "Structural Biology", "Cytogenetics", "Bioavailability", "Phytochemistry", "Atmospheric Chemistry", "Petrology", "Hydrogeophysics", "Remote Sensing", "Environmental Modeling", "Sustainable Development", "Ecological Restoration", "Genome Editing", "Nanomedicine", "Quantum Computing", "Astrochemistry", "Cosmic Microwave Background", "Nuclear Fusion", "Particle Accelerators", "Space Exploration", "Exoplanets", "Mars Colonization", "Astronomical Observations", "Environmental Ethics", "Conservation", "Sustainable", "Renewable", "Climate Change", "Mammalogy", "Virology",
                  "Synthetic Biology", "Greenhouse Gases", "Renewable Resources", "Hydroelectric Power", "Genetic Variation", "Environmental Health", "Eco-Conservation", "Solar Energy", "Microbiome", "DNA Sequencing", "CRISPR", "Epigenetics", "Gene Expression", "Transcriptomics"]

# Combine keywords/tags
keywords = keywords_diseases + keywords_techniques + keywords_mixed

# Add lower case versions of tags
keywords = keywords + [x.lower() for x in keywords]

# Function for getting rss feed data
def Get_RSS(URL, Limit_Hours):  # Get RSS data from URL List

    found = []

    rss_data = feedparser.parse(URL)  # Get RSS Feed Data

    for entry in rss_data.entries:  # Check all available RSS Information per URL

        parsed_date = parser.parse(entry.published).replace(
            tzinfo=None)  # Get publish date

        published_recently = datetime.now(
        ) - parsed_date < timedelta(hours=Limit_Hours)  # Check for recently

        if published_recently:

            parsed_title = entry.title.split()  # Split Title to extract Position

            # Check for PhD/Doctoral Keywords in Title
            if any(elem in titles for elem in parsed_title):

                date_published = entry.published[:len(
                    entry.published) - 5] + "(GMT'+'2)"  # Replace +0200 by GMT+2

                # Extract Keywords/Tags from Description
                parsed_summary = entry.summary

                tags = []  # Empty for next run
                # Check if tags are contained in summary
                [tags.append(keywords[i].upper()) for i in range(
                    0, len(keywords)) if keywords[i] in parsed_summary]

                tags = list(set(tags))  # Avoid duplicated Tags

                tags = ' '.join(tags)

                # Combine Title, Date, Link
                msg = entry.title + "\n" \
                    + entry.links[0].href + "\n" \
                    + "Published: " + date_published + "\n" \
                    + "Tags: " + tags

                found.append(msg)  # Save Positions in List

    return found


###############################################################
## RUN SEARCH FOR LIST OF URLS AND SPECIFIED UPDATE INTERVAL ##
###############################################################
Update_Interval_hours = 24  # 168 = 1 Week; 680 1 Month
Update_Time = "19:30"

print("PhD/Doctoral Student Position Finder Bot started.\n",
      "Update Time:", Update_Time, "\n\n")

# Analyze RSS data
def Position_Search():
    
    position_list = []

    print("Now checking", len(URLs), "URLs for positions published within the last",
          Update_Interval_hours, "hours.", "\n")

    for URL in URLs:  # Loop all provided URLs

        # Open Positions within single Institution
        found_pos = Get_RSS(URL, Update_Interval_hours)

        for positions in range(len(found_pos)):  # Loop all found positions

            # Output Title + Date + Link to Console
            print(found_pos[positions], "\n")

            #################################
            ## UNCOMMENT HERE TO BROADCAST ##
            #################################

            # Send_To_Channel(found_pos[positions])  # Output Title + Date + Link to Telegram Channel
            # sleep(4)  # Timer to avoid 30 msg/min Limit
    
            position_list.append(found_pos)

    print("All", len(position_list), "found Positions printed." "\n" "Waiting for",
          Update_Time, "to execute new search.")


# Schedule bot run
schedule.every().day.at(Update_Time).do(Position_Search)

# Keep bot running
while True:
    # print("Its running")
    schedule.run_pending()
    # print("and checking")
    time.sleep(1)  # wait
