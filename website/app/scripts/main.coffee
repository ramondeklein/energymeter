app = angular.module 'energyMonitor', ['ngRoute','ngMaterial']

Highcharts.setOptions
  global:
    useUTC: false

app.config ($routeProvider) ->
  $routeProvider
  .when '/',
    templateUrl: '/views/chart.html'
  .otherwise
    redirectTo: '/'
