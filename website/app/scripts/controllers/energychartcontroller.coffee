app = angular.module 'energyMonitor'

app.controller 'EnergyChartController', ($scope, ReadingService) ->
  $scope.period =
    start: new Date(2015,0,1)
    end: new Date(2015,1,1)

  ReadingService.getPulses 1, $scope.period.start, $scope.period.end
  .then (electricity) ->
    ReadingService.getPulses 2, $scope.period.start, $scope.period.end
    .then (gas) ->
        $scope.period.start = if electricity.start < gas.start then electricity.start else gas.start
        $scope.period.end = if electricity.end > gas.end then electricity.start else gas.start

        # Create the chart
        $('#container').highcharts 'StockChart',
          rangeSelector:
            selected: 1
          title:
            text: 'Energy overview (times in UTC)'
          series: [
            name : 'Electricity'
            data : electricity.pulses
          ,
            name : 'Gas'
            data : gas.pulses
          ]

        $scope.start = null
