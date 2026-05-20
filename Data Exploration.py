import pandas as pd
import numpy as np
import matplotlib as mp
import seaborn as sb
import pycountry
import pycountry_convert as pc 
import matplotlib.pyplot as plt 

prodind = "FAO_PIN_Merged.csv"
pdid = pd.read_csv(prodind)

del pdid['element_code']
headers = ["Region", "Production", "Year", "Unit", "Price", "Category"]
pdid.columns = headers

pdid.replace("?", np.nan, inplace=True)
pdid.dropna(inplace=True)

pdid["Year"] = pdid["Year"].astype("object")
pdid["Price"] = pd.to_numeric(pdid["Price"], errors='coerce').astype("int64")

pdid["Production"] = pdid["Production"].replace(
    "Gross Production Index Number (2014-2016 = 100)", 
    "Gross PIN"
)
pdid["Production"] = pdid["Production"].replace(
    "Gross per capita Production Index Number (2014-2016 = 100)", 
    "Gross per capita PIN"
)

pdid1 = pdid.drop(pdid[pdid['Production'] != 'Gross PIN'].index)
pdid2 = pdid1.drop(pdid1[pdid1['Category'] != 'Agri_PIN'].index)

def get_continent_improved(country_name):
    try:
        country = pycountry.countries.search_fuzzy(country_name)[0]
        country_alpha2 = country.alpha_2
        country_continent = pc.country_alpha2_to_continent_code(country_alpha2)
        return pc.convert_continent_code_to_continent_name(country_continent)
    except:
        return country_name

pdid2['Region_Group'] = pdid2['Region'].apply(get_continent_improved)

gross_agri_region = pdid2.groupby('Region_Group')['Price'].sum()
print(gross_agri_region)

gross_agri_prod2 = pdid2.pivot_table(
    index='Region_Group', 
    columns='Year', 
    values='Price', 
    aggfunc='sum'
)

gross_agri_prod2.columns = gross_agri_prod2.columns.astype(str)
years = list(map(str, range(1961, 2022)))
gap = gross_agri_prod2
gap['Total'] = gap.sum(axis=1)
gap.sort_values(['Total'], ascending=False, axis=0, inplace=True)
gap = gap[years].transpose()
gap.fillna(0, inplace=True)
print(gap.head())

plt.figure(figsize=(14, 6))
gap.plot(figsize=(14, 6))
plt.title('Gross Agricultural Production Index by Region (1961-2021)')
plt.xlabel('Year')
plt.ylabel('Price Index')
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()