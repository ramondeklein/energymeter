'use strict'

app = angular.module 'energyMonitor'

app.directive 'emChart', ($filter, $mdTheming) ->

  serieConfiguration =
    main:
      id: 'main'
    alt:
      id: 'alt'
      type: 'spline'
      color: 'rgba(31,31,31,.5)'

  restrict: 'E'
  scope:
    title: '@emTitle'
    meter: '&emMeter'
    date: '&emDate'
    altDate: '&emAltdate'
    interval: '&emInterval'

  link: ($scope, element) ->
    # Obtain the chart object
    highChartContainer = element[0]

    # Create the chart
    $scope._chart = new Highcharts.StockChart
      chart:
        renderTo: highChartContainer
        type: 'areaspline'
      credits:
        enabled: false
      rangeSelector:
        enabled: false
      tooltip:
        shared: true
        formatter: ->
          tooltip = "<b>#{$filter('date')(@x,'shortTime')}</b>"
          for point in @points
            tooltip += "<br/>#{point.series.name}: #{point.y}"
          tooltip
      plotOptions:
        areaspline:
          fillOpacity: 0.5

  controller: ($scope, ReadingService) ->
    cache = {}
    loadData = (id, date) ->
      # Check if the serie already exists
      chart = $scope._chart
      serie = chart.get id
      meter = $scope.meter()
      if date and meter
        # Make sure the serie is created
        serie ?= chart.addSeries angular.extend {}, serieConfiguration[id], name: $filter('date')(date, 'shortDate')

        # Obtain only the date part
        date = new Date(date.getTime())
        date.setHours 0
        date.setMinutes 0
        date.setSeconds 0
        date.setMilliseconds 0

        # Determine the duration
        duration = $scope.interval() or 60

        # Avoid loading the same date multiple times
        if currentDate = date.getTime()
          if currentDate != cache[id]
            cache[id] = date.getTime()

            # Read the usage for this meter
            ReadingService.getUsageByDuration meter.id, duration, date
            .then (usageResult) ->
              offset = date.getTime()

              # Set the proper data
              serie.setData ([item[0]-offset, Math.round (item[1] * meter.currentFactor) / duration] for item in usageResult.data)
            , ->
              # Clear serie when no data can be loaded
              serie.setData []
        else
          serie?.remove true

    initGraph = ->
      if chart = $scope._chart
        # Remove all existing series
        while chart.series.length
          chart.series[0].remove true

        # Load the data
        loadDate()
        loadAltDate()

    loadDate = ->
      loadData 'main', $scope.date() or new Date()

    loadAltDate = ->
      loadData 'alt', $scope.altDate()

    $scope.getTitle = ->
      $scope.title or $scope.meter()?.description or ''

    # Watch title changes
    $scope.$watch 'getTitle()', (newTitle) ->
      $scope._chart?.setTitle text: newTitle

    # Reload when the data changes
    $scope.$watch 'meter()', -> initGraph()
    $scope.$watch 'date()', -> loadDate()
    $scope.$watch 'altDate()', -> loadAltDate()
