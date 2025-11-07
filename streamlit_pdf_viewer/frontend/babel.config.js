module.exports = {
  presets: [
    '@vue/cli-plugin-babel/preset'
  ],
  // Ignore large PDF.js files from Babel processing to avoid deoptimization warnings
  ignore: [
    /node_modules\/pdfjs-dist\/build\/pdf\.worker\.mjs$/,
    /node_modules\/pdfjs-dist\/build\/pdf\.mjs$/,
    /node_modules\/pdfjs-dist\/build\/pdf\.sandbox\.mjs$/
  ]
};
