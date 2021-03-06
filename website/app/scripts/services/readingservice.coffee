app = angular.module 'energyMonitor'

app.service 'ReadingService', ($http, $q) ->

  #apiServer = "http://localhost:8888"
  apiServer = ""

  getMeters: ->
    dfd = $q.defer()
    $http.get "#{apiServer}/api/v1/meter"
    .success (data) -> dfd.resolve data.meters
    .error -> dfd.reject 'Unable to obtain the meters.'
    dfd.promise;

  getPulses: (meter, start, end) ->
    dfd = $q.defer()
    params = {}
    params.start = start if start
    params.end = end if end

    $http.get "#{apiServer}/api/v1/pulses/#{meter}", params: params
      .success (data) -> dfd.resolve data
      .error -> dfd.reject 'Unable to obtain the meter pulses.'
    dfd.promise;

  getUsageByDuration: (meter, duration, start, end) ->
    dfd = $q.defer()
    params = {}
    params.start = start if start
    params.end = end if end

    $http.get "#{apiServer}/api/v1/usage/#{meter}/#{duration}", params: params
    .success (data) -> dfd.resolve data
    .error -> dfd.reject 'Unable to obtain the meter usage per duration.'
    dfd.promise;

  getCostByDuration: (meter, duration, start, end) ->
    dfd = $q.defer()
    params = {}
    params.start = start if start
    params.end = end if end

    $http.get "#{apiServer}/api/v1/cost/#{meter}/#{duration}", params: params
    .success (data) -> dfd.resolve data
    .error -> dfd.reject 'Unable to obtain the meter cost per duration.'
    dfd.promise;

  getCurrentPower: ->
    dfd = $q.defer()
    $http.get "#{apiServer}/api/v1/readings/last"
    .success (data) -> dfd.resolve data.meters
    .error -> dfd.reject 'Unable to obtain the meters.'
    dfd.promise;
