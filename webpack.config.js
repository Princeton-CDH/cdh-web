const path = require('path');
const glob = require('glob');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const cssnano = require('cssnano');
const autoprefixer = require('autoprefixer');
const SVGSpritemapPlugin = require('svg-spritemap-webpack-plugin');
const { CleanWebpackPlugin } = require('clean-webpack-plugin');

const outputPath = 'static/dist';

const SVG_SPRITE_DIR = './cdhweb/static_src/images/sprites_src';
const svgSpritePattern = path.join(SVG_SPRITE_DIR, '*/'); // note: trailing slash means it will match directories only

module.exports = (env, options) => {
  const plugins = [
    new MiniCssExtractPlugin({
      filename: 'styles.css',
      chunkFilename: '[name]-[id].css',
    }),
    new CleanWebpackPlugin({
      cleanOnceBeforeBuildPatterns: [path.resolve(__dirname, outputPath)],
    }),
  ];

  // SVG sprites. Each directory will create a spritemap (spritesheet).
  // It's a good idea to have several different spritemaps, especially to split out
  // larger or one-off SVGs, so that pages which don't use any of the svgs from a
  // spritemap don't need to download that file.
  const svgSpriteDirs = glob.sync(svgSpritePattern);
  svgSpriteDirs.forEach((svgSpriteDir) => {
    const svgPattern = path.resolve(__dirname, svgSpriteDir, '*.svg');
    const opts = {
      output: {
        filename: `${path.basename(svgSpriteDir)}.svg`,
        svgo: true,
      },
      sprite: {
        prefix: false,
      },
    };
    plugins.push(new SVGSpritemapPlugin(svgPattern, opts));
  });

  return {
    mode: options.mode,
    devtool: options.mode !== 'production' ? 'inline-source-map' : undefined,
    entry: './cdhweb/static_src/index.tsx',
    output: {
      //  NOTE: this is a little different from usual Springload setup due to different directory structure of this site.
      path: path.resolve(__dirname, outputPath),
      publicPath: '/static/dist/',
      filename: '[name].js', // No filename hashing, Django takes care of this
      chunkFilename: '[name]-[chunkhash].js',
      clean: true,
    },
    devServer: {
      writeToDisk: true, // Write files to disk in dev mode, so Django can serve the assets
    },
    resolve: {
      extensions: ['.tsx', '.ts', '.js'],
      alias: {
        react: 'preact/compat',
        'react-dom/test-utils': 'preact/test-utils',
        'react-dom': 'preact/compat', // Must be below test-utils
      },
    },
    plugins,
    module: {
      rules: [
        {
          test: /\.tsx?$/,
          exclude: /(node_modules)/,
          use: [
            {
              loader: 'ts-loader',
            },
          ],
        },
        {
          test: /\.(scss|css)$/,
          use: [
            {
              loader: MiniCssExtractPlugin.loader,
            },
            {
              loader: 'css-loader', // translates CSS into CommonJS
              options: {
                url: true,
                sourceMap: options.mode === 'development',
                importLoaders: 2,
              },
            },
            {
              loader: 'postcss-loader',
              options: {
                sourceMap: options.mode === 'development',
                postcssOptions: {
                  plugins: [
                    autoprefixer,
                    options.mode !== 'development' ? cssnano : undefined,
                  ],
                },
              },
            },
            {
              loader: 'sass-loader', // translates sass to css
              options: {
                sourceMap: options.mode === 'development',
              },
            },
          ],
        },
        {
          test: /\.woff|woff2$/,
          type: 'asset/resource',
        },
        {
          test: /\.svg|jpg|webp|png$/,
          type: 'asset/resource',
        },
      ],
    },
  };
};
