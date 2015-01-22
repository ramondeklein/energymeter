app = angular.module 'energyMonitor'

app.controller 'EnergyChartController', ($scope, $interval, ReadingService) ->
  $scope.meters = []
  $scope.today = new Date()
  $scope.yesterday = new Date($scope.today.getTime() - (24 * 60 * 60 * 1000))

  ReadingService.getMeters().then (meters) ->
    $scope.meters = meters
