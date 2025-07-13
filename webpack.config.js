// /webpack.config.js
const path = require('path');
const NodePolyfillPlugin = require('node-polyfill-webpack-plugin');
const HtmlWebpackPlugin = require('html-webpack-plugin'); // Generates index.html
const MiniCssExtractPlugin = require('mini-css-extract-plugin'); // Extracts CSS into files
const { CleanWebpackPlugin } = require('clean-webpack-plugin'); // Cleans output folder

module.exports = (env, argv) => {
    const isProduction = argv.mode === 'production';

    return {
        // Entry point of your application
        entry: './src/index.js',

        // Output configuration for bundled files
        output: {
            filename: isProduction ? 'js/[name].[contenthash].js' : 'js/[name].js',
            path: path.resolve(__dirname, 'dist'),
            publicPath: '/', // Ensure correct routing for SPA
        },

        // Resolve configuration for polyfills and module aliases
        resolve: {
            fallback: {
                https: require.resolve('https-browserify'),
                http: require.resolve('stream-http'),
                buffer: require.resolve('buffer/'),
                stream: require.resolve('stream-browserify'),
                crypto: require.resolve('crypto-browserify'),
                assert: require.resolve('assert/'),
                util: require.resolve('util/'),
                process: require.resolve('process/browser'),
            },
            // IMPORTANT: Alias the default MUI styled engine (Emotion) to styled‑components
            // This avoids context conflicts causing errors like "Cannot read properties of null (reading 'useContext')"
            alias: {
                '@mui/styled-engine': '@mui/styled-engine-sc',
            },
            extensions: ['.js', '.jsx', '.json'],
        },

        // Module rules for processing different file types
        module: {
            rules: [
                // Transpile JavaScript/JSX using Babel
                {
                    test: /\.(js|jsx)$/,
                    exclude: /node_modules/,
                    use: 'babel-loader',
                },
                // Process CSS files and extract them in production
                {
                    test: /\.css$/,
                    use: [
                        isProduction ? MiniCssExtractPlugin.loader : 'style-loader',
                        'css-loader',
                    ],
                },
                // Load images and fonts
                {
                    test: /\.(png|jpe?g|gif|svg|eot|ttf|woff|woff2)$/,
                    type: 'asset/resource',
                    generator: {
                        filename: 'assets/[hash][ext][query]',
                    },
                },
            ],
        },

        // Plugins to enhance the build process
        plugins: [
            new NodePolyfillPlugin(),
            new CleanWebpackPlugin(), // Clean the dist folder before each build
            new HtmlWebpackPlugin({
                template: './public/index.html', // HTML template file
                minify: isProduction
                    ? {
                        collapseWhitespace: true,
                        removeComments: true,
                        removeRedundantAttributes: true,
                        removeScriptTypeAttributes: true,
                        removeStyleLinkTypeAttributes: true,
                        useShortDoctype: true,
                    }
                    : false,
            }),
            ...(isProduction
                ? [new MiniCssExtractPlugin({ filename: 'css/[name].[contenthash].css' })]
                : []),
        ],

        // Optimization settings for production
        optimization: {
            splitChunks: {
                chunks: 'all',
            },
            runtimeChunk: 'single',
        },

        // DevServer configuration for development mode
        devServer: {
            static: path.join(__dirname, 'dist'),
            historyApiFallback: true, // For SPA routing
            open: true,
            compress: true,
            port: 3000,
            hot: true,
        },

        // Source maps for easier debugging
        devtool: isProduction ? 'source-map' : 'eval-source-map',
    };
};
