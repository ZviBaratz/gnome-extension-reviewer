// This file is a dev-tooling trigger — it is not GJS extension code.
// gulp/ and conf/ companion dirs are excluded by PR #275; this file itself
// should also be excluded from pattern checks (R-WEB-09 etc.).
const gulp = require('gulp');
const sass = require('gulp-sass');
const exec = require('child_process').exec;
