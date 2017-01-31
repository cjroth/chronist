const fs = require('fs')
const path = require('path')
const CSV = require('big-csv')
const username = require('username').sync()
const moment = require('moment')

const getSentimentScores = require('./get-sentiment-scores')

exports.builder = {
    input: {
        alias: 'i',
        required: 'Please specify the path to the directory with 750 Words entries'
    },
    output: {
        alias: 'o',
        default: `/Users/${username}/Desktop/chronist-750words-${username}.csv`
    }
}

exports.handler = argv => {

    const inputDirectoryPath = path.resolve(argv.input)
    const outputFilePath = path.resolve(argv.output)

    const csv = new CSV(outputFilePath, { flags: 'w+' })

    fs.readDirSync(inputDirectoryPath)
        .filter(item => /.txt$/.test(item))
        .map(filePath => {
            return fs.readFileSync(inputFilePath, filePath).toString()
        })
        .reduce((prev, curr) => {
            return prev + curr
        })
        .split('------ ENTRY ------')
        .map(entry => {
            return entry
                .split('\n')
                .filter(line => line.length)
        })
        .filter(entry => entry.length)
        .map(entry => {
            let scores = getSentimentScores(entry[3])
            scores.words = parseInt(entry[1].split(':')[1].trim())
            scores.minutes = parseInt(entry[2].split(':')[1].trim())
            scores.date = entry[0].split(':')[1].trim()
            csv.write(scores)
            return scores
        })
        
        console.log(`Saved results to ${argv.output}`)

}
