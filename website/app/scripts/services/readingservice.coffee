app = angular.module 'energyMonitor'

app.service 'ReadingService', ($http, $q) ->

  apiServer = "http://localhost:8888"

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

  getPulsesByDuration: (meter, duration, start, end) ->
    dfd = $q.defer()
    params = {}
    params.start = start if start
    params.end = end if end

    $http.get "#{apiServer}/api/v1/duration/#{meter}/#{duration}", params: params
    .success (data) -> dfd.resolve data
    .error -> dfd.reject 'Unable to obtain the meter pulses per duration.'
    dfd.promise;
