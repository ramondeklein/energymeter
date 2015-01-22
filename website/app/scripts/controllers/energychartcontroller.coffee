app = angular.module 'energyMonitor'

app.controller 'EnergyChartController', ($scope, ReadingService) ->
  $scope.meters = []
  $scope.date = new Date()
  $scope.altdate = null
  $scope.data =
    compareWithYesterday: false

  $scope.$watch 'data.compareWithYesterday', (newValue) ->
    $scope.altdate = if newValue then new Date($scope.date.getTime() - (24 * 60 * 60 * 1000)) else null

  ReadingService.getMeters().then (meters) ->
    $scope.meters = meters
