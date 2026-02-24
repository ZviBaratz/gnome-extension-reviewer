import gnome from 'eslint-config-gnome';

export default [
    {
        ignores: ['node_modules/**', 'schemas/**'],
    },
    ...gnome.configs.recommended,
    {
        files: ['**/*.js'],
        languageOptions: {
            sourceType: 'module',
            globals: {
                global: 'readonly',
            },
        },
    },
];
