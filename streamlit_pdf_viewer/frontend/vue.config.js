const {VueLoaderPlugin} = require('vue-loader');
module.exports = {
  publicPath: './',
  configureWebpack: {
    target: 'web',
    module: {
      rules: [
        {
          test: /\.(js|mjs)$/,
          include: /node_modules\/pdfjs-dist/,
          use: {
            loader: 'babel-loader',
            options: {
              presets: [['@babel/preset-env', {targets: {esmodules: true}}]],
            }
          }
        }
      ]
    },
    plugins: [
      new VueLoaderPlugin()
    ],
  }
}