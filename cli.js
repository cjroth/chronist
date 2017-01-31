#!/usr/bin/env node

const argv = require('yargs')
    .command('photos', 'Output emotion, expression, age, and ethnic data to CSV', require('./lib/photos').photos)
    .command('lifeslice', 'Same as "photos" but use the default Lifeslice photo directory', require('./lib/photos').lifeslice)
    .command('imessage', 'Output sentiment analysis of iMessages for current user to CSV', require('./lib/imessage'))
    .command('facebook', 'Output sentiment analysis of Facebook messages to CSV', require('./lib/facebook'))
    .command('dayone', 'Output sentiment analysis of Day One entries to CSV', require('./lib/dayone'))
    .command('750words', 'Output sentiment analysis of 750 entries to CSV', require('./lib/750words'))
    .help()
    .showHelp()
    .argv
