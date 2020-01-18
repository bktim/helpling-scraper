from scipy import stats
from sklearn import linear_model
from textblob import TextBlob
from collections import Counter
import seaborn as sns
import matplotlib.pyplot as plt
import statsmodels.formula.api as sm
import pandas as pd
import re
import enchant

def boxplot_for_gender_pay(candidates):
    plt.figure()
    candidates["presumed_gender"] = candidates.apply(_determine_gender, axis = 1)
    sns.boxplot(x="presumed_gender", y="price_per_hour", showfliers=False, showmeans=True, data=candidates)

def scatter_plot_with_linear_predictor(candidates, attribute, dependent_attribute):
    plt.figure()
    plt.scatter(candidates[attribute], candidates[dependent_attribute])
    variable = pd.DataFrame(candidates[attribute])
    dependent_variable = pd.DataFrame(candidates[dependent_attribute])
    lm.fit(variable, dependent_variable)
    plt.plot(variable, lm.predict(variable), color='red')
    plt.xlabel(attribute)
    plt.ylabel(dependent_attribute)

def ttest_for_gender_pay_gap(candidates):
    candidates["presumed_gender"] = candidates.apply(_determine_gender, axis = 1)
    male_candidates = candidates.loc[candidates["presumed_gender"] == 0]
    female_candidates = candidates.loc[candidates["presumed_gender"] == 1]
    t2, p2 = stats.ttest_ind(female_candidates["price_per_hour"], male_candidates["price_per_hour"])
    print(t2)
    print(p2)
    print(female_candidates["price_per_hour"].mean())
    print(male_candidates["price_per_hour"].mean())

def ttest_for_experience(candidates, cleaning_count_level = 100):
    experienced_candidates = candidates.loc[candidates["performed_cleanings_count"] > cleaning_count_level]
    less_experienced_candidates = candidates.loc[candidates["performed_cleanings_count"] <= cleaning_count_level]
    t2, p2 = stats.ttest_ind(experienced_candidates["price_per_hour"], less_experienced_candidates["price_per_hour"])
    print(t2)
    print(p2)
    print(experienced_candidates["price_per_hour"].mean())
    print(less_experienced_candidates["price_per_hour"].mean())

# def analyse_postcode(candidates):
    # postcodes = pd.read_csv("postcodes_with_population_density.csv", sep=',', header=1, names=["population_density", "postcode"])
    # postcodes["postcode"] = pd.to_numeric(postcodes["postcode"], downcast='integer')
    # print(candidates.sort_values(by=["postcode"]))
    # candidates_w_population_density = pd.merge(candidates, postcodes, how="left", on="postcode") #.sort_values(by=["postcode"])
    # print(candidates_w_population_density)
    # candidates_w_population_density["population_density"] = candidates_w_population_density["population_density"].interpolate(method='nearest')
    # candidates_w_population_density = candidates_w_population_density.loc[candidates_w_population_density["population_density"].isnull()]
    # plt.scatter(candidates["price_per_hour"], candidates["postcode"])

def _clean_up_postcode_data(file_name):
    plz = pd.read_csv(file_name, sep=',', header=None, names=["population_density", "postcode"])
    plz = plz.dropna()
    plz["population_density"] = plz["population_density"].str.replace(" ","")
    plz["population_density"] = pd.to_numeric(plz["population_density"])
    plz = plz.sort_values(by=["postcode"])
    plz.to_csv("postcodes_with_population_density.csv", sep=',', index=False, header=1)

def _determine_gender(candidate):
    if "avatar_her" in candidate["default_profile_image"]:
        return 1
    else:
        return 0

def _determine_grammar_mistakes(candidate):
    tool = enchant.Dict("en_US")
    matches = 0
    for word in candidate["experience_description"].split():
        word = re.sub('[^A-Za-z]+', '', word)
        if not tool.check(word):
            matches += matches
            print(word)
    return matches

def _determine_offer_language(candidate):
    b = TextBlob(candidate["experience_description"])
    l = "unknown"
    if len(candidate["experience_description"]) > 2:
        print("###")
        l = b.detect_language()
    print(l)
    return l
    
def extract_candidates(file_name):
    entries = pd.read_csv(file_name, sep=',', header=1, names=["candidate_id", "postcode", "date", "firstname", "price_per_hour", "avg_rating", "shortname", "default_profile_image", "pets", "windows", "ironing", "ratings_received_count", "verification_level", "documents", "language_skills", "instabook_enabled", "performed_cleanings_count", "experience_description", "experience_headline", "created_at"])
    candidates = entries.drop_duplicates(subset="candidate_id", keep="first", inplace=False).reset_index(drop=True)
    candidates = candidates.loc[candidates["performed_cleanings_count"] > 0]
    candidates["presumed_gender"] = candidates.apply(_determine_gender, axis = 1)
    return candidates

def add_language_attributes(candidates):
    candidates = candidates.dropna(subset=["experience_description"])
    candidates["offer_language"] = candidates.apply(_determine_offer_language, axis = 1)
    candidates["offer_grammar_mistakes"] = candidates.apply(_determine_grammar_mistakes, axis = 1)
    return candidates
 

########################## Data Extraction ##########################
candidates = extract_candidates("entries_export.csv")

####################### Significance Testing #########################
ttest_for_gender_pay_gap(candidates)
ttest_for_experience(candidates)

################### Regression Analysis: OLS Test 1 ###################
result = sm.ols(formula="price_per_hour ~ avg_rating + presumed_gender + ratings_received_count + performed_cleanings_count", data=candidates).fit()
print(result.params)
print(result.summary())

################### Regression Analysis: OLS Test 2 ###################
variables = pd.DataFrame(candidates[["avg_rating", "presumed_gender", "ratings_received_count", "performed_cleanings_count"]])
dependent_variable = pd.DataFrame(candidates["price_per_hour"])

lm = linear_model.LinearRegression()
lm.fit(variables, dependent_variable)
print(lm.coef_) 

########################## Visualization ############################
boxplot_for_gender_pay(candidates)

rated_candidates = candidates.loc[candidates["avg_rating"] != 0]
scatter_plot_with_linear_predictor(rated_candidates, "avg_rating", "price_per_hour")

scatter_plot_with_linear_predictor(candidates, "performed_cleanings_count", "price_per_hour")

plt.show()


################### WIP / Playground ###################

# east = pd.DataFrame(candidates.loc[candidates["postcode"] < 10000])
# south = pd.DataFrame(candidates.loc[candidates["postcode"].between(70000, 90000)])
# print(south)

# ttest_for_gender_pay_gap(east)
# boxplot_for_gender_pay(east)
# ttest_for_gender_pay_gap(south)
# boxplot_for_gender_pay(south)


# t2, p2 = stats.ttest_ind(east["price_per_hour"], south["price_per_hour"])
# print(t2)
# print(p2)
# print(east["price_per_hour"].mean())
# print(south["price_per_hour"].mean())

# print(Counter(candidates["candidate_id"].values))   
# z = candidates.loc[candidates["candidate_id"] == 347915]
# print(z[["candidate_id", "price_per_hour", "performed_cleanings_count"]].sort_values(by=["price_per_hour"]))
