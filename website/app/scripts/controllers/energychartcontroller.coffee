app = angular.module 'energyMonitor'

app.controller 'EnergyChartController', ($scope, $interval, ReadingService) ->
  $scope.duration = 60
  $scope.meters = {}
  $scope.period =
    start: null
    end: null

  # Set options
  Highcharts.setOptions
    global:
      useUTC: false         # Show everything in the timezone of the browser

  # Create the chart
  chart = new Highcharts.StockChart
    chart:
      renderTo: 'container',
    navigator:
      adaptToUpdatedData: false
    title:
      text: 'Energy overview'

  ReadingService.getMeters().then (meters) ->
    # Add the meter
    addMeter = (meter) ->
      # Update the meters dictionary, so we have easy access to all its properties
      $scope.meters[meter.id] = meter

      # Add the series to the chart
      serie = chart.addSeries
        name: meter.description
        type: 'spline'

      # Get all the power readings for this meter from the back-end
      duration = $scope.duration
      ReadingService.getPulsesByDuration meter.id, $scope.duration, $scope.period.start, $scope.period.end
      .then (result) ->
        serie.setData ([item[0], Math.round (item[1] * meter.currentFactor) / duration] for item in result.data)

        # Update period based on the returned data
        if !$scope.period.start or result.start < $scope.period.start
          $scope.period.start = result.start
        if !$scope.period.end or result.end > $scope.period.end
          $scope.period.end = result.end

    # Method to get the current power readings
    getCurrentPower = ->
      #ReadingService.getCurrentPower().then (meters) ->
      #  for meter in meters
      #    console.log "#{$scope.meters[meter.id].description}: #{meter.power}"

    # Add all meters
    addMeter meter for meter in meters

    # Get the current power reading
    getCurrentPower()

    # Obtain the reading every 5 seconds
    $interval getCurrentPower, 5000