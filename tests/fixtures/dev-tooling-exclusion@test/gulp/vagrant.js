// Gulp tasks for managing the Vagrant development VM
// This file is dev tooling — never shipped in an EGO package.
const gulp = require('gulp');
const { exec } = require('child_process');

gulp.task('vm-up', (done) => {
    exec('sudo vagrant up', (err, stdout) => {
        done(err);
    });
});

gulp.task('vm-gsettings', (done) => {
    exec('gsettings set org.gnome.shell disable-user-extensions false', done);
});
