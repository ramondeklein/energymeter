app = angular.module 'energyMonitor'

app.controller 'EnergyChartController', ($scope, ReadingService) ->
  $scope.duration = 60
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
      text: 'Energy overview (times in UTC)'

  ReadingService.getMeters().then (meters) ->
    addMeter = (meter) ->
      serie = chart.addSeries
        name: meter.description

      ReadingService.getPulsesByDuration meter.id, $scope.duration, $scope.period.start, $scope.period.end
      .then (result) ->
        serie.setData result.data

        # Update period based on the returned data
        if !$scope.period.start or result.start < $scope.period.start
          $scope.period.start = result.start
        if !$scope.period.end or result.end > $scope.period.end
          $scope.period.end = result.end

    addMeter meter for meter in meters
