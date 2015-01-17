app = angular.module 'energyMonitor'

app.service 'ReadingService', ($http, $q) ->

  getPulses: (meter, start, end) ->
    dfd = $q.defer()
    params = {}
    params.start = start if start
    params.end = end if end

    $http.get "/api/v1/pulses/#{meter}", params: params
      .success (data, status, headers, config) ->
        # This callback will be called asynchronously when the response is available
        dfd.resolve data
      .error (data, status, headers, config) ->
        # Called asynchronously if an error occurs or server returns response with an error status.
        dfd.reject 'Unable to obtain the meter pulses.'
    dfd.promise;
