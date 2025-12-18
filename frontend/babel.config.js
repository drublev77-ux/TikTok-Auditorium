module.exports = function (api) {
  api.cache(true);
  return {
    presets: ["babel-preset-expo"],
    plugins: [
      // Fixes: "Cannot use 'import.meta' outside a module" in some web bundles
      "babel-plugin-transform-import-meta",
    ],
  };
};
