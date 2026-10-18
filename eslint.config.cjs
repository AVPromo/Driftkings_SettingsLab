/* Build tooling runs on Node 20; the checked client scripts stay ES5. */
module.exports = [
    {
        files: ["mod/res/gui/gameface/**/*.js", "prototypes/tactical_minimap/*.js"],
        languageOptions: {
            ecmaVersion: 5,
            sourceType: "script",
            globals: {
                window: "readonly",
                document: "readonly",
                console: "readonly",
                Event: "readonly",
                MutationObserver: "readonly",
                getComputedStyle: "readonly",
                requestAnimationFrame: "readonly",
                cancelAnimationFrame: "readonly",
                engine: "readonly",
                viewEnv: "readonly",
                setTimeout: "readonly",
                clearTimeout: "readonly",
                setInterval: "readonly",
                clearInterval: "readonly"
            }
        },
        rules: {
            "no-undef": "error",
            "no-unused-vars": ["error", { args: "none", caughtErrors: "none" }],
            "no-redeclare": "error",
            semi: ["error", "always"]
        }
    },
    {
        files: ["prototypes/tactical_minimap/renderer.js",
            "mod/res/gui/gameface/mods/Driftkings/CarouselStats/carousel_layout.js",
            "mod/res/gui/gameface/mods/Driftkings/CarouselStats/carousel_native.js"],
        languageOptions: { globals: { module: "readonly" } }
    }
];
