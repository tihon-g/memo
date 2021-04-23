const path = require('path');
const BundleTracker = require('webpack-bundle-tracker');

module.exports = {
    webpack: function (config, env) {
        if (config.mode == 'development') {
            config.output.publicPath = 'http://localhost:3000/';
            config.entry = ['webpack-dev-server/client?http://localhost:3000', config.entry];
        }
        config.plugins.push(new BundleTracker({
            path: __dirname,
            filename: './webpack-stats.json',
        }))
        return config;
    },
    devServer: function (configFunction) {
        return function (proxy, allowedHost) {
            const config = configFunction(proxy, allowedHost);
            config.headers = {
                "Access-Control-Allow-Origin": "*"
            }
            return config;
        }
    }
}
