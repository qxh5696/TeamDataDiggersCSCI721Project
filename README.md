# Getting started with the project:
1. Pull down all files (must have jupyter-notebook python package available)
2. Install the following packages:

	a) numpy: numerical python package

	b) pandas: data manipulation
	
	c) matplotlib: data visualization
	
	d) seaborn: data visualization
	
	e) joblib: helps saving and loading python objects
	
	f) googlemaps & gmaps: separate packages. Helps plot listings onto heatmap as well as get latitude and longitude coordinates. MUST HAVE YOUR OWN API KEY 
	
	g) beautiful soup 4: Static page scraping
	
	h) selenium webdriver: dynamic page scraping
	
3. Both Airbnb and Tripadvisor datasets are already included, but if you want to collect more data, run the AirbnbScraper notebook and the TripAdvisorScraper notebook 
4. After data collection, run the Normalization notebook to clean and combine the datasets. Normalization notebook also includes graphing components easier data visualization
5. Finally, the GoogleMapsVizualizer notebook is what makes the google maps api calls. Don't even bother running this without your own APIKey, or contacting me to borrow mine. Google Cloud as $300 free credit for student accounts so making your account and lplugging in your own should work just fine. 

Make sure that all files are in the same directory or you will have FileNotFound errors!  
