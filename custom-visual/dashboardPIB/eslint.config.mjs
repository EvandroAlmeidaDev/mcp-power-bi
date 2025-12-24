import eslint from "@eslint/js";
import tseslint from "typescript-eslint";

export default [
    eslint.configs.recommended,
    ...tseslint.configs.recommended,
    {
        rules: {
            // Desabilita regra de innerHTML para este visual (necessário para renderização HTML)
            "powerbi-visuals/no-inner-outer-html": "off",
            "@typescript-eslint/no-explicit-any": "off"
        }
    }
];