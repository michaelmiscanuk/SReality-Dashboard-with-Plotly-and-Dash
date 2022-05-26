# %%
from bs4 import BeautifulSoup
from time import time, sleep
import unidecode
from selenium import webdriver
from joblib import Parallel, delayed
import multiprocessing
import itertools
from tqdm import tqdm
import pickle
from functools import wraps
import re
from selenium.common.exceptions import WebDriverException
import datetime


# Helping Functions
def render_page(url):
    '''
        selenium.webdriver.Chrome():
            Rendering page using selenium.webdriver.Chrome()
            Get Chrome WebDriver here - https://sites.google.com/chromium.org/driver/
            Add path to the folder containing it to PATH System Enviromental Variables.
            Install: pip install selenium
    '''
    # This section will disable images in Chrome
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.keys import Keys
    chromedrive_path = 'd:/Programs Full/chromedriver_win32/chromedriver.exe'

    service = webdriver.chrome.service.Service(chromedrive_path)
    service.start()
    chrome_options = Options()

    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument('--lang=en_US') 
    chrome_options.headless = True

    driver = webdriver.Remote(service.service_url, desired_capabilities=chrome_options.to_capabilities())

    try:
        driver.get(url)
        sleep(1)
        r = driver.page_source
        #driver.quit()
        return r
    except WebDriverException:
        print("page down") 

def list_to_dict(rlist):
    '''
        Convert colon separated list of strings into a dict
        Split only on first occurence of :, because there can be dates with : in time.
    '''
    return dict(map(lambda s : s.split(':', 1), rlist))


def speed_test(fn):
    '''
        Wrapper for Speed Test Functions
    '''
    @wraps(fn)
    def wrapper(*args, **kwargs):
        start_time = time()
        result = fn(*args, **kwargs)
        end_time = time()
        print(f"Executing {fn.__name__}")
        print(f"Time Elapsed: {end_time - start_time}")
        return result
    return wrapper


def unique_values_df_to_excel(df, excel_name, transpose): 
    '''
        Simple function to make excel containing Unique values for each column.
        All Unique Values are in one cell as values enclosed in ''
        In Excel - Select all Columns and use Wrap Text for easier examination.    

        Example:
        unique_values_df_to_excel(property_data_dataframe, "property_data_dataframe_5", True)    
    '''
    if transpose == True:
        if excel_name.endswith(".xlsx"):
            df.apply(lambda x: [x.unique()]).T.to_excel(excel_name)
        else:
            df.apply(lambda x: [x.unique()]).T.to_excel(f"{excel_name}.xlsx")
    else:
        if excel_name.endswith(".xlsx"):
            df.apply(lambda x: [x.unique()]).to_excel(excel_name)
        else:
            df.apply(lambda x: [x.unique()]).to_excel(f"{excel_name}.xlsx")


def get_property_links( page = 1, advertising_type = "to-rent", property_kind = "apartments", 
                        district = "praha", property_type = "4+kt,4+1", min_price = 0, max_price = 20000): 
    '''
        Returns all the Links to the Individual Properties from one filtered page, which contains up to 20 links to Individual Properies.

        Attributes:

            advertising_type: Type of Advertisement. Possible values:
                "for-sale", "to-rent", "auction"

            property_kind: Available values:
                "apartments", "houses", "lands", "commercial-properties", "other-real-estates"

            district: e.g. "praha", "stredocesky-kraj" etc.

            property_type: Possible values are something like: 
                "2+kt,2+1,3+kt,3+1,4+kt,4+1" #'1+1' # "2+kt,2+1" #"1+1,1+kt" # "2+kt,2+1,3+kt,3+1,4+kt,4+1"
                "" for all types.
                DONT USE SPACEs; input type of property in this format - "1+1,1+kt"; kt stands for kitchen

            page - which page in a filtered result to go to to get links to Individual Properties 
                (can be looped using Parallel function to get all the pages)

            min_price - minimum price for filter

            max_price - maximum price for filter
    '''

    property_type = str.replace(property_type, "+", "%2B")

    # Base Links, to build other links by appending the relative link.
    base_link = "https://www.sreality.cz/"

    # Page with one list of properites (there are many pages like this, each contains 20 properies)
    base_page_response = (f"https://www.sreality.cz/en/search/{advertising_type}/{property_kind}/{district}?disposition={property_type}&min-price={min_price}&max-price={max_price}&page={page}")
    print(base_page_response)
    # Regnder website using selenium.webdriver.Chrome(), which will open the page and let it load all the data.
    # See docstring for instalation
    r = render_page(base_page_response)

    # Parse the rendered page using BeautifulSoup to get the HTML Page
    soup = BeautifulSoup(r, "html.parser")

    ###########################################################################
    ### Gather all links to individual properties and make a List ###
    property_links_on_one_page = [base_link + i.parent.attrs['href'] for i in soup.select(".ng-scope+ .ng-scope .name")][2:-1] 
    
    return property_links_on_one_page


def get_property_links_in_Parallel(num_of_pages, advertising_type, property_kind, district, property_type, min_price, max_price):
    '''
        Run get_property_links() in Parallel using joblib.Parallel
        Using tqdm to see progress bar.
        
        Arguments:
            num_of_pages - Number of Pages to go through in a filtered result.
                We dont know the maximum number of pages. It will go through the page even if it contains no links
                to Individual Properties. Those will be in empty list, and after flattening will dissapear.
                Set it sufficiently high, but not much, because pages have to be loaded by selenium.webdriver.Chrome()
                Can be approximated by going to the website, 
                    applying same filter
                    below see how many properties will be displayed, 
                    divide by 20, 
                    round up to get the number of pages.
            property_type - the type of a flat, like 2+kt stands for 2 rooms and shared kitchen in one of the rooms.
                can be input as a string separated by comma for more types (Don't use Space)
            min_price - minimum price for filter
            max_price - maximum price for filter
    '''
    cpus = multiprocessing.cpu_count()
    property_links_list_of_lists = Parallel(n_jobs=cpus)(delayed(get_property_links)(
                                                                        page=i, 
                                                                        advertising_type = advertising_type,
                                                                        property_kind = property_kind,
                                                                        district = district,
                                                                        property_type = property_type,                                                                        
                                                                        min_price = min_price, 
                                                                        max_price = max_price) 
                                                                            for i in tqdm(range(1, num_of_pages + 1))
                                                                    )
    # Flatten the List of Lists
    property_links_list_flattened = list(itertools.chain(*property_links_list_of_lists))

    return property_links_list_flattened


def get_property_details(property_link = ''):
    '''
        Input a property link and it will scrape the page with property info.
        Output is one dictionary containing data for one property.
    '''

    try:
        r = render_page(property_link)
        soup = BeautifulSoup(r, "html.parser")


        ###########################################################################
        ### UPPER Section with Property Attributes - Attributes of Property itself ###
        property_items_upper_list = []
        for property_item in soup.select(".param"):
            if 'icon-ok' not in str(property_item) and 'icon-cross' not in str(property_item):
                property_items_upper_list.append(unidecode.unidecode(property_item.get_text().strip()))
            elif 'icon-ok' in str(property_item) and 'icon-cross' not in str(property_item):
                property_items_upper_list.append(f"{unidecode.unidecode(property_item.get_text().strip())}:1")
            elif 'icon-ok' not in str(property_item) and 'icon-cross' in str(property_item):
                property_items_upper_list.append(f"{unidecode.unidecode(property_item.get_text().strip())}:0")


        property_items_upper_cleaned_list = []
        for i in property_items_upper_list:
            property_items_upper_cleaned_list.append(i.replace('\n', '').replace('::', ':'))

        property_items_upper_dict = list_to_dict(property_items_upper_cleaned_list)

        property_items_upper_cleaned_dict = {k.replace(" ", "_"):v 
                                                for k,v in property_items_upper_dict.items()}


        ###########################################################################
        ### BOTTOM Section with Property Attributes - Attributes of Distances from surrounding Area ###
        sur_area_keys_list = []
        for property_item in soup.select(".clear.ng-scope"):
            my_key = (property_item.get_text().strip().split(":")[0])
            sur_area_keys_list.append(my_key)

        distances_list = []
        for i in soup.select(".c-pois__distance"):
            distance_in_par = i.get_text().strip()
            # distance = distance_in_par[distance_in_par.find("(")+1:distance_in_par.find(")")].split(' ')[0] 
            distance = ''.join(distance_in_par.split()).replace("m", "").replace("(","").replace(")","")
            distances_list.append(distance)

        property_items_bottom_cleaned_dict = dict(zip(sur_area_keys_list,distances_list))
        property_items_bottom_cleaned_dict


        ###########################################################################
        ### OTHER Property Attributes ###
        address = dict(("Address", i.get_text()) for i in soup.select(".location-text"))
        energy_efficiency_rating = dict(("Energy_Efficiency_Rating", i.get_text()) for i in soup.select(".energy-efficiency-rating__type"))
        estate_agency = dict(("Estate_Agency", i.get_text()) for i in soup.select(".line.name"))
        property_link = dict([("Property_Link",property_link)])


        # Get Advertisiment Type
        property_title = unidecode.unidecode(soup.select(".property-title .name")[0].get_text())
        pattern = re.compile("\d")
        match = pattern.search(property_title)

        property_status_string = property_title[:match.start()][:-1]
        advertising_type = {"Advertising_Type": f"{property_status_string}"}


        # Get Property Type
        try:
            property_type_string_in_dict = soup.select(".buttons")[0].attrs['data-dot-data']
            property_type_string = eval(property_type_string_in_dict)['velikost']
        except Exception as e:
            property_type_string = ''

        property_type = {"Property_Type": property_type_string}
        

        # Image
        image_link = soup.findAll(attrs={'src' : re.compile("d18")})[0].attrs['src']
        image = dict(Image = image_link)


        # Reload Time
        reload_date_time = {"Reload_Date_Time": datetime.datetime.now()}
        # reload_time = {"Reload_Time": str(datetime.datetime.now().time().strftime("%H:%M"))}


        ###########################################################################
        ### Merge Dictionaries ###
        property_data_dict = {  **property_items_upper_cleaned_dict, 
                                **property_items_bottom_cleaned_dict, 
                                **address,
                                **energy_efficiency_rating,
                                **estate_agency,
                                **property_link,
                                **property_type,
                                **advertising_type,
                                **image,
                                **reload_date_time
                            }
        return property_data_dict

    except Exception as e:
        print(e) # For Debug
        # pass # Production




def get_property_details_in_Parallel(property_links_list):
    '''
        Run get_property_details() in Parallel using joblib.Parallel
        Using tqdm to see progress bar.
        
        Arguments: property_links_list - links to Individual Properties
    '''
    cpus = multiprocessing.cpu_count()
    property_data_list_of_dicts = Parallel(n_jobs=cpus)(delayed(get_property_details)(
                                                                        property_link=i) 
                                                                            for i in tqdm(property_links_list)
                                                                    )

    return property_data_list_of_dicts



# %%
# DEBUG
# l = 'https://www.sreality.cz/en/detail/prodej/byt/2+kk/praha-hlubocepy-werichova/617000284#img=0&fullscreen=false'
# a = get_property_details(l)
# a
# %%

# %%

# %%

# %%

# %%
