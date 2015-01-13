module.exports = (grunt) ->

  # Load Grunt tasks automatically
  require('load-grunt-tasks')(grunt)

  # Time all Grunt tasks
  require('time-grunt')(grunt)

  # Configure Grunt
  grunt.initConfig
        
    # Define all paths
    paths:
      app: 'app'
      tmp: '.tmp'
      dist: 'static-dist'

    clean:
      # Clear all temporary files
      tmp:
        files: [
          dot: true
          src: ['<%= paths.tmp %>/*']
        ]

      # Clear all distribution files
      dist:
        files: [
          dot: true,
          src: ['<%= paths.dist %>/*']
        ]

    # HAML to HTML conversion
    haml:
      app:
        files: [
          expand: true,
          cwd: '<%= paths.app %>/'
          src: ['*.haml', 'views/{,*/}*.haml']
          dest: '<%= paths.tmp %>/'
          ext: '.html'
        ]

    compass:
      options:
        sassDir: '<%= paths.app %>/styles'
        cssDir: '<%= paths.tmp %>/styles'
        imagesDir: '<%= paths.app %>/images'
        generatedImagesDir: '<%= paths.tmp %>/images/generated'
        javascriptsDir: '<%= paths.tmp %>/scripts'
        fontsDir: '<%= paths.app %>/styles/fonts'
        importPath: '<%= paths.app %>/bower_components'
        httpImagesPath: '/images'
        httpGeneratedImagesPath: '/images/generated'
        httpFontsPath: '/styles/fonts'
        relativeAssets: false
        assetCacheBuster: false
        raw: 'Sass::Script::Number.precision = 10\n'

      app:
        options:
          debugInfo: true

      dist:
        options:
          generatedImagesDir: '<%= paths.dist %>/images/generated'

    autoprefixer:
      options:
        browsers: ['last 1 version']

      app:
        files: [
          expand: true
          cwd: '<%= paths.tmp %>/styles/'
          src: '{,*/}*.css'
          dest: '<%= paths.tmp %>/styles/'
        ]

    coffee:
      app:
        files: [
          expand: true,
          cwd: '<%= paths.app %>/',
          src: ['scripts/{,*/}*.coffee'],
          dest: '<%= paths.tmp %>/',
          ext: '.js'
        ]

    ngAnnotate:
      options:
        singleQuotes: true

      app:
        files: [
          src: '<%= paths.tmp %>/scripts/{,*/}*.js'
        ]

      dist:
        files: [
          '<%= paths.tmp %>/concat/scripts/scripts.js': '<%= paths.tmp %>/concat/scripts/scripts.js'
        ]

    useminPrepare:
      options:
        dest: '<%= paths.dist %>'

      html:
        files:
          src: ['<%= paths.tmp %>/*.html']

    usemin:
      options:
        assetsDirs: ['<%= paths.dist %>', '<%= paths.dist %>/images']
        patterns:
          js: [[/(images\/.*?\.(?:gif|jpeg|jpg|png|webp))/gm, 'Update the JS to reference our revved images']]

      html: ['<%= paths.dist %>/*.html']
      css: ['<%= paths.dist %>/styles/{,*/}*.css']
      js: ['<%= paths.dist %>/{,*/}*.js']

    imagemin:
      dist:
        files: [
          expand: true
          cwd: '<%= paths.app %>/images'
          src: '**/*.{png,jpg,jpeg,gif}'
          dest: '<%= paths.dist %>/images'
        ]

    svgmin:
      dist:
        files: [
          expand: true
          cwd: '<%= paths.app %>/images'
          src: '**/*.svg'
          dest: '<%= paths.dist %>/images'
        ]

    htmlmin:
      dist:
        options:
          collapseWhitespace: true
          collapseBooleanAttributes: true
          removeAttributeQuotes: true
          removeCommentsFromCDATA: true
          removeEmptyAttributes: true
          removeOptionalTags: true
          removeRedundantAttributes: true
          removeScriptTypeAttributes:  true
          removeStyleLinkTypeAttributes: true
          minifyCSS: true

        files: [
          expand: true
          cwd: '<%= paths.dist %>'
          src: ['*.html']
          dest: '<%= paths.dist %>'
        ]

    rev:
      dist:
        files:
          src: ['<%= paths.dist %>/scripts/*.js', '<%= paths.dist %>/styles/{,*/}*.css', '<%= paths.dist %>/images/{,*/}*.{png,jpg,jpeg,gif,webp,svg}']

    ngtemplates:
      dist:
        cwd: '<%= paths.tmp %>'
        src: 'views/**/*.html'
        dest: '<%= paths.tmp %>/concat/scripts/templates.js'
        options:
          module: 'energyMonitor'
          prefix: '/'
          usemin: '<%= paths.dist %>/scripts/scripts.js'
          htmlmin:
            collapseBooleanAttributes: true
            collapseWhitespace: true
            removeAttributeQuotes: true
            removeComments: true
            removeEmptyAttributes: true
            removeRedundantAttributes: true
            removeScriptTypeAttributes:  true
            removeStyleLinkTypeAttributes: true

    copy:
      dist:
        files: [
          dot: true
          expand: true
          cwd: '<%= paths.tmp %>'
          dest: '<%= paths.dist %>'
          src: ['*.html']
        ,
          dot: true
          expand: true
          cwd: '<%= paths.app %>'
          dest: '<%= paths.dist %>'
          src: ['*.{ico,png,txt,html}', 'fonts/*.{eot,svg,ttf,woff}']
        ,
          expand: true
          cwd: '<%= paths.tmp %>/images'
          dest: '<%= paths.dist %>/images'
          src: ['tmp/*']
        ]

    watch:
      haml:
        files: ['<%= paths.app %>/*.haml','<%= paths.app %>/views/{,*/}*.haml']
        tasks: ['newer:haml:app']

      compass:
        files: ['<%= paths.app %>/styles/{,*/}*.{scss,sass}']
        tasks: ['newer:compass:app', 'newer:autoprefixer:app']

      coffee:
        files: ['<%= paths.app %>/scripts/{,*/}*.coffee']
        tasks: ['newer:coffee:app', 'newer:ngAnnotate:app']

      livereload:
        files: ['<%= paths.tmp %>/styles/{,*/}*.css']
        options:
            livereload: true

    connect:
      options:
        hostname: 'localhost'
        debug: true

      app:
        options:
          port: 9000
          open: 'http://localhost:9000'
          base: ['<%= paths.tmp %>', '<%= paths.app %>']
          livereload: true

      livereload:
        options:
          open: 'http://localhost:9000'
          base: ['<%= paths.tmp %>', '<%= paths.app %>' ]

      dist:
        options:
          port: 9001
          open: 'http://localhost:9001'
          base: '<%= paths.dist %>'

    # Uncomment the following block when debugging the dist version
    uglify:
      options:
        mangle: false
        compress: false
        beautify: true
        preserveComments: 'all'

    modernizr:
      app:
        devFile: '<%= paths.app %>/bower_components/modernizr/modernizr.js'
        outputFile: '<%= paths.tmp %>/scripts/custom-modernizr.js'
        extra:
            shiv: false
            load: false
        matchCommunityTests: true
        uglify: false
        tests: ['fontface', 'backgroundsize', 'borderradius', 'boxshadow', 'opacity', 'rgba', 'textshadow', 'cssanimations', 'generatedcontent', 'cssgradients', 'csstransforms', 'csstransitions', 'canvas', 'localstorage', 'svg']
        parseFiles: false

  grunt.registerTask 'build', (target) ->
    switch target or 'develop'
        when 'develop'
          grunt.task.run [
            'clean:tmp'
            'modernizr:app'
            'coffee:app'
            'ngAnnotate:app'
            'haml:app'
            'compass:app'
            'autoprefixer:app'
          ]

        when 'dist'
          grunt.task.run [
            'clean:dist'
            'clean:tmp'
            'haml:app'
            'modernizr:app'
            'useminPrepare'
            'coffee:app'
            'ngAnnotate:app'
            'compass:dist'
            'autoprefixer:app'
            'imagemin'
            'svgmin'
            'ngtemplates:dist'
            'concat'
            'copy:dist'
            'cssmin'
            'uglify'
            'rev'
            'usemin'
            'htmlmin'
          ]

  # Register the different serve tasks
  grunt.registerTask 'serve', (target) ->
    switch target or 'develop'
      when 'develop'
        grunt.task.run ['build:develop', 'connect:app', 'watch']
      when 'dist'
        grunt.task.run ['build:dist', 'connect:dist:keepalive']

  # Some useful aliases
  grunt.registerTask 'serve-develop', ['serve:develop']
  grunt.registerTask 'serve-dist', ['serve:dist']
