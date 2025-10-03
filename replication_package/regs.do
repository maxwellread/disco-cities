cd //set working directory here

use "data\city_panel.dta", clear

///////////////SETUP//////////////////
cap drop start_year
gen start_year = substr(period, 1, 4)
destring start_year, replace

egen city_total = total(num_master_ids), by(city)
encode city, gen(city_id)
drop if mod(start_year, 10) == 5 //ALTER THIS BETWEEN 5 AND 0 TO ADJUST THE DECADE AND OFF-DECADE - keep at mod(start_year, 10) == 5 for normal specification
egen epoch = group(start_year)

//drop if city_total > 2000

duplicates drop


cap drop share*
foreach genre in Electronic Hip_Hop Funk___Soul Rock Reggae Pop Stage___Screen Jazz Classical Non_Music ///
                   Folk__World____Country Blues Latin Brass___Military Children_s {
    gen share_`genre' = `genre'_total / count
}

xtset city_id epoch
gen ln_num_master_ids = ln(num_master_ids)


gen ln_avg_taddy     = ln(avg_taddy)
gen ln_taddy_p75     = ln(taddy_p75)
gen ln_taddy_p90     = ln(taddy_p90)
gen ln_taddy_p95     = ln(taddy_p95)
gen ln_first_release_taddy = ln(avg_first_release)

lab var ln_avg_taddy "Avg. Innovation Score (log)"
lab var ln_taddy_p75  "Innovation Score - 75th percentile (log)"
lab var ln_taddy_p90   "Innovation Score - 90th percentile (log)"
lab var ln_taddy_p95   "Innovation Score - 95th percentile (log)"
lab var ln_first_release_taddy "Avg. Innovation Score of First Releases (log)"


//VAR LABELS
lab var num_master_ids "Total Albums"
lab var avg_taddy "Average Innovation Scores"
lab var taddy_p75 "Innovation Score at 75th Percentile"
lab var taddy_p90 "Innovation Score at 90th Percentile"
lab var taddy_p95 "Innovation Score at 95th Percentile"

lab var centrality "Centrality"
lab var density "Network Density"
lab var entropy "Network Entropy"
lab var num_nodes "Number of Nodes"

lab var releases_per_master_mean "Average Releases per Master"
lab var releases_per_master_median "Median Releases per Master"
lab var releases_per_master_25th "Releases per Master - 25th Percentile"
lab var releases_per_master_75th "Releases per Master - 75th Percentile"
lab var releases_per_master_90th "Releases per Master - 90th Percentile"


/*
sort start_year
gen lag_num_master_ids = L1.num_master_ids
bysort start_year: reg avg_taddy lag_num_master_ids share*
*/

/////////////////MAIN REGRESSIONS - SUMMARY////////////////////
xtreg avg_taddy centrality share*, fe cluster(city)
xtreg avg_taddy L.num_master_ids share*, fe cluster(city)
xtreg avg_taddy density share*, fe cluster(city)
xtreg avg_taddy entropy share*, fe cluster(city)
xtreg avg_taddy genre_hhi, fe cluster(city)


xtreg avg_taddy L.num_master_ids share*, fe
xtreg taddy_p75 L.num_master_ids share*, fe
xtreg taddy_p95 L.num_master_ids share*, fe

xtreg avg_taddy L.centrality share*, fe
xtreg taddy_p75 L.centrality share*, fe
xtreg taddy_p95 L.centrality share*, fe

xtreg avg_taddy L.density L.num_master_ids share*, fe
xtreg taddy_p75 L.density L.num_master_ids share*, fe
xtreg taddy_p95 L.density L.num_master_ids share*, fe

xtreg avg_taddy L.entropy L.num_master_ids share*, fe
xtreg taddy_p75 L.entropy L.num_master_ids share*, fe
xtreg taddy_p90 L.entropy L.num_master_ids share*, fe


xtreg releases_per_master_mean L.num_master_ids share*, fe
xtreg releases_per_master_25th L.num_master_ids share*, fe
xtreg releases_per_master_75th L.num_master_ids share*, fe
xtreg releases_per_master_90th L.num_master_ids share*, fe

xtreg releases_per_master_mean L.centrality share*, fe
xtreg releases_per_master_25th L.centrality share*, fe
xtreg releases_per_master_75th L.centrality share*, fe
xtreg releases_per_master_90th L.centrality share*, fe


xtreg avg_taddy genre_hhi L.genre_hhi L.num_master_ids, fe
xtreg avg_taddy genre_hhi L.genre_hhi L.num_master_ids, fe
xtreg taddy_p75 genre_hhi L.genre_hhi L.num_master_ids, fe
xtreg taddy_p90 genre_hhi L.genre_hhi L.num_master_ids, fe



//TESTS THE WHOLE SAMPLE  WITH NO FILTERING - NUM_MASTER_IDS ONLY AVAILABLE FOR MAIN SAMPLE, COUNT AVAILABLE FOR ALL
xtreg avg_taddy L.count share*, fe cluster(city)
xtreg taddy_p75 L.count share*, fe cluster(city)
xtreg taddy_p90 L.count share*, fe cluster(city)

////////////PRECISE ELASTICITIES/////////////
estimates clear

xtreg ln_first_release_taddy L.ln_num_master_ids share*, fe cluster(city)
eststo reg_fr
estadd local genre_controls "Yes"

xtreg ln_avg_taddy L.ln_num_master_ids share*, fe cluster(city)
eststo reg_avg
estadd local genre_controls "Yes"

xtreg ln_taddy_p75 L.ln_num_master_ids share*, fe cluster(city)
eststo reg_75
estadd local genre_controls "Yes"

xtreg ln_taddy_p95 L.ln_num_master_ids share*, fe cluster(city)
eststo reg_95
estadd local genre_controls "Yes"

esttab reg_* using "output\tables\taddy_elasticities_baseline.tex", ///
    replace label se star(* 0.10 ** 0.05 *** 0.01) ///
    title(Regression Results) ///
    alignment(D{.}{.}{-1}) ///
    drop(share*) ///
    varlabels(_cons Constant L.ln_num_master_ids "Lagged log # Albums") ///
    nonumber compress booktabs ///
    stats(genre_controls N r2, labels("Genre Controls" "Observations" "R-squared")) ///
    addnotes("Fixed effects included", "Standard errors in parentheses")
	

	
////////////CENTRALITY ANALYSIS//////////
estimates clear

preserve
keep if num_master_ids != . ///centrality exists across sample - isolate sample only

gen ln_forward = ln(avg_forward)
gen ln_backward = ln(avg_backward)
lab var ln_forward "Avg. Forward Similarity (log)"
lab var ln_backward "Avg. Backward Similarity (log)"


xtreg ln_avg_taddy L.centrality share*, fe cluster(city)
eststo c_reg_avg1
estadd local genre_controls "Yes"

xtreg ln_first_release_taddy L.centrality L.num_master_ids share*, fe cluster(city)
eststo c_reg_fr
estadd local genre_controls "Yes"

xtreg ln_avg_taddy L.centrality L.num_master_ids share*, fe cluster(city)
eststo c_reg_avg
estadd local genre_controls "Yes"

xtreg ln_forward L.centrality L.num_master_ids share*, fe cluster(city)
eststo c_reg_75
estadd local genre_controls "Yes"

xtreg ln_backward L.centrality L.num_master_ids share*, fe cluster(city)
eststo c_reg_95
estadd local genre_controls "Yes"

esttab c_reg_* using "output\tables\centrality.tex", ///
    replace label se star(* 0.10 ** 0.05 *** 0.01) ///
    title(Regression Results) ///
    alignment(D{.}{.}{-1}) ///
    drop(share*) ///
    varlabels(_cons Constant L.ln_num_master_ids "Lagged Centrality") ///
    nonumber compress booktabs ///
    stats(genre_controls N r2, labels("Genre Controls" "Observations" "R-squared")) ///
    addnotes("Fixed effects included", "Standard errors in parentheses")
	
restore	

/////////////DENSITY TABLE//////////////
estimates clear

reg avg_taddy density, r
eststo den_avg0
estadd local genre_controls "No"

xtreg avg_taddy L.density L.num_master_ids share*, fe cluster(city)
eststo den_avg1
estadd local genre_controls "Yes"

xtreg avg_taddy L.density num_nodes L.num_master_ids share*, fe cluster(city)
eststo den_avg2
estadd local genre_controls "Yes"

xtreg avg_taddy L.density num_nodes num_master_ids share*, fe cluster(city)
eststo den_avg3
estadd local genre_controls "Yes"

xtreg taddy_p75 L.density L.num_master_ids share*, fe cluster(city)
eststo den_75
estadd local genre_controls "Yes"

xtreg taddy_p95 L.density L.num_master_ids share*, fe cluster(city)
eststo den_95
estadd local genre_controls "Yes"

esttab den_avg* using "output\tables\density_baseline.tex", ///
    replace label se star(* 0.10 ** 0.05 *** 0.01) ///
    title(Regression Results) ///
    alignment(D{.}{.}{-1}) ///
    drop(share*) ///
    varlabels(_cons Constant L.ln_num_master_ids "Lagged Network Density") ///
    nonumber compress booktabs ///
    stats(genre_controls N r2, labels("Genre Controls" "Observations" "R-squared")) ///
    addnotes("Fixed effects included", "Standard errors in parentheses")


//////////////////COEFPLOT OF RELEASES_PER_MASTER//////////////////

* Original regressions (Lagged)
xtreg releases_per_master_25th L.num_master_ids share*, fe cluster(city)
eststo rpm1

xtreg releases_per_master_median L.num_master_ids share*, fe cluster(city)
eststo rpm2

xtreg releases_per_master_75th L.num_master_ids share*, fe cluster(city)
eststo rpm3

xtreg releases_per_master_90th L.num_master_ids share*, fe cluster(city)
eststo rpm4

*non-lagged
xtreg releases_per_master_25th num_master_ids share*, fe cluster(city)
eststo rpm1_nolag

xtreg releases_per_master_median num_master_ids share*, fe cluster(city)
eststo rpm2_nolag

xtreg releases_per_master_75th num_master_ids share*, fe cluster(city)
eststo rpm3_nolag

xtreg releases_per_master_90th num_master_ids share*, fe cluster(city)
eststo rpm4_nolag


coefplot ///
    (rpm1, label("25th (Lagged)") keep(L.num_master_ids)) ///
    (rpm1_nolag, label("25th (Current)") keep(num_master_ids)) ///
    (rpm2, label("Median (Lagged)") keep(L.num_master_ids)) ///
    (rpm2_nolag, label("Median (Current)") keep(num_master_ids)) ///
    (rpm3, label("75th (Lagged)") keep(L.num_master_ids)) ///
    (rpm3_nolag, label("75th (Current)") keep(num_master_ids)) ///
    (rpm4, label("90th (Lagged)") keep(L.num_master_ids)) ///
    (rpm4_nolag, label("90th (Current)") keep(num_master_ids)), ///
    drop(_cons share*) ///
    yline(0, lpattern(dash)) ///
    vertical ///
    note("Genre controls and fixed effects included") ///
    scheme(s1color)
	


//////////ROBUSTNESS - DROP SATELLITE CITES AND CORE CITIES///////////
preserve
drop if city == "Paterson" | city == "Newark" | city == "Evanston" | city == "Pasadena2" | ///
       city == "Irvine" | city == "Oakland" | city == "Alexandria2" | city == "Berkeley" | ///
     city == "Versailles" | city == "San Jose3" | city == "San Mateo"
   
drop if city == "New York" | city == "Los Angeles" | city == "San Francisco" | city == "Paris" | ///
       city == "Chicago" 

	   
xtreg ln_first_release_taddy L.ln_num_master_ids share*, fe
xtreg ln_avg_taddy L.ln_num_master_ids share*, fe
xtreg ln_taddy_p75 L.ln_num_master_ids share*, fe
xtreg ln_taddy_p95 L.ln_num_master_ids share*, fe


xtreg ln_first_release_taddy L.ln_num_master_ids share*, fe
eststo reg_fr
estadd local genre_controls "Yes"

xtreg ln_avg_taddy L.ln_num_master_ids share*, fe
eststo reg_avg
estadd local genre_controls "Yes"

xtreg ln_taddy_p75 L.ln_num_master_ids share*, fe
eststo reg_75
estadd local genre_controls "Yes"

xtreg ln_taddy_p95 L.ln_num_master_ids share*, fe
eststo reg_95
estadd local genre_controls "Yes"

esttab reg_* using "output\tables\taddy_elasticities_no_sats.tex", ///
    replace label se star(* 0.10 ** 0.05 *** 0.01) ///
    title(Regression Results) ///
    alignment(D{.}{.}{-1}) ///
    drop(share*) ///
    varlabels(_cons Constant L.ln_num_master_ids "Lagged log(Albums)") ///
    nonumber compress booktabs ///
    stats(genre_controls N r2, labels("Genre Controls" "Observations" "R-squared")) ///
    addnotes("Fixed effects included", "Standard errors in parentheses")
	


xtreg ln_first_release_taddy L.ln_num_master_ids share*, fe
xtreg ln_taddy_p75 L.ln_num_master_ids avg_first_release share*, fe
xtreg ln_taddy_p95 L.ln_num_master_ids avg_first_release  share*, fe


/////////////DENSITY TABLE - SATELLITE CITIES//////////////
reg avg_taddy density, r
eststo den_avg0
estadd local genre_controls "No"

xtreg avg_taddy L.density L.num_master_ids share*, fe cluster(city)
eststo den_avg1
estadd local genre_controls "Yes"

xtreg avg_taddy L.density num_nodes L.num_master_ids share*, fe cluster(city)
eststo den_avg2
estadd local genre_controls "Yes"

xtreg avg_taddy L.density num_nodes num_master_ids share*, fe cluster(city)
eststo den_avg3
estadd local genre_controls "Yes"

xtreg taddy_p75 L.density L.num_master_ids share*, fe cluster(city)
eststo den_75
estadd local genre_controls "Yes"

xtreg taddy_p95 L.density L.num_master_ids share*, fe cluster(city)
eststo den_95
estadd local genre_controls "Yes"

esttab den_avg* using "output\tables\density_nosats.tex", ///
    replace label se star(* 0.10 ** 0.05 *** 0.01) ///
    title(Regression Results) ///
    alignment(D{.}{.}{-1}) ///
    drop(share*) ///
    varlabels(_cons Constant L.ln_num_master_ids "Lagged Network Density") ///
    nonumber compress booktabs ///
    stats(genre_controls N r2, labels("Genre Controls" "Observations" "R-squared")) ///
    addnotes("Fixed effects included", "Standard errors in parentheses")


restore

cap xtset city_id epoch

///////////////////ANALYSIS ON US CITIES ONLY////////////////////
gen us_city = 0

replace us_city = 1 if inlist(city, "New York", "Los Angeles1", "Pasadena2", ///
    "Nashville", "San Francisco1", "Chicago", "Philadelphia", "Boston", "Miami")

replace us_city = 1 if inlist(city, "Oakland", "Seattle", "Washington, D.C.", ///
    "Newark", "Austin", "Paterson", "Atlanta", "Minneapolis", "Berkeley")

replace us_city = 1 if inlist(city, "Memphis", "Detroit", "Evanston", ///
    "Miami Beach", "Houston", "New Orleans", "Irvine", "Dallas", "Portland2")

replace us_city = 1 if inlist(city, "Stamford", "San Jose3", "San Mateo", ///
    "Long Beach", "San Diego", "Tampa", "Cleveland", "Cincinnati", "Providence")

replace us_city = 1 if inlist(city, "Denver", "Phoenix", "Covington", ///
    "Richmond1", "Las Vegas2", "Santa Rosa1", "Tucson", "Baltimore", "New Haven")

replace us_city = 1 if inlist(city, "Pittsburgh", "Charlotte", "Columbus2")


////test of market access outside of US////
bysort us_city: sum releases_per_master_*

preserve
drop if us_city == 0

cap xtset city_id epoch

xtreg ln_first_release_taddy L.ln_num_master_ids share*, fe cluster(city)
xtreg ln_avg_taddy L.ln_num_master_ids share*, fe cluster(city)
xtreg ln_taddy_p75 L.ln_num_master_ids share*, fe cluster(city)
xtreg ln_taddy_p95 L.ln_num_master_ids share*, fe cluster(city)

xtreg avg_taddy L.centrality share*, fe cluster(city)
xtreg taddy_p75 L.centrality share*, fe cluster(city)
xtreg taddy_p95 L.centrality share*, fe cluster(city)

reg avg_taddy density, r
xtreg avg_taddy L.density L.num_master_ids share*, fe cluster(city)
xtreg avg_taddy L.density num_nodes L.num_master_ids share*, fe cluster(city)
xtreg avg_taddy L.density num_nodes num_master_ids share*, fe cluster(city)
xtreg taddy_p75 L.density L.num_master_ids share*, fe cluster(city)
xtreg taddy_p95 L.density L.num_master_ids share*, fe cluster(city)

xtreg releases_per_master_mean L.num_master_ids share*, fe cluster(city)
xtreg releases_per_master_25th L.num_master_ids share*, fe cluster(city)
xtreg releases_per_master_75th L.num_master_ids share*, fe cluster(city)
xtreg releases_per_master_90th L.num_master_ids share*, fe cluster(city)

restore

/////////////////////ANALYSIS ON NON-US CITIES/////////////////////
preserve
drop if us_city == 1
cap xtset city_id epoch

xtreg ln_first_release_taddy L.ln_num_master_ids share*, fe cluster(city)
xtreg ln_avg_taddy L.ln_num_master_ids share*, fe cluster(city)
xtreg ln_taddy_p75 L.ln_num_master_ids share*, fe cluster(city)
xtreg ln_taddy_p95 L.ln_num_master_ids share*, fe cluster(city)

xtreg avg_taddy L.centrality share*, fe cluster(city)
xtreg taddy_p75 L.centrality share*, fe cluster(city)
xtreg taddy_p95 L.centrality share*, fe cluster(city)

reg avg_taddy density, r
xtreg avg_taddy L.density L.num_master_ids share*, fe cluster(city)
xtreg avg_taddy L.density num_nodes L.num_master_ids share*, fe cluster(city)
xtreg avg_taddy L.density num_nodes num_master_ids share*, fe cluster(city)
xtreg taddy_p75 L.density L.num_master_ids share*, fe cluster(city)
xtreg taddy_p95 L.density L.num_master_ids share*, fe cluster(city)

xtreg releases_per_master_mean L.num_master_ids share*, fe cluster(city)
xtreg releases_per_master_25th L.num_master_ids share*, fe cluster(city)
xtreg releases_per_master_75th L.num_master_ids share*, fe cluster(city)
xtreg releases_per_master_90th L.num_master_ids share*, fe cluster(city)

restore

///////////DEPRECATED - HAUSMAN TEST/////////
/*
xtreg ln_first_release_taddy ln_num_master_ids share*, fe
estimates store fe
xtreg ln_first_release_taddy ln_num_master_ids share*, re
estimates store re
hausman fe re
*/

/////////ROBUSTNESS TO SIZE CUTOFFS///////////

drop if num_master_ids == .
bysort city_id: gen overall_total = sum(num_master_ids)



////////RAISE CUTOFFS//////
preserve

drop if overall_total < 500

cap xtset city_id epoch

xtreg ln_first_release_taddy L.ln_num_master_ids share*, fe cluster(city)
xtreg ln_avg_taddy L.ln_num_master_ids share*, fe cluster(city)
xtreg ln_taddy_p75 L.ln_num_master_ids share*, fe cluster(city)
xtreg ln_taddy_p95 L.ln_num_master_ids share*, fe cluster(city)

xtreg avg_taddy L.centrality share*, fe cluster(city)
xtreg taddy_p75 L.centrality share*, fe cluster(city)
xtreg taddy_p95 L.centrality share*, fe cluster(city)

reg avg_taddy density, r
xtreg avg_taddy L.density L.num_master_ids share*, fe cluster(city)
xtreg avg_taddy L.density num_nodes L.num_master_ids share*, fe cluster(city)
xtreg avg_taddy L.density num_nodes num_master_ids share*, fe cluster(city)
xtreg taddy_p75 L.density L.num_master_ids share*, fe cluster(city)
xtreg taddy_p95 L.density L.num_master_ids share*, fe cluster(city)

xtreg releases_per_master_mean L.num_master_ids share*, fe cluster(city)
xtreg releases_per_master_25th L.num_master_ids share*, fe cluster(city)
xtreg releases_per_master_75th L.num_master_ids share*, fe cluster(city)
xtreg releases_per_master_90th L.num_master_ids share*, fe cluster(city)

restore



///////////////DROP LARGE CITIES//////////////
preserve

drop if overall_total > 1000

cap xtset city_id epoch

xtreg ln_first_release_taddy L.ln_num_master_ids share*, fe cluster(city)
xtreg ln_avg_taddy L.ln_num_master_ids share*, fe cluster(city)
xtreg ln_taddy_p75 L.ln_num_master_ids share*, fe cluster(city)
xtreg ln_taddy_p95 L.ln_num_master_ids share*, fe cluster(city)

xtreg avg_taddy L.centrality share*, fe cluster(city)
xtreg taddy_p75 L.centrality share*, fe cluster(city)
xtreg taddy_p95 L.centrality share*, fe cluster(city)

reg avg_taddy density, r
xtreg avg_taddy L.density L.num_master_ids share*, fe cluster(city)
xtreg avg_taddy L.density num_nodes L.num_master_ids share*, fe cluster(city)
xtreg avg_taddy L.density num_nodes num_master_ids share*, fe cluster(city)
xtreg taddy_p75 L.density L.num_master_ids share*, fe cluster(city)
xtreg taddy_p95 L.density L.num_master_ids share*, fe cluster(city)

xtreg releases_per_master_mean L.num_master_ids share*, fe cluster(city)
xtreg releases_per_master_25th L.num_master_ids share*, fe cluster(city)
xtreg releases_per_master_75th L.num_master_ids share*, fe cluster(city)
xtreg releases_per_master_90th L.num_master_ids share*, fe cluster(city)

restore