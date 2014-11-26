//Images
var currentLocation = new google.maps.LatLng(49.287092, -123.117703);
var communityIcon   = 'static/Images/CommunityMarket.png';
var farmerIcon      = 'static/Images/FarmerMarket.png';
var currentIcon     = 'static/Images/CurrentLocation.png';

//Map Variables
var markets = [];  
var map;             

//Dummy coordinate (if GeoLocation is not supported)
var currentLocation = new google.maps.LatLng(49.287092, -123.117703);

//Direction Routing Properties
var vStrokeColor = "#0DFF00";
var vzIndex = 1;
var directionsService = new google.maps.DirectionsService();
var directionsDisplay;

//<--------------------------- Google Map Initialization ------------------------------------->

//Precondition: google map API is loaded
//Purpose:  generate a google map and call helpers
//		    to initialize the map and its markers           
function initializeMap() {		
	var mapCanvas = document.getElementById('map_canvas');
	//map properties 
	var mapOptions = {
		zoom: 10,
		mapTypeId: google.maps.MapTypeId.ROADMAP
	}
	//define map variable
	map = new google.maps.Map(mapCanvas, mapOptions);
	// Try HTML5 geolocation
	if(navigator.geolocation) {
		navigator.geolocation.getCurrentPosition(
				function(position) {
					//Success: currentLocation holds location value
					currentLocation = new google.maps.LatLng(position.coords.latitude,
                                     					position.coords.longitude);
					//set map's center to currentLocation
					map.setCenter(currentLocation);
					//create currentLocation marker
					new google.maps.Marker( {
						position: currentLocation,
						map: map,
						title: "Current Location",
						icon: currentIcon
					});    
				}, 
				function() {
					//Error: handle with error message
					handleNoGeolocation(true);
				});
  } else {
  	// Browser doesn't support Geolocation:
   	handleNoGeolocation(false);
  }
  //create the market markers
  initializeMarkers();
} 
google.maps.event.addDomListener(window, 'load', initializeMap);


//<-------------------------------- Helper Functions ------------------------------------->

//Purpose: handle situations where GeoLocation fails
//if so, center the map at the default location on downtown Vancouver
function handleNoGeolocation(errorFlag) {
	if (errorFlag) {
		var content = 'Error: The Geolocation service failed.';
	} else {
		var content = 'Error: Your browser doesn\'t support geolocation.';
	}
	var options = {
			map: map,
			position: new google.maps.LatLng(60, 105),
			content: content
	};
	var infowindow = new google.maps.InfoWindow(options);
	map.setCenter(options.position);
}

//Precondition: map is initialized. markets variable is empty
//Purpose:  generate all google map markers from markets stored in the database     
function initializeMarkers() {
	//pull market information from database (the function is in main_page.html)
	retrieveMarkets();
	//create Markers on the google maps
	createMarkers();
	//reset Market size to 0
	markets.length = 0;
}

//Precondition: markets variable holds all the markets that were pulled from the database
//Purpose: create markers for each market.
function createMarkers() {
	for (var i = 0; i < markets.length; i++) {
		//for each market, get location information
		var lat  = markets[i][0];
		var long = markets[i][1];
		var latlong = new google.maps.LatLng(markets[i][0], markets[i][1]);
		var marker;
		//create an appropriate marker at that location
		//          "appropriate"refers to farmer or community icon
		if (markets[i][2] == "Farmers Market")
			marker = new google.maps.Marker( {
					position: latlong,
					map: map,
					title: markets[i][3],
					icon: farmerIcon
				});
		else {
			marker = new google.maps.Marker( {
					position: latlong,
					map: map,
					title: markets[i][3],
					icon: communityIcon
			});
		}	
		//add click event for each marker
		addClickEvent(marker, latlong);
	}
}

//Precondition: marker is valid
//Purpose: zooms/centres/calculates route to market that is clicked.
function addClickEvent(marker, markerPosition) {
	google.maps.event.addListener(marker, 'click', function() {
		map.setCenter(marker.position);
		map.setZoom(13);
		//display the route from the currentlocation to the clicked market
		calcRoute(markerPosition);
	});
}

//Precondition: map has been initialized. 
//Purpose: calculate route and display route on the map for the given market marker position
function calcRoute(markerPosition) {
	//request for google maps route
	var request = {
		origin: currentLocation,
		destination: markerPosition,
		travelMode: google.maps.TravelMode.DRIVING
		}
	//if route has already been shown on map, set it to null
	if(directionsDisplay){
		directionsDisplay.setMap(null);
   }
	//directions display characteristics
	directionsDisplay = new google.maps.DirectionsRenderer({polylineOptions:{suppressPolylines:true, 
 																geodesic:true,  strokeColor:vStrokeColor, 
 																strokeWeight: 4, strokeOpacity: 1, zIndex: vzIndex}});
	///set directionsDiplay to the map
	directionsDisplay.setMap(map);
	directionsDisplay.setOptions( { suppressMarkers: true } );
	
	//set the directions
	directionsService.route(request, function(response, status) {
		if (status == google.maps.DirectionsStatus.OK) {
			directionsDisplay.setDirections(response);
		}
	});
}