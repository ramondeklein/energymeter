(function() {
    var app;
    app = angular.module("energyMonitor", [ "ngRoute" ]);
    app.config([ "$routeProvider", function($routeProvider) {
        return $routeProvider.when("/", {
            templateUrl: "/views/chart.html"
        }).otherwise({
            redirectTo: "/"
        });
    } ]);
}).call(this);

(function() {
    var app;
    app = angular.module("energyMonitor");
    app.service("ReadingService", [ "$http", "$q", function($http, $q) {
        return {
            getPulses: function(meter, start, end) {
                var dfd, params;
                dfd = $q.defer();
                params = {};
                if (start) {
                    params.start = start;
                }
                if (end) {
                    params.end = end;
                }
                $http.get("/api/v1/pulses/" + meter, {
                    params: params
                }).success(function(data, status, headers, config) {
                    return dfd.resolve(data);
                }).error(function(data, status, headers, config) {
                    return dfd.reject("Unable to obtain the meter pulses.");
                });
                return dfd.promise;
            }
        };
    } ]);
}).call(this);

(function() {
    var app;
    app = angular.module("energyMonitor");
    app.controller("EnergyChartController", [ "$scope", "ReadingService", function($scope, ReadingService) {
        $scope.period = {
            start: new Date(2015, 0, 1),
            end: new Date(2015, 1, 1)
        };
        return ReadingService.getPulses(1, $scope.period.start, $scope.period.end).then(function(electricity) {
            return ReadingService.getPulses(2, $scope.period.start, $scope.period.end).then(function(gas) {
                $scope.period.start = electricity.start < gas.start ? electricity.start : gas.start;
                $scope.period.end = electricity.end > gas.end ? electricity.start : gas.start;
                $("#container").highcharts("StockChart", {
                    rangeSelector: {
                        selected: 1
                    },
                    title: {
                        text: "Energy overview (times in UTC)"
                    },
                    series: [ {
                        name: "Electricity",
                        data: electricity.pulses
                    }, {
                        name: "Gas",
                        data: gas.pulses
                    } ]
                });
                return $scope.start = null;
            });
        });
    } ]);
}).call(this);

angular.module("energyMonitor").run([ "$templateCache", function($templateCache) {
    "use strict";
    $templateCache.put("/views/chart.html", '<div ng-controller=EnergyChartController><div id=container style="width: 100%; height: 400px"></div></div>');
} ]);