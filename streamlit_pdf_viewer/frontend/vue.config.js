module.exports = {
  publicPath: './',
  configureWebpack: {
    module: {
      rules: [
        {
          test: /\.js$/,
          include: /node_modules\/pdfjs-dist/,
          use: {
            loader: 'babel-loader',
            options: {
              presets: ['@babel/preset-env'],
              plugins: ['@babel/plugin-proposal-class-properties', '@babel/plugin-proposal-private-methods']
            }
          }
        }
      ]
    }
  }
}