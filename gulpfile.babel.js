'use strict';

import gulp from 'gulp'
import babel from 'gulp-babel'
import sass from 'gulp-sass'
import sourcemaps from 'gulp-sourcemaps'
import plumber from 'gulp-plumber'

gulp.task('babel', () => {
    return gulp.src('functree/static/src/js/*.js')
        .pipe(sourcemaps.init())
        .pipe(plumber())
        .pipe(babel())
        .pipe(sourcemaps.write('./'))
        .pipe(gulp.dest('functree/static/dist/js'));
});

gulp.task('babel:watch', () => {
    return gulp.watch('functree/static/src/js/*.js', ['babel']);
});

gulp.task('sass', () => {
    return gulp.src('functree/static/src/scss/*.scss')
        .pipe(sourcemaps.init())
        .pipe(sass({'outputStyle': 'compressed'}).on('error', sass.logError))
        .pipe(sourcemaps.write('./'))
        .pipe(gulp.dest('functree/static/dist/css'));
});

gulp.task('sass:watch', function () {
    return gulp.watch('functree/static/src/scss/*.scss', ['sass']);
});

gulp.task('build', ['babel', 'sass']);

gulp.task('default', ['build']);
