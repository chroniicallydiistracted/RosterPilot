const nextJest = require("next/jest");

const createJestConfig = nextJest({
  dir: "./"
});

const customJestConfig = {
  testEnvironment: "jest-environment-jsdom",
  setupFilesAfterEnv: ["<rootDir>/tests/setupTests.ts"],
  moduleNameMapper: {
    "^@/(.*)$": "<rootDir>/$1",
    "\\.(css|less|scss|sass)$": "identity-obj-proxy"
  },
  testMatch: ["<rootDir>/tests/**/*.test.ts", "<rootDir>/tests/**/*.test.tsx"],
  collectCoverageFrom: [
    "<rootDir>/components/**/*.{ts,tsx}",
    "<rootDir>/hooks/**/*.{ts,tsx}",
    "<rootDir>/lib/**/*.{ts,tsx}"
  ]
};

module.exports = createJestConfig(customJestConfig);
