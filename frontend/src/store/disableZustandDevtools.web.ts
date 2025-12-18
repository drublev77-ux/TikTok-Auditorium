// Web-only patch:
// Legacy expo-cli web bundle can crash on `import.meta` usage inside zustand devtools.
// We disable the devtools middleware by forcing production mode.

// eslint-disable-next-line no-underscore-dangle
(globalThis as any).process = (globalThis as any).process ?? {};
// eslint-disable-next-line no-underscore-dangle
(globalThis as any).process.env = (globalThis as any).process.env ?? {};
// eslint-disable-next-line no-underscore-dangle
(globalThis as any).process.env.NODE_ENV = "production";
