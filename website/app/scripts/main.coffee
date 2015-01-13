app = angular.module 'energyMonitor', ['ngRoute']

app.config ($routeProvider) ->
  $routeProvider
  .when '/',
    templateUrl: '/views/chart.html'
  .otherwise
    redirectTo: '/'
