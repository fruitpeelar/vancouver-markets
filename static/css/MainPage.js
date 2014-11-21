//Images
var currentLocation = new google.maps.LatLng(49.287092, -123.117703);
var communityIcon = 'static/Images/CommunityMarket.png';
var farmerIcon = 'static/Images/FarmerMarket.png';
var currentIcon = 'static/Images/CurrentLocation.png';

var markets = [];    //list of Markets
var map;             //Google Map

//Dummy coordinate (if GeoLocation is not supported)
var currentLocation = new google.maps.LatLng(49.287092, -123.117703);

//Direction Routing Properties
var vStrokeColor = "#0DFF00";
var vzIndex = 1;
var directionsService = new google.maps.DirectionsService();
var directionsDisplay;

//Precondition: Database has data (or result will be empy)
//Purpose: Pull market latlon/ marketType from database 
//		-Generate an array of array of markets where 
//		array = [ [lat, lon, marketType, marketName]
//			      [lat, lon, marketType, marketName]
//				   ...  ...      ...   ]

function calcRoute(map, markerPosition) {
	var request = {
		origin: currentLocation,
		destination: markerPosition,
		travelMode: google.maps.TravelMode.DRIVING
		}
   if(directionsDisplay){
      directionsDisplay.setMap(null);
     }
 
   directionsDisplay = new google.maps.DirectionsRenderer({polylineOptions:{suppressPolylines:true, 
   																geodesic:true,  strokeColor:vStrokeColor, 
   																strokeWeight: 4, strokeOpacity: 1, zIndex: vzIndex}});
   directionsDisplay.setMap(map);
   directionsDisplay.setOptions( { suppressMarkers: true } );

   directionsService.route(request, function(response, status) {
     if (status == google.maps.DirectionsStatus.OK) {
      directionsDisplay.setDirections(response);
     }
   });
}
//Precondition: marker is valid
//Purpose: add functionality to marker when clicked (i.e. zoom and centre)

function addClickEvent(map, marker, markerPosition) {
	google.maps.event.addListener(marker, 'click', function() {
		map.setCenter(marker.position);
		map.setZoom(13);
		
		calcRoute(map, markerPosition);
	});
}

function createMarkers(map) {
	for (var i = 0; i < markets.length; i++) {
		var lat  = markets[i][0];
		var long = markets[i][1];
		var latlong = new google.maps.LatLng(markets[i][0], markets[i][1]);
		var marker;
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
		addClickEvent(map, marker, latlong);
	}
}

//Precondition: map, and icons are initialized
//Purpose:  generate all google map markers given an array 
//		   (of array) of market information          

function initializeMarkers(map) {
	//pull market information from database
	retrieveMarkets();
	//create Markers on the google maps
	createMarkers(map);
	//reset Market size to 0
	markets.length = 0;
}

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
//centres and zooms on a market when it is clicked on the table
function clickOnMarket(lat, lon) {
	var marketPosition = new google.maps.LatLng(lat, lon)
	map.setCenter(marketPosition);
	map.setZoom(13);
}

//Precondition: google map api is loaded
//Purpose:  generate a google map and call helpers
//		    to initialize the markers           

function initializeMap() {
	//create the map 		
	var mapCanvas = document.getElementById('map_canvas');
	var mapOptions = {
		zoom: 10,
		mapTypeId: google.maps.MapTypeId.ROADMAP
	}
	map = new google.maps.Map(mapCanvas, mapOptions);
	// Try HTML5 geolocation
  if(navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
    	function(position) {
    		//Success: pos gets currentLocation
      		currentLocation = new google.maps.LatLng(position.coords.latitude,
                                     				position.coords.longitude);
      		map.setCenter(currentLocation);
      		//create the geolocation marker
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
  initializeMarkers(map);
} 
google.maps.event.addDomListener(window, 'load', initializeMap)