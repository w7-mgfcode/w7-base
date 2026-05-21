import tseslint from "typescript-eslint";

const determinismBans = [
  {
    selector: "MemberExpression[object.name='Math'][property.name='random']",
    message: "Math.random is forbidden in core/**. Use mulberry32(seed) via prng.ts.",
  },
  {
    selector: "MemberExpression[object.name='Date'][property.name='now']",
    message: "Date.now is forbidden in core/**. The engine has no concept of time.",
  },
  {
    selector: "NewExpression[callee.name='Date']",
    message: "new Date() is forbidden in core/**. The engine has no concept of time.",
  },
  {
    selector: "MemberExpression[object.name='performance'][property.name='now']",
    message: "performance.now is forbidden in core/**.",
  },
  {
    selector:
      "MemberExpression[object.name='crypto'][property.name='getRandomValues']",
    message: "crypto.getRandomValues is forbidden in core/**.",
  },
];

export default tseslint.config(
  {
    ignores: ["node_modules", "dist", "scripts/**", "**/__tests__/**"],
  },
  ...tseslint.configs.recommended,
  {
    files: ["src/core/**/*.ts"],
    languageOptions: {
      parserOptions: {
        project: false,
        ecmaVersion: 2022,
        sourceType: "module",
      },
    },
    rules: {
      "no-restricted-syntax": ["error", ...determinismBans],
      "@typescript-eslint/no-unused-vars": [
        "error",
        { argsIgnorePattern: "^_", varsIgnorePattern: "^_" },
      ],
      "@typescript-eslint/no-explicit-any": "warn",
    },
  },
);
