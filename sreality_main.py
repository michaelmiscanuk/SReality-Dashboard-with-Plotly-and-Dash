#%%
from sreality_scrape import (
    get_property_links_in_Parallel,
    get_property_details_in_Parallel,
)
import pickle
import operator


def run_scraping():
    """
    DO THIS:
        Please make sure you set the display to no to turn off in Windows!!!
        Please make sure you have enough memory!!!
        Please make sure you have the latest version of the ChromeDriver!!!:
            https://sites.google.com/a/chromium.org/chromedriver/downloads
        Add path to the folder containing ChromeDriver to PATH System Enviromental Variables.
        Install: pip install selenium
    """

    # global property_data_list_of_dicts, property_links_list

    ########################################################################################
    # Parametrize the property filtering
    advertising_type = "to-rent"
    property_kind = "apartments"
    district = "praha"

    property_type = ""

    min_price = 0
    max_price = 15000

    num_of_pages = 220

    ########################################################################################
    # Get all the Property Links in a List by Calling Paralellized Function
    # Use variable above to parametrize input
    property_links_list = get_property_links_in_Parallel(
        num_of_pages=num_of_pages,
        advertising_type=advertising_type,
        property_kind=property_kind,
        district=district,
        property_type=property_type,
        min_price=min_price,
        max_price=max_price,
    )

    #%%
    # Pickle List with Links to Properties to Disk
    # property_links_list.to_pickle("property_links_list.pkl")
    with open("property_links_list.pkl", "wb") as b:
        pickle.dump(property_links_list, b)

    # Load Back Property Links
    # import pickle
    # with open('property_links_list.pkl', 'rb') as b:
    #     property_links_list = pickle.load(b)

    #%%
    ########################################################################################
    # Go over all the links to Individual Properties in Parallelized manner
    # result will be a List of Dictionaries. One dict for one individual property
    property_data_list_of_dicts = get_property_details_in_Parallel(
        property_links_list=property_links_list
    )

    # print(property_data_list_of_dicts)
    #%%
    # Pickle to Disk
    with open("property_data_list_of_dicts.pkl", "wb") as b:
        pickle.dump(property_data_list_of_dicts, b)

    # Load Back Property Data
    # with open('property_data_list_of_dicts.pkl', 'rb') as b:
    #     property_data_list_of_dicts = pickle.load(b)


def process_additional(x=5):
    """
    If for some reason there was en error in processing, it will go to the List as None
    This function will loop and process unprocessed properties again,
    so we have as much processed as possible.
    """

    try:
        # Load Back Property Links
        # import pickle
        with open("property_links_list.pkl", "rb") as b:
            property_links_list = pickle.load(b)

        # Load Back Property Data
        with open("property_data_list_of_dicts.pkl", "rb") as b:
            property_data_list_of_dicts = pickle.load(b)

        for _ in range(x):
            # Get Indexes That contains None in List of Dicts (That were not processed correctly)
            not_processed_link_positions = [
                i for i, x in enumerate(property_data_list_of_dicts) if x == None
            ]

            if len(not_processed_link_positions) > 0:
                #%%
                # Get Links to the Not Processed Properties
                indices = not_processed_link_positions
                property_links_not_processed_list = list(
                    operator.itemgetter(*indices)(property_links_list)
                )

                # Here we remove the None values
                property_data_list_of_dicts = [
                    i for i in property_data_list_of_dicts if i
                ]

                #%%
                # Process Properties that were not processed before
                property_data_additional_list_of_dicts = (
                    get_property_details_in_Parallel(
                        property_links_list=property_links_not_processed_list
                    )
                )

                #%%
                # Merging Lists
                property_data_list_of_dicts.extend(
                    property_data_additional_list_of_dicts
                )
                #%%

                # Pickle to Disk
                with open("property_data_list_of_dicts.pkl", "wb") as b:
                    pickle.dump(property_data_list_of_dicts, b)
    except Exception as e:
        print(e)  # For Debug
        # pass # Production


if __name__ == "__main__":
    run_scraping()
    process_additional()
