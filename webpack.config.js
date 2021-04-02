const path = require('path')

module.exports = {
  entry: '/octoprint_wled/static/src/wled.js',
  output: {
    filename: 'wled.js',
    path: path.resolve(__dirname, 'octoprint_wled/static/dist')
  },
  module: {
    rules: [
      {
        test: /\.m?js$/,
        exclude: /(node_modules|bower_components)/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: ['@babel/preset-env']
          }
        }
      }
    ]
  }
}
