app = angular.module 'energyMonitor'

app.controller 'EnergyChartController', ($scope, ReadingService) ->
  $scope.meters = [
    { id: 1, description: 'Electricity' }
    { id: 2, description: 'Gas' }
  ]
  $scope.period =
    start: new Date(2015,0,1)
    end: new Date(2015,1,1)

  ReadingService.getPulses $scope.meters[0].id, $scope.period.start, $scope.period.end
  .then (data) ->
    $scope.period.start = data.start
    $scope.period.end = data.end

    # Create the chart
    $('#container').highcharts 'StockChart',
      rangeSelector:
        selected: 1
      title:
        text: 'AAPL Stock Price'
      series: [
        name : 'AAPL'
        data : data.pulses
        tooltip:
          valueDecimals: 2
      ]
    , (error) ->
        x = data;

    $scope.start = null
