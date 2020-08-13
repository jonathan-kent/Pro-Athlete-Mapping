require([
        "esri/Map",
        "esri/layers/CSVLayer",
        "esri/views/MapView",
        "esri/widgets/Legend"],
function (Map, CSVLayer, MapView, Legend) {
  const template = {
    title: "Athlete Info",
    content: "{name}"
  };

  var nflCSV = "http://jonathan-kent.com/athlete_mapping/nfl.csv";
  var nflRenderer = {
    type: "heatmap",
    colorStops: [
      { color: "rgba(255, 171, 171, 0)", ratio: 0 },
      { color: "#ff0000", ratio: 1 }
    ],
    maxPixelIntensity: 10,
    minPixelIntensity: 0
  };


  const nflLayer = new CSVLayer({
    title: "NFL",
    url: nflCSV,
    renderer: nflRenderer,
    popupTemplate: template
  });

  var mlbCSV = "http://jonathan-kent.com/athlete_mapping/mlb.csv";
  var mlbRenderer = {
    type: "heatmap",
    colorStops: [
      { color: "rgba(177, 255, 173, 0)", ratio: 0 },
      { color: "#0dff00", ratio: 1 }
    ],
    maxPixelIntensity: 10,
    minPixelIntensity: 0
  };


  const mlbLayer = new CSVLayer({
    title: "MLB",
    url: mlbCSV,
    renderer: mlbRenderer,
    popupTemplate: template
  });

  var nhlCSV = "http://jonathan-kent.com/athlete_mapping/nhl.csv";
  var nhlRenderer = {
    type: "heatmap",
    colorStops: [
      { color: "rgba(173, 241, 255, 0)", ratio: 0 },
      { color: "#00d5ff", ratio: 1 }
    ],
    maxPixelIntensity: 10,
    minPixelIntensity: 0
  };


  const nhlLayer = new CSVLayer({
    title: "NHL",
    url: nhlCSV,
    renderer: nhlRenderer,
    popupTemplate: template
  });

  var nbaCSV = "http://jonathan-kent.com/athlete_mapping/nba.csv";
  var nbaRenderer = {
    type: "heatmap",
    colorStops: [
      { color: "rgba(255, 226, 173, 0)", ratio: 0 },
      { color: "#ffa500", ratio: 1 }
    ],
    maxPixelIntensity: 10,
    minPixelIntensity: 0
  };


  const nbaLayer = new CSVLayer({
    title: "NBA",
    url: nbaCSV,
    renderer: nbaRenderer,
    popupTemplate: template
  });



  const map = new Map({
    basemap: "dark-gray-vector",
    layers: [nflLayer, mlbLayer, nhlLayer, nbaLayer]
  });

  const view = new MapView({
    container: "viewDiv",
    center: [-90.90614554667947, 38.44811777828268],
    zoom: 3,
    map: map
  });

  // layer toggles

  var nbaLayerToggle = document.getElementById("nbaLayer");
  nbaLayerToggle.addEventListener("change", function () {
    nbaLayer.visible = nbaLayerToggle.checked;
  });
  var nhlLayerToggle = document.getElementById("nhlLayer");
  nhlLayerToggle.addEventListener("change", function () {
    nhlLayer.visible = nhlLayerToggle.checked;
  });
  var mlbLayerToggle = document.getElementById("mlbLayer");
  mlbLayerToggle.addEventListener("change", function () {
    mlbLayer.visible = mlbLayerToggle.checked;
  });
  var nflLayerToggle = document.getElementById("nflLayer");
  nflLayerToggle.addEventListener("change", function () {
    nflLayer.visible = nflLayerToggle.checked;
  });

  view.ui.components = [ "attribution" ];
  view.ui.add(titleDiv, "top-left");
  view.ui.add(
    new Legend({
      view: view
    }),
    "bottom-left"
  );

  view.when().then(function () {
     const nflLayer = view.map.layers.getItemAt(0);
     const nflHeatMapRenderer = nflLayer.renderer.clone();
     const mlbLayer = view.map.layers.getItemAt(1);
     const mlbHeatMapRenderer = mlbLayer.renderer.clone();
     const nhlLayer = view.map.layers.getItemAt(2);
     const nhlHeatMapRenderer = nhlLayer.renderer.clone();
     const nbaLayer = view.map.layers.getItemAt(3);
     const nbaHeatMapRenderer = nbaLayer.renderer.clone();

     const nflSimpleRenderer = {
       type: "simple",
       symbol: {
         type: "simple-marker",
         color: "#ff0000",
         size: 20
       }
     };
     const mlbSimpleRenderer = {
       type: "simple",
       symbol: {
         type: "simple-marker",
         color: "#0dff00",
         size: 20
       }
     };
     const nhlSimpleRenderer = {
       type: "simple",
       symbol: {
         type: "simple-marker",
         color: "#00d5ff",
         size: 20
       }
     };
     const nbaSimpleRenderer = {
       type: "simple",
       symbol: {
         type: "simple-marker",
         color: "#ffa500",
         size: 20
       }
     };

     // When the scale is larger than 1:72,224 (zoomed in passed that scale),
     // then switch from a heatmap renderer to a simple renderer. When zoomed
     // out beyond that scale, switch back to the heatmap renderer

     view.watch("scale", function (newValue) {
       nflLayer.renderer = newValue <= 500000 ? nflSimpleRenderer : nflHeatMapRenderer;
       mlbLayer.renderer = newValue <= 500000 ? mlbSimpleRenderer : mlbHeatMapRenderer;
       nhlLayer.renderer = newValue <= 500000 ? nhlSimpleRenderer : nhlHeatMapRenderer;
       nbaLayer.renderer = newValue <= 500000 ? nbaSimpleRenderer : nbaHeatMapRenderer;
     });
   });

});
