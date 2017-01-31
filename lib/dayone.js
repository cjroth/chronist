const fs = require('fs')
const path = require('path')
const moment = require('moment')
const username = require('username').sync()
const CSV = require('big-csv')

const getSentimentScores = require('./get-sentiment-scores')

exports.builder = {
    input: {
        alias: 'i',
        required: 'Please specify the path to your JSON input file'
    },
    output: {
        alias: 'o',
        default: `/Users/${username}/Desktop/chronist-dayone-${username}}.csv`
    }
}

exports.handler = argv => {

    const inputFilePath = path.resolve(argv.input)
    const outputFilePath = path.resolve(argv.output)
    const csv = new CSV(outputFilePath, { flags: 'w+' })

    JSON.parse(fs.readFileSync(inputFilePath)).entries.map((entry) => {
        let scores = getSentimentScores(entry.text)
        let date = moment(entry.creationDate)
        scores.date = date.format('YYYY-MM-DD')
        scores.time = date.format('HH:mm:ss')
        csv.write(scores)
        return scores
    })

    console.log(`Saved results to ${argv.output}`)

}
